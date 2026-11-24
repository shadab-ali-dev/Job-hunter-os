import html, re, requests
from fetchers.config import EMAIL_REGEX, matches_criteria, save_jobs
from mailer.lead_guard import valid_email

def fetch_remotive():
    rows = []
    try:
        jobs = requests.get("https://remotive.com/api/remote-jobs", timeout=15).json().get("jobs", [])
        for j in jobs:
            loc = j.get("candidate_required_location", "").lower()
            if ("worldwide" in loc or "anywhere" in loc) and matches_criteria(j.get("title", ""), loc):
                rows.append({"lane": "remote", "company": j.get("company_name", "").strip(),
                             "role": j.get("title", "").strip(), "email": "",
                             "apply_url": j.get("url", "").strip(), "source": "remotive"})
    except Exception as e:
        print("Remotive err:", e)
    return rows

def fetch_hn():
    rows = []
    try:
        s_url = "https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&query=Who%20is%20hiring"
        sid = requests.get(s_url, timeout=15).json()["hits"][0]["objectID"]
        comments = requests.get(f"https://hn.algolia.com/api/v1/items/{sid}", timeout=20).json().get("children", [])
        for c in comments:
            txt = re.sub(r"<[^>]+>", " ", html.unescape(c.get("text") or ""))
            emails = EMAIL_REGEX.findall(txt)
            if "remote" in txt.lower() and emails and valid_email(emails[0], check_mx=False) and not txt.strip().lower().startswith(("location:", "seeking")) and any(w in txt.lower() for w in ("hiring", "apply", "careers", "role", "position", "openings", "looking for")):
                comp = txt.strip().split("|")[0][:55].strip() or "HN Startup"
                if matches_criteria(comp, txt):
                    rows.append({"lane": "remote", "company": comp, "role": "Software / Data / Cloud (HN)",
                                 "email": emails[0], "apply_url": f"https://news.ycombinator.com/item?id={c.get('id')}",
                                 "source": "hackernews"})
    except Exception as e:
        print("HN err:", e)
    return rows

def run():
    added = save_jobs(fetch_remotive() + fetch_hn())
    print(f"[Remote] Added {added} new jobs.")

if __name__ == "__main__":
    run()
