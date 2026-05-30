#!/usr/bin/env python3
"""bridge_manager.py - Persistent manager for Social News Bridge

This script launches ``bridge.py`` in a subprocess and automatically
restarts it if the process crashes or exits unexpectedly.  It prints
status messages to the console and can be stopped cleanly with
Ctrl+C (SIGINT).

Usage::
    $ chmod +x bridge_manager.py
    $ ./bridge_manager.py

The manager will:
  * Load the environment from ``.env`` (the bridge does this itself).
  * Start ``bridge.py``.
  * If ``bridge.py`` exits with a non‑zero code, wait a short back‑off and
    restart it.
  * On Ctrl+C, terminate the child process and exit gracefully.
"""

import subprocess
import sys
import time
import signal
import os

# Path to the bridge script (relative to this manager)
BRIDGE_SCRIPT = os.path.join(os.path.dirname(__file__), "bridge.py")

# Path to the virtual‑environment python interpreter
VENV_PYTHON = os.path.join(os.path.dirname(__file__), "venv", "bin", "python")

# Fallback if venv python doesn't exist
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

# Back‑off parameters (seconds) – increase after repeated failures
INITIAL_BACKOFF = 2
MAX_BACKOFF = 30
backoff = INITIAL_BACKOFF

# Flag to indicate whether we should keep looping
keep_running = True


def handle_sigint(signum, frame):
    global keep_running
    print("\n⚡ Received interrupt – shutting down bridge manager…")
    keep_running = False
    # The current child process will be terminated below

# Register SIGINT (Ctrl+C) handler
signal.signal(signal.SIGINT, handle_sigint)

def start_bridge():
    """Start the bridge subprocess using the venv python interpreter.

    Returns the ``subprocess.Popen`` instance.
    """
    env = os.environ.copy()
    # Ensure the virtual‑env bin directory is at the front of PATH
    venv_bin = os.path.join(os.path.dirname(__file__), "venv", "bin")
    if os.path.isdir(venv_bin):
        env["PATH"] = f"{venv_bin}:{env.get('PATH','')}"
    
    # Use the python from the venv to run bridge.py
    return subprocess.Popen([VENV_PYTHON, BRIDGE_SCRIPT], env=env)

print("============================================================")
print("  Telegram to Meta Real-Time News Bridge - Local Manager")
print("============================================================")
print("This script will keep the bridge running persistently in the background.")
print("If the bridge crashes or loses connection, it will automatically restart.")
print("Press Ctrl+C to stop.")
print("------------------------------------------------------------")

while keep_running:
    print("[{}] Starting Real-time Bridge...".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    proc = start_bridge()
    try:
        # Wait for the bridge process to finish
        proc.wait()
    except KeyboardInterrupt:
        # This block is rarely hit because SIGINT is handled globally
        pass
    exit_code = proc.returncode
    
    if not keep_running:
        # Manager was asked to stop – break the loop
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        break
        
    if exit_code == 0:
        # Normal exit (unlikely for a continuously running bridge)
        print("✅ Bridge exited normally. Restarting after short delay…")
    else:
        print(f"⚠️ Bridge terminated with exit code {exit_code}. Restarting…")
        
    # Simple exponential back‑off to avoid rapid restart loops
    time.sleep(backoff)
    backoff = min(backoff * 2, MAX_BACKOFF)

print("🚪 Manager stopped. Goodbye!")
sys.exit(0)
