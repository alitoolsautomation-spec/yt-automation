"""
Runs main.py's pipeline automatically at fixed times each day, producing
2-3 videos daily. Keep this script running (e.g. via nohup, screen/tmux,
or a systemd service) for it to work continuously.

Alternative: instead of running this as a long-lived process, you can
just add these same times to a cron job that calls `python main.py` -
see README.md.
"""
import time
import schedule
from main import run_pipeline

# Adjust these times (24h format, server's local time) to spread videos
# through the day. 3 videos/day example:
UPLOAD_TIMES = ["09:00", "15:00", "20:00"]


def job():
    print(f"Running scheduled upload at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        run_pipeline()
    except Exception as e:
        print(f"Scheduled run failed: {e}")


for t in UPLOAD_TIMES:
    schedule.every().day.at(t).do(job)

print(f"Scheduler started. Uploads scheduled daily at: {UPLOAD_TIMES}")
print("Keep this process running (screen/tmux/nohup) for automation to work.")

while True:
    schedule.run_pending()
    time.sleep(30)
