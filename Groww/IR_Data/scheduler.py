#!/usr/bin/env python3
"""
Local scheduler for Groww IR Data fetch
Runs the fetch script every 5 minutes locally
"""

import schedule
import time
import subprocess
import os
from datetime import datetime

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'fetch_groww_ir_data_with_sheets.py')

def run_fetch():
    """Execute the fetch script"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{timestamp}] Running Groww IR Data fetch...")
    
    try:
        result = subprocess.run(
            ['python', SCRIPT_PATH],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"[{timestamp}] ✅ Fetch completed successfully")
        else:
            print(f"[{timestamp}] ❌ Fetch failed: {result.stderr}")
    except Exception as e:
        print(f"[{timestamp}] ❌ Error: {e}")

def main():
    """Main scheduler loop"""
    print("=" * 60)
    print("Groww IR Data - Local Scheduler")
    print("=" * 60)
    print(f"Schedule: Every 5 minutes")
    print(f"Script: {SCRIPT_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Schedule the job
    schedule.every(5).minutes.do(run_fetch)
    
    # Run initial fetch
    run_fetch()
    
    # Keep scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(10)  # Check every 10 seconds
    except KeyboardInterrupt:
        print("\n⏹️  Scheduler stopped")

if __name__ == '__main__':
    try:
        import schedule
    except ImportError:
        print("❌ 'schedule' package not found. Installing...")
        subprocess.run(['pip', 'install', 'schedule'], check=True)
        import schedule
    
    main()
