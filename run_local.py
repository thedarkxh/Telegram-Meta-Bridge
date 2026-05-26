import time
import subprocess
import sys

print("Local Bridge Scheduler started. Running bridge.py every 30 minutes...")
print("Press Ctrl+C to stop.")

try:
    while True:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Triggering bridge...")
        
        # Use virtual environment's isolated python if it exists, fallback to sys.executable
        import os
        python_bin = './venv/bin/python' if os.path.exists('./venv/bin/python') else sys.executable
        result = subprocess.run([python_bin, 'bridge.py'])
        if result.returncode == 0:
            print("Bridge run completed successfully.")
        else:
            print(f"Bridge run failed with exit code {result.returncode}.")
            
        print("Sleeping for 30 minutes...")
        time.sleep(1800) # 1800 seconds = 30 minutes
except KeyboardInterrupt:
    print("\nScheduler stopped.")
