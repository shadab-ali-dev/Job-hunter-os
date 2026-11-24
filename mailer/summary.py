import csv, os
from collections import Counter
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENT_CSV = os.path.join(BASE, "data", "sent_log.csv")
QUEUE_CSV = os.path.join(BASE, "data", "jobs_queue.csv")

today = datetime.now().strftime("%Y-%m-%d")
if os.path.exists(SENT_CSV):
    with open(SENT_CSV, encoding="utf-8") as _f1:
        sent = list(csv.DictReader(_f1))
else:
    sent = []
if os.path.exists(QUEUE_CSV):
    with open(QUEUE_CSV, encoding="utf-8") as _f2:
        queue = list(csv.DictReader(_f2))
else:
    queue = []

today_rows = [r for r in sent if r["date"].startswith(today)]
days = len({r["date"][:10] for r in sent})
by_lane = Counter(r["lane"] for r in sent)
q_lane = Counter(r["lane"] for r in queue)

print("\n================ JOB HUNTER SUMMARY ================")
print(f"Sent Today ({today}) : {len(today_rows)} emails")
print(f"Total Sent Overall     : {len(sent)} emails (across {days} active day{'s' if days != 1 else ''})")
print(f"By Lane (Sent)         : Remote={by_lane['remote']} | Luxembourg={by_lane['luxembourg']} | Kolkata={by_lane['kolkata']} | UAE={by_lane['uae']}")
print(f"Remaining in Queue     : {len(queue)} (Remote={q_lane['remote']} | Luxembourg={q_lane['luxembourg']} | Kolkata={q_lane['kolkata']} | UAE={q_lane['uae']})")
print("====================================================\n")
