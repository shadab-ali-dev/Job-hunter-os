try:
    from sync_export import refresh_export; refresh_export(quiet=True)
except Exception:
    pass
import requests
import os
import json
import re

HIRING_PREFIXES = {
    "careers", "career", "hr", "jobs", "job", "hiring", "talent",
    "recruitment", "recruiting", "recruiter", "apply", "internships", "people"
}
GENERAL_DEPT_PREFIXES = {
    "info", "admin", "support", "hello", "contact", "team", "office", "desk", "enquiry", "inquiry"
}
FREE_DOMAINS = {
    "gmail.com", "yahoo.com", "yahoo.co.in", "outlook.com",
    "hotmail.com", "icloud.com", "proton.me", "protonmail.com"
}
_CACHE_PATH = os.path.expanduser("~/job-hunter/mailer/recipient_cache.json")

def _load_recipient_cache():
    try:
        if os.path.exists(_CACHE_PATH):
            with open(_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_recipient_cache(cache):
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass

def _classify_with_groq(email: str, company: str = "") -> dict:
    cache = _load_recipient_cache()
    key = f"{email.lower()}|{company.lower()}"
    if key in cache:
        return cache[key]

    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        for ep in (os.path.expanduser("~/job-hunter/.env"), os.path.expanduser("~/.env"), os.path.expanduser("~/.bashrc")):
            if os.path.exists(ep):
                with open(ep, encoding="utf-8", errors="ignore") as _epf:
                    for line in _epf:
                        m_k = re.search(r'GROQ_API_KEY\s*=\s*["\']?([^"\'\s]+)', line)
                        if m_k:
                            api_key = m_k.group(1).strip()
                            os.environ["GROQ_API_KEY"] = api_key
                            break
            if api_key:
                break
    if not api_key:
        return {"type": "unknown", "first_name": ""}

    prompt = (
        f"Classify this email recipient for a job application.\n"
        f"Email: {email}\nCompany context: {company or 'None'}\n"
        f"Determine if the email belongs to:\n"
        f"1. 'person': an individual human (extract their capitalized First Name even if concatenated like zeeshanqadir568 -> Zeeshan, himanshujangir16 -> Himanshu, subhajitdas -> Subhajit; leave first_name empty if it is a nickname/handle with no real human name).\n"
        f"2. 'company': a company recruiting/HR inbox or brand alias.\n"
        f"3. 'other': a generic department/support/noreply inbox.\n"
        f"Reply ONLY with valid JSON: {{\"type\": \"person|company|other\", \"first_name\": \"\"}}"
    )
    try:
        hdrs = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        model_id = globals().get("_GROQ_ACTIVE_MODEL")
        if not model_id:
            mr = requests.get("https://api.groq.com/openai/v1/models", headers=hdrs, timeout=6)
            mr.raise_for_status()
            mids = [m["id"] for m in mr.json().get("data", []) if not any(x in m["id"].lower() for x in ("whisper", "guard", "tts", "embed"))]
            for pref in ("llama-3.3", "llama-3", "llama", "qwen", "gemma", "mixtral"):
                hit = next((x for x in mids if pref in x.lower()), None)
                if hit:
                    model_id = hit
                    break
            model_id = model_id or (mids[0] if mids else "llama-3.3-70b-versatile")
            globals()["_GROQ_ACTIVE_MODEL"] = model_id

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=hdrs,
            json={
                "model": model_id,
                "temperature": 0,
                "max_tokens": 40,
                "response_format": {"type": "json_object"},
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=8,
        )
        r.raise_for_status()
        res = json.loads(r.json()["choices"][0]["message"]["content"])
        out = {
            "type": res.get("type", "unknown"),
            "first_name": (res.get("first_name") or "").strip().split()[0].title() if (res.get("first_name") or "").strip() else ""
        }
        cache[key] = out
        _save_recipient_cache(cache)
        return out
    except Exception as _e:
        print(f"[!] Groq classify warning for {email}: {_e}")
        return {"type": "unknown", "first_name": ""}

def smart_greeting_and_closing(email: str, company: str = "", first_name: str = ""):
    local, _, _ = (email or "").strip().lower().partition("@")
    if local in GENERAL_DEPT_PREFIXES:
        c = "I've attached my resume for your review—please let me know if you could route this to the appropriate hiring team."
    else:
        c = "I've attached my resume for your review and would welcome the opportunity to discuss how my background aligns with this role."
    return "Dear Recruiter,", c

from mailer.lead_guard import valid_email, is_seeker_post, clean_company
from mailer.ai_personalizer import evaluate_and_hook
from mailer.bounce_shield import is_deliverable
import csv, random, smtplib, sys, time
from datetime import datetime
from email.message import EmailMessage

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_CSV = os.path.join(BASE, "data", "jobs_queue.csv")
SENT_CSV = os.path.join(BASE, "data", "sent_log.csv")
RESUME_DIR = os.path.join(BASE, "resume")

def pick_resume_and_pitch(role):
    r = role.lower()
    if re.search(r"\b(ai|artificial intelligence|llm|llms|genai|gen ai|agent|agents|agentic|automation|machine learning|ml|nlp|rag)\b", r):
        return "Shadab_Ali_AI_Automation_Engineer_Resume.pdf", "LLM-powered workflow automation, multi-agent Python pipelines, API orchestration, and production SQL/cloud systems"
    if any(k in r for k in ("oracle", "dba", "database")):
        return "Shadab_Ali_Oracle_DBA_Resume.pdf", "Oracle database administration, RMAN backup/recovery, archivelog management, and SQL performance troubleshooting"
    if any(k in r for k in ("frontend", "front-end", "ui", "ux", "react", "web")):
        return "Shadab_Ali_Frontend_UIUX_Resume.pdf", "responsive frontend engineering, clean UI/UX architecture, and modern web application development"
    if any(k in r for k in ("data analyst", "analytics", "bi ", "reporting")):
        return "Shadab_Ali_Data_Analyst_Resume.pdf", "SQL data analysis, reporting pipelines, and Python-driven data automation"
    return "Shadab_Ali_Python_Developer_Resume.pdf", "Python backend automation, SQL troubleshooting, and AWS cloud infrastructure"
def load_env():
    env = {}
    with open(os.path.join(BASE, ".env"), encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k.strip()] = v.strip()
    return env

def build_msg(sender_name, sender_email, job):
    pdf_name, specialty = pick_resume_and_pitch(job["role"])
    msg = EmailMessage()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = job["email"]
    j = job
    clean_role = (job.get("role") or job.get("title") or "Software Engineer").strip()
    msg["Subject"] = f"Application for {clean_role} - {sender_name}"
    _raw_co = re.sub(r"\s*\(.*?\)", "", (job.get("company") or "")).strip()
    _co = "" if (not _raw_co or len(_raw_co) > 35 or _raw_co.lower().startswith(("location:","remote:","apply","posted","salary","http","unknown","stack:","skills:","tech:","experience:","role:")) or ":" in _raw_co or _raw_co.count(",") >= 2) else _raw_co
    _greet, _close = smart_greeting_and_closing(job.get("email", ""), _co, job.get("name") or job.get("contact") or job.get("recruiter") or "")
    _open = f"I'm reaching out regarding the {clean_role} opening at {_co}." if _co else f"I'm reaching out regarding the {clean_role} opening."
    _hook = (j.get("_hook", "").strip() + " ") if j.get("_hook") else ""
    if "Frontend" in pdf_name:
        _exp = "I have 2.4 years of software and IT operations experience alongside hands-on web development with HTML, CSS, Bootstrap, Django, and AWS cloud fundamentals—backed by an AWS Certified Cloud Practitioner credential and a Bachelor's degree."
    elif "AI_Automation" in pdf_name:
        _exp = "Over the past 2.4 years, I’ve built production Python and LLM-driven automation pipelines—integrating Groq/OpenAI APIs, Whisper STT, DNS/IMAP verification, and SQL workflows to eliminate manual bottlenecks—backed by an AWS Certified Cloud Practitioner credential and a Bachelor’s degree."
    elif "Data_Analyst" in pdf_name:
        _exp = "Over the last 2.4 years, I've worked with SQL data extraction, validation, and Python (Pandas) workflows to clean datasets, automate recurring reports, and resolve data discrepancies—backed by an AWS Certified Cloud Practitioner credential and a Bachelor's degree."
    elif "Python_Developer" in pdf_name:
        _exp = "Over the past 2.4 years, I've worked hands-on building Python automation scripts, troubleshooting production application issues, and writing SQL queries to keep backend workflows reliable—backed by an AWS Certified Cloud Practitioner credential and a Bachelor's degree."
    else:
        _exp = "Over the past 2.4 years, I've supported production Oracle databases, health checks, and SLA-bound incident escalations alongside application teams—backed by an AWS Certified Cloud Practitioner credential and a Bachelor's degree."
    body = f"{_greet}\n\n{_open} {_hook}\n\n{_exp}\n\n{_close}\n\nBest regards,\n{sender_name}\n{sender_email}\ngithub.com/shadab-ali-dev | linkedin.com/in/shadab-ali-a25477223"
    msg.set_content(body)
    with open(os.path.join(RESUME_DIR, pdf_name), "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=pdf_name)
    return msg, pdf_name

def get_daily_quota():
    if "--limit" in sys.argv:
        return int(sys.argv[sys.argv.index("--limit") + 1])
    if not os.path.exists(SENT_CSV):
        return 2
    with open(SENT_CSV, encoding="utf-8") as _sf1:
        sent_days = len({r["date"][:10] for r in csv.DictReader(_sf1)})
    return 2 if sent_days < 4 else (5 if sent_days < 10 else (8 if sent_days < 17 else 10))

def run():
    dry = "--dry-run" in sys.argv
    env = load_env()
    quota = get_daily_quota()
    with open(QUEUE_CSV, encoding="utf-8") as _qf_in:
        _reader = csv.DictReader(_qf_in)
        queue_fields = list(_reader.fieldnames or ["lane", "company", "role", "email", "apply_url", "source"])
        rows = list(_reader)
    today_str = datetime.now().strftime("%Y-%m-%d")
    counts = {"remote": 0, "luxembourg": 0, "kolkata": 0, "uae": 0}
    if os.path.exists(SENT_CSV):
        with open(SENT_CSV, encoding="utf-8") as _sf2:
            sent_rows = list(csv.DictReader(_sf2))
        already_sent = {r["email"].lower() for r in sent_rows}
        for r in sent_rows:
            if (r.get("date") or "").startswith(today_str) and r.get("lane") in counts:
                counts[r["lane"]] += 1
    else:
        already_sent = set()
    picked, remaining = [], []

    for r in rows:
        lane = r["lane"]
        r["company"]=clean_company(r.get("company",""))
        if r["company"] and r["email"] and not is_seeker_post(r["company"],r.get("role","")) and valid_email(r["email"],True) and r["email"].lower() not in already_sent and lane in counts and counts[lane] < quota:
            pdf_tmp, spec = pick_resume_and_pitch(r["role"])
            fit_ok, hook = evaluate_and_hook(r["company"], r["role"], spec, r["email"])
            if not fit_ok:
                print(f"[FILTERED] Low fit: {r['role']} @ {r['company']}")
                continue
            r["_hook"] = hook
            picked.append(r)
            counts[lane] += 1
            already_sent.add(r["email"].lower())
        elif r["company"] and not is_seeker_post(r["company"], r.get("role", "")) and (r.get("email") or "").lower() not in already_sent:
            remaining.append(r)

    print(f"[Mailer] Mode={'DRY-RUN' if dry else 'LIVE'} | Quota/lane={quota} | Selected={len(picked)}")
    if dry:
        for j in picked:
            pdf, _ = pick_resume_and_pitch(j["role"])
            print(f"  -> [{j['lane']}] {j['company']} | {j['email']} | {pdf}")
        return

    def _connect_smtp():
        s = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
        s.login(env["GMAIL_USER"], env["GMAIL_APP_PASS"])
        return s

    unsent_picked = list(picked)
    smtp = _connect_smtp()
    try:
        new_file = not os.path.exists(SENT_CSV)
        with open(SENT_CSV, "a", newline="", encoding="utf-8") as sf:
            sw = csv.DictWriter(sf, fieldnames=["date", "lane", "company", "role", "email", "resume"])
            if new_file:
                sw.writeheader()
            for i, j in enumerate(picked):
                ok, reason = is_deliverable(j["email"])
                if not ok:
                    print(f"[SKIP] Invalid email {j['email']} ({reason})")
                    unsent_picked.remove(j)
                    continue
                try:
                    msg, pdf = build_msg(env["SENDER_NAME"], env["GMAIL_USER"], j)
                    try:
                        smtp.noop()
                    except Exception:
                        try:
                            smtp.quit()
                        except Exception:
                            pass
                        smtp = _connect_smtp()
                    smtp.send_message(msg)
                    sw.writerow({"date": datetime.now().isoformat(timespec="seconds"), "lane": j["lane"], "company": j["company"], "role": j["role"], "email": j["email"], "resume": pdf})
                    sf.flush()
                    unsent_picked.remove(j)
                    print(f"[{i+1}/{len(picked)}] Sent to {j['company']} ({j['email']}) [{pdf}]")
                except Exception as _send_err:
                    print(f"[ERROR] Failed sending to {j['email']}: {_send_err}")
                if i < len(picked) - 1:
                    time.sleep(random.randint(60, 140))
    finally:
        try:
            smtp.quit()
        except Exception:
            pass
        clean_rows = [{k: v for k, v in row.items() if not k.startswith("_")} for row in (unsent_picked + remaining)]
        with open(QUEUE_CSV, "w", newline="", encoding="utf-8") as qf:
            qw = csv.DictWriter(qf, fieldnames=queue_fields, extrasaction="ignore")
            qw.writeheader()
            qw.writerows(clean_rows)

if __name__ == "__main__":
    run()
