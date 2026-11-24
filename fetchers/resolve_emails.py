import csv, re, socket, requests
from fetchers.config import QUEUE_CSV, EMAIL_REGEX

KNOWN_HR = {
    "alten": "recrutement@alten.lu",
    "capgemini": "recruitment.lu@capgemini.com",
    "soprasteria": "recrutement.lu@soprasteria.com",
    "pwcluxembourg": "lu_recruitment@pwc.com",
    "ey": "recruitment@lu.ey.com",
    "cognizant": "careersindia@cognizant.com",
    "wipro": "helpdesk.recruitment@wipro.com",
    "genpact": "careers@genpact.com"
}

def scrape_page_email(url):
    try:
        html = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}).text
        found = [e for e in EMAIL_REGEX.findall(html) if not e.endswith((".png", ".jpg", ".js", ".css", "sentry.io"))]
        return found[0] if found else ""
    except Exception:
        return ""

def run():
    with open(QUEUE_CSV, "r", encoding="utf-8") as _qf:
        rows = list(csv.DictReader(_qf))
    resolved = 0
    for r in rows:
        if r["email"]:
            continue
        ckey = re.sub(r"[^a-z]", "", r["company"].lower())
        if ckey in KNOWN_HR:
            r["email"] = KNOWN_HR[ckey]
            resolved += 1
        elif r["apply_url"].startswith("http") and "news.google.com" not in r["apply_url"]:
            found = scrape_page_email(r["apply_url"])
            if found:
                r["email"] = found
                resolved += 1

    with open(QUEUE_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["lane", "company", "role", "email", "apply_url", "source"])
        w.writeheader()
        w.writerows(rows)
    print(f"[Resolver] Filled {resolved} recruiter emails.")

if __name__ == "__main__":
    run()
