import json, os, re, urllib.error, urllib.request

NOISE_PATTERNS = (
    "seeking work", "who wants to be hired", "open to work", "available for hire",
    "looking for my next", "no experience required", "no experience needed",
    "registration fee", "training fee", "security deposit", "whatsapp only",
    "telegram only", "earn daily", "weekly payout", "easy typing", "part time data entry",
    "guaranteed job", "100% job guarantee", "pay after placement"
)

BIG_BRANDS = ("infosys", "tcs", "wipro", "cognizant", "accenture", "capgemini", "google", "amazon", "microsoft", "meta", "deloitte", "ibm")
FREE_DOMAINS = ("gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com")

def _get_groq_key() -> str:
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key.startswith("gsk_"):
        return key
    for path in (os.path.expanduser("~/job-hunter/.env"), os.path.expanduser("~/.bashrc")):
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="ignore") as _pf:
                txt = _pf.read()
            m = re.search(r"gsk_[A-Za-z0-9_]+", txt)
            if m:
                return m.group(0)
    return ""

def is_obviously_fake_or_noise(company: str, role: str, email: str = "") -> tuple[bool, str]:
    blob = f"{company} {role}".lower()
    if (company or "").strip().lower().startswith("location:"):
        return True, "scraped_seeker_post"
    for pat in NOISE_PATTERNS:
        if pat in blob:
            return True, f"blocked_phrase:{pat}"
    comp_l = (company or "").lower()
    dom = email.split("@", 1)[1].lower() if "@" in (email or "") else ""
    if dom in FREE_DOMAINS and any(b in comp_l for b in BIG_BRANDS):
        return True, "brand_impersonation_freemail"
    return False, ""

def evaluate_and_hook(company: str, role: str, specialty: str, email: str = "", debug: bool = False) -> tuple[bool, str]:
    bad, reason = is_obviously_fake_or_noise(company, role, email)
    if bad:
        if debug:
            print(f"[RULE-BLOCKED] {reason}")
        return False, ""

    key = _get_groq_key()
    if not key:
        return True, ""

    prompt = (
        f"Candidate: 2.4 years experience in software engineering & IT operations, skilled in Python, SQL/Oracle DB, Frontend/Web, Data Analysis, and AWS Certified Cloud Practitioner.\n"
        f"Job: Role='{role}' at Company='{company}' (contact: {email}). Matched focus: {specialty}.\n"
        f"Rate authenticity & fit from 1-10 for a Software Engineer, Python Developer, Data Analyst, SQL/Oracle DBA, or Frontend Developer with 2.4 years experience.\n"
        f"Give score <=2 if it looks like a fake/scam job post, vague MLM/spam, or a job-seeker 'SEEKING WORK' post rather than an employer hiring. Give score <=4 for pure IT helpdesk/call-center, sales, or 8+ yr director roles.\n"
        f"Reply in EXACTLY two lines:\n"
        f"SCORE: <number 1-10>\n"
        f"HOOK: <one natural, human-sounding sentence, max 24 words, no buzzwords like thrilled/delighted, written in FIRST PERSON (using 'I' or 'My', NEVER 'Your'), directly connecting my {specialty} experience to {company}'s {role} role>"
    )

    payload = json.dumps({
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "reasoning_effort": "low",
        "temperature": 0.3,
        "max_tokens": 600,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = (data["choices"][0]["message"].get("content") or "").strip()
        m_score = re.search(r"SCORE:\s*(\d+)", text, re.I)
        m_hook = re.search(r"HOOK:\s*(.+)", text, re.I)
        score = int(m_score.group(1)) if m_score else 7
        hook = m_hook.group(1).strip().strip('"') if m_hook else ""
        if debug:
            print(f"[openai/gpt-oss-20b] score={score}")
        return (score >= 6), hook
    except Exception as e:
        if debug:
            print("DEBUG:", e)
        return True, ""
