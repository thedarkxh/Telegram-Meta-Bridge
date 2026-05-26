import subprocess
import os
import sys
import time

print("=" * 60)
print("  Telegram to Meta Real-Time News Bridge - Local Manager")
print("=" * 60)
print("This script will keep the bridge running persistently in the background.")
print("If the bridge crashes or loses connection, it will automatically restart.")
print("Press Ctrl+C to stop.")
print("-" * 60)

python_bin = './venv/bin/python' if os.path.exists('./venv/bin/python') else sys.executable

try:
    while True:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Real-time Bridge...")
        
        # Run bridge.py persistently
        process = subprocess.run([python_bin, 'bridge.py'])
        
        if process.returncode == 0:
            print("Bridge stopped cleanly.")
            break
        else:
            print(f"\n[Warning] Bridge process exited with code {process.returncode}.")
            print("Restarting bridge in 10 seconds... (Press Ctrl+C to abort)")
            time.sleep(10)
except KeyboardInterrupt:
    print("\nLocal Manager stopped by user.")
