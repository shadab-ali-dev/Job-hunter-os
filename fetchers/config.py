import csv, json, os, re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_CSV = os.path.join(BASE_DIR, "data", "jobs_queue.csv")
SENT_CSV = os.path.join(BASE_DIR, "data", "sent_log.csv")
BOUNCE_JSON = os.path.join(BASE_DIR, "data", "bounced_emails.json")

INCLUDE_KEYWORDS = [
    "python", "sql", "aws", "oracle", "frontend", "front-end",
    "ui/ux", "ui", "ux", "dba", "database", "data analyst",
    "engineer", "backend", "software"
]

EXCLUDE_TITLE = ["senior", "sr.", "staff", "principal", "lead", "director", "manager", "vp", "head of", "intern"]
EXCLUDE_LOC = ["us only", "usa only", "united states only", "north america only", "uk only", "canada only"]
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

def matches_criteria(title, text="", check_location=True):
    t_low, full_low = title.lower(), f"{title} {text}".lower()
    if any(b in t_low for b in EXCLUDE_TITLE):
        return False
    if check_location and any(b in full_low for b in EXCLUDE_LOC):
        return False
    return any(kw in full_low for kw in INCLUDE_KEYWORDS)

def save_jobs(new_rows):
    seen, sent_emails = set(), set()
    if os.path.exists(BOUNCE_JSON):
        with open(BOUNCE_JSON, encoding="utf-8") as bf:
            sent_emails.update(e.lower() for e in json.load(bf))
    for p in (QUEUE_CSV, SENT_CSV):
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                for r in csv.DictReader(f):
                    seen.add(((r.get("company") or "").lower(), (r.get("role") or "").lower()))
                    em = (r.get("email") or "").strip().lower()
                    if em:
                        sent_emails.add(em)
    unique = []
    for i in new_rows:
        co, ro = (i.get("company") or "").strip(), (i.get("role") or "").strip()
        em = (i.get("email") or "").strip().lower()
        if not co or (co.lower(), ro.lower()) in seen or (em and em in sent_emails):
            continue
        seen.add((co.lower(), ro.lower()))
        unique.append(i)
    if not unique:
        return 0
    exists = os.path.exists(QUEUE_CSV)
    with open(QUEUE_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["lane", "company", "role", "email", "apply_url", "source"])
        if not exists:
            w.writeheader()
        w.writerows(unique)
    return len(unique)
