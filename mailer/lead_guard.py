import re, socket, functools
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
BAD_PFX = ("noreply","no-reply","donotreply","do-not-reply","mailer-daemon","postmaster","webmaster","abuse","spam","privacy","legal","billing","unsubscribe","bounce","notification","alert","support","helpdesk","info")
BAD_DOM = {"example.com","example.org","example.net","test.com","domain.com","email.com","sentry.io","wixpress.com","gmail.con","gamil.com","yahoo.con","passinbox.com","simplelogin.com","simplelogin.co","anonaddy.me","duck.com"}
SEEKER_RE = re.compile(r"\b(seeking\s+work|seeking\s+freelancer|for\s+hire|open\s+to\s+work|looking\s+for\s+a\s+job|available\s+for\s+hire)\b", re.I)
FAKE_CO_RE = re.compile(r"^(location|remote|willing\s+to|stack|skills|tech|experience|role|salary|apply|posted|http|www|unknown|confidential|n/?a|none|tbd|early[- ]stage\s+startup|kolkata\s+it\s+employer|stealth|hiring|looking\s+for|we\s+are|join\s+us|freelance|self[- ]employed)\b", re.I)

@functools.lru_cache(maxsize=512)
def domain_live(dom):
    dom = dom.lower().strip(".")
    if not dom or dom in BAD_DOM: return False
    socket.setdefaulttimeout(1.5)
    try:
        socket.getaddrinfo(dom, 25)
        return True
    except Exception:
        return False

FREE_PERSONAL_DOMAINS = {"gmail.com", "yahoo.com", "yahoo.co.in", "hotmail.com", "outlook.com", "rediffmail.com", "icloud.com", "proton.me", "protonmail.com"}
RECRUITER_HINTS = {"hr", "career", "careers", "job", "jobs", "hiring", "recruit", "recruitment", "recruiter", "talent", "apply"}

def is_recruiter_email(email):
    e = (email or "").strip().lower()
    if "@" not in e: return False
    loc, dom = e.rsplit("@", 1)
    tokens = {re.sub(r"\d+", "", t) for t in re.split(r"[._+-]+", loc) if t}
    if dom in FREE_PERSONAL_DOMAINS:
        return bool(tokens & RECRUITER_HINTS)
    return True

def valid_email(email, check_mx=True):
    e = (email or "").strip().lower()
    if not EMAIL_RE.match(e) or len(e) > 90: return False
    loc, dom = e.rsplit("@", 1)
    if any(loc == p or loc.startswith(p + "+") or loc.startswith(p + ".") for p in BAD_PFX): return False
    if dom in BAD_DOM or dom.endswith((".png",".jpg",".jpeg",".gif",".css",".js",".svg")): return False
    if not is_recruiter_email(e): return False
    return domain_live(dom) if check_mx else True

def is_seeker_post(co, role):
    return bool(SEEKER_RE.search(f"{co or ''} {role or ''}"))

def clean_company(raw):
    s = (raw or "").replace("\r"," ").replace("\n"," ").strip()
    s = re.sub(r"\s*\(.*?\)", "", s)
    s = re.sub(r"\s*[|•—–].*$", "", s)
    s = re.sub(r"\s+", " ", s).strip(" -:,.")
    if not s or len(s) < 2 or len(s) > 40 or ":" in s or "@" in s or "http" in s.lower() or s.count(",") >= 2: return ""
    if FAKE_CO_RE.match(s) or re.search(r"\b(utc[+-]?\d|remote:\s*yes|willing\s+to\s+relocate)\b", s, re.I): return ""
    return s
