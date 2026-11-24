import csv, email, imaplib, json, os, re
from email.header import decode_header

BASE = os.path.expanduser("~/job-hunter")
ENV_PATH = os.path.join(BASE, ".env")
SENT_CSV = os.path.join(BASE, "data", "sent_log.csv")
QUEUE_CSV = os.path.join(BASE, "data", "jobs_queue.csv")
BOUNCE_JSON = os.path.join(BASE, "data", "bounced_emails.json")
FREE_DOMS = {"gmail.com", "yahoo.com", "yahoo.co.in", "hotmail.com", "outlook.com", "rediffmail.com", "icloud.com", "proton.me", "protonmail.com"}

def _env():
    d = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    d[k.strip()] = v.strip().strip('"').strip("'")
    return d

def _dec(val):
    if not val: return ""
    out = []
    for part, enc in decode_header(val):
        out.append(part.decode(enc or "utf-8", errors="ignore") if isinstance(part, bytes) else part)
    return "".join(out)

def check_replies():
    env = _env()
    user, pw = env.get("GMAIL_USER", ""), env.get("GMAIL_APP_PASS", "")
    if not user or not pw:
        print("[ReplyWatcher] Missing GMAIL_USER or GMAIL_APP_PASS in .env")
        return
    tracked = set()
    for p in (SENT_CSV, QUEUE_CSV):
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="ignore") as f:
                for r in csv.DictReader(f):
                    e = (r.get("email") or "").strip().lower()
                    if "@" in e and e != user.lower():
                        tracked.add(e)
                        dom = e.split("@", 1)[1]
                        if dom not in FREE_DOMS:
                            tracked.add("@" + dom)

    bset = set()
    if os.path.exists(BOUNCE_JSON):
        with open(BOUNCE_JSON, encoding="utf-8") as bf:
            bset = set(json.load(bf))
    orig_bcount = len(bset)

    M = imaplib.IMAP4_SSL("imap.gmail.com")
    M.login(user, pw)
    M.select("INBOX")
    _, data = M.search(None, "ALL")
    ids = (data[0].split() or [])[-150:]
    hits = []
    for num in reversed(ids):
        _, msg_data = M.fetch(num, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
        msg = email.message_from_bytes(msg_data[0][1] or b"")
        frm = _dec(msg.get("From", ""))
        low = frm.lower()
        if user.lower() in low:
            continue
        if "mailer-daemon" in low or "postmaster" in low:
            _, bdata = M.fetch(num, "(BODY.PEEK[TEXT])")
            body = (bdata[0][1] or b"").decode("utf-8", errors="ignore")
            for em in re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", body):
                if em.lower() in tracked:
                    bset.add(em.lower())
        elif any(t in low for t in tracked) and not any(b in low for b in ("noreply", "no-reply")):
            hits.append((msg.get("Date", "")[:16], frm[:42], _dec(msg.get("Subject", ""))[:50]))
    M.logout()

    if len(bset) > orig_bcount:
        with open(BOUNCE_JSON, "w", encoding="utf-8") as bf:
            json.dump(sorted(bset), bf, indent=2)
        if os.path.exists(QUEUE_CSV):
            with open(QUEUE_CSV, encoding="utf-8") as qf:
                rd = csv.DictReader(qf)
                fns, qrows = rd.fieldnames, [r for r in rd if (r.get("email") or "").strip().lower() not in bset]
            with open(QUEUE_CSV, "w", newline="", encoding="utf-8") as qf:
                w = csv.DictWriter(qf, fieldnames=fns); w.writeheader(); w.writerows(qrows)

    print(f"[ReplyWatcher] Checked {len(ids)} emails -> {len(hits)} reply(s), {len(bset)} blocked bounce(s).")
    for dt, frm, subj in hits[:8]:
        print(f"  -> {dt} | {frm} | {subj}")

if __name__ == "__main__":
    check_replies()
