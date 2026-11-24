import json, os, re, urllib.request
_BFILE = os.path.expanduser('~/job-hunter/data/bounced_emails.json')

BAD_PREFIXES = ("noreply@", "no-reply@", "donotreply@", "do-not-reply@", "mailer-daemon@", "postmaster@", "unsubscribe@")
BAD_DOMAINS = {"example.com", "example.org", "test.com", "localhost", "sentry.io", "wixpress.com"}
BAD_EMAILS = {"career@webskitters.com"}
_MX_CACHE = {}

def is_deliverable(email: str) -> tuple[bool, str]:
    e = (email or "").strip().lower()
    if not re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", e):
        return False, "invalid_syntax"
    bounced = set()
    if os.path.exists(_BFILE):
        with open(_BFILE, encoding='utf-8') as _bf:
            bounced = set(json.load(_bf))
    if e in BAD_EMAILS or e in bounced or e.startswith(BAD_PREFIXES):
        return False, "trap_prefix"
    domain = e.split("@", 1)[1]
    if domain in BAD_DOMAINS:
        return False, "blocked_domain"
    if domain in _MX_CACHE:
        ok = _MX_CACHE[domain]
        return ok, ("ok" if ok else "no_mx_record")
    try:
        req = urllib.request.Request(
            f"https://1.1.1.1/dns-query?name={domain}&type=MX",
            headers={"Accept": "application/dns-json", "User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        ok = data.get("Status") == 0 and any(a.get("type") == 15 for a in data.get("Answer", []))
    except Exception:
        ok = True
    _MX_CACHE[domain] = ok
    return ok, ("ok" if ok else "no_mx_record")

if __name__ == "__main__":
    for test in ["careers@google.com", "noreply@stripe.com", "fake@nonexistentdomain99999.com"]:
        print(test, "->", is_deliverable(test))
