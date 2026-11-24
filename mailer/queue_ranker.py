import csv, json, os, random
from collections import Counter
from datetime import datetime, timedelta

BASE = os.path.expanduser("~/job-hunter")
QUEUE_CSV = os.path.join(BASE, "data", "jobs_queue.csv")
META_JSON = os.path.join(BASE, "data", "job_meta.json")

def key_for(row):
    return (row.get("apply_url") or f"{row.get('company','')}|{row.get('role','')}").strip().lower()

def refresh_and_rank(is_hunt=False):
    if not os.path.exists(QUEUE_CSV):
        return
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    if os.path.exists(META_JSON):
        with open(META_JSON, encoding="utf-8") as _mf:
            meta = json.load(_mf)
    else:
        meta = {}

    with open(QUEUE_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or ["lane", "company", "role", "email", "apply_url", "source"]
        rows = list(reader)

    company_counts = Counter((r.get("company") or "").strip().lower() for r in rows if (r.get("company") or "").strip())
    kept = []

    for r in rows:
        k = key_for(r)
        info = meta.get(k)
        if not info:
            info = {"first_seen": today_str, "last_seen": today_str, "seen_count": 1}
        elif is_hunt:
            if info.get("last_seen") != today_str:
                info["seen_count"] = info.get("seen_count", 1) + 1
            info["last_seen"] = today_str
        meta[k] = info

        first_dt = datetime.strptime(info["first_seen"], "%Y-%m-%d")
        age_days = (now - first_dt).days
        still_hiring = info.get("seen_count", 1) >= 2 and info.get("last_seen") == today_str

        # Keep jobs <= 30 days old, OR older jobs if re-confirmed active in latest hunt
        if age_days <= 30 or still_hiring:
            comp = (r.get("company") or "").strip().lower()
            freq_score = info.get("seen_count", 1) + (1 if company_counts[comp] >= 2 else 0)
            kept.append((freq_score, info["last_seen"], random.random(), r))

    # Highest recruiting frequency first, then newest last_seen date, light shuffle within same tier/day
    kept.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    ranked_rows = [x[3] for x in kept]

    with open(QUEUE_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(ranked_rows)

    with open(META_JSON, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Queue ranked: {len(ranked_rows)} active jobs (pruned {len(rows) - len(ranked_rows)} stale >30d).")

if __name__ == "__main__":
    import sys
    refresh_and_rank(is_hunt=("--hunt" in sys.argv))
