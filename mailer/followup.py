import csv, imaplib, json, os, smtplib, sys, time
from datetime import datetime
from email.message import EmailMessage
from mailer.bounce_shield import is_deliverable
from mailer.send_daily import smart_greeting_and_closing

BASE = os.path.expanduser("~/job-hunter")
ENV_PATH = os.path.join(BASE, ".env")
SENT_CSV = os.path.join(BASE, "data", "sent_log.csv")
FOLLOWUP_JSON = os.path.join(BASE, "data", "followup_sent.json")
FOLLOWUP_DAILY_JSON = os.path.join(BASE, "data", "followup_daily.json")

def load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as _ef:
            for line in _ef:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env[k] = v.strip().strip('"').strip("'")
    return env

def get_replied_senders(user: str, app_pass: str) -> set[str]:
    replied = set()
    try:
        M = imaplib.IMAP4_SSL("imap.gmail.com")
        M.login(user, app_pass)
        M.select("INBOX")
        _, data = M.search(None, "ALL")
        ids = (data[0].split() or [])[-200:]
        for num in ids:
            _, msg_data = M.fetch(num, "(BODY.PEEK[HEADER.FIELDS (FROM)])")
            raw = (msg_data[0][1] or b"").decode("utf-8", errors="ignore").lower()
            if "@" in raw:
                for token in raw.replace("<", " ").replace(">", " ").split():
                    if "@" in token:
                        replied.add(token.strip(".,:;\"'"))
        M.logout()
    except Exception:
        pass
    return replied

def run_followups(max_bumps: int = 3):
    dry = "--dry-run" in sys.argv
    if not os.path.exists(SENT_CSV):
        return
    env = load_env()
    user, app_pass = env.get("GMAIL_USER", ""), env.get("GMAIL_APP_PASS", "")
    if not user or not app_pass:
        return

    if os.path.exists(FOLLOWUP_JSON):
        with open(FOLLOWUP_JSON, encoding="utf-8") as _fj:
            bumped = set(json.load(_fj))
    else:
        bumped = set()
    replied = get_replied_senders(user, app_pass)
    now = datetime.now()
    candidates = []

    with open(SENT_CSV, encoding="utf-8") as _sf:
        sent_rows = list(csv.DictReader(_sf))
    for r in sent_rows:
        email = (r.get("email") or "").strip().lower()
        if not email or email in bumped or email in replied:
            continue
        try:
            sent_dt = datetime.strptime((r.get("date") or "")[:10], "%Y-%m-%d")
        except Exception:
            continue
        age = (now - sent_dt).days
        if 5 <= age <= 12:
            candidates.append(r)

    today_k = now.strftime("%Y-%m-%d")
    daily_log = {}
    if os.path.exists(FOLLOWUP_DAILY_JSON):
        with open(FOLLOWUP_DAILY_JSON, encoding="utf-8") as _df: daily_log = json.load(_df)
    rem_bumps = max(0, max_bumps - int(daily_log.get(today_k, 0)))
    candidates = candidates[:rem_bumps]
    print(f"[Follow-Up] Eligible 5-12d bumps={len(candidates)} (dry={dry})")
    if dry or not candidates:
        for c in candidates:
            print(f"  -> Would bump: {c.get('company')} ({c.get('email')}) | {c.get('role')}")
        return

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, app_pass)
        for c in candidates:
            email = c["email"].strip().lower()
            ok, _ = is_deliverable(email)
            if not ok:
                bumped.add(email)
                continue
            role = (c.get("role") or "Software Engineer").strip()
            raw_c = (c.get("company") or "").strip()
            clean_c = "" if (not raw_c or len(raw_c) > 40 or raw_c.lower().startswith(("location:", "remote:", "apply", "posted", "salary", "http", "unknown"))) else raw_c
            greet = "Dear Recruiter,"
            where_txt = f"at {clean_c}" if clean_c else "on your team"
            msg = EmailMessage()
            msg["From"] = f"Shadab Ali <{user}>"
            msg["To"] = email
            msg["Subject"] = f"Re: Application for {role} - Shadab Ali"
            msg.set_content(
                f"{greet}\n\n"
                f"Following up briefly on my application from last week for the {role} role {where_txt}. "
                f"With 2.4 years of hands-on experience across Python, SQL/Oracle, data analysis, and AWS, "
                f"I would welcome the chance to connect if the position is still open.\n\n"
                f"Best regards,\nShadab Ali\ngithub.com/shadab-ali-dev | linkedin.com/in/shadab-ali-a25477223"
            )
            try:
                smtp.send_message(msg)
                bumped.add(email)
                daily_log[today_k] = int(daily_log.get(today_k, 0)) + 1
                with open(FOLLOWUP_DAILY_JSON, "w", encoding="utf-8") as _df2: json.dump(daily_log, _df2, indent=2)
                with open(FOLLOWUP_JSON, "w", encoding="utf-8") as jf:
                    json.dump(sorted(bumped), jf, indent=2)
                print(f"[Follow-Up] Bumped {clean_c or 'team'} ({email})")
            except Exception as se:
                print(f"[Follow-Up][ERR] {email}: {se}")
            time.sleep(8)

    with open(FOLLOWUP_JSON, "w", encoding="utf-8") as f:
        json.dump(sorted(bumped), f, indent=2)

if __name__ == "__main__":
    run_followups()
