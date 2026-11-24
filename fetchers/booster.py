import html, re, requests
from fetchers.config import EMAIL_REGEX, matches_criteria, save_jobs
from mailer.lead_guard import valid_email

def fetch_hn_regional():
    rows = []
    try:
        stories = requests.get("https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&query=Who%20is%20hiring&hitsPerPage=3", timeout=15).json().get("hits", [])
        for s in stories:
            comments = requests.get(f"https://hn.algolia.com/api/v1/items/{s['objectID']}", timeout=20).json().get("children", [])
            for c in comments:
                txt = re.sub(r"<[^>]+>", " ", html.unescape(c.get("text") or ""))
                emails = EMAIL_REGEX.findall(txt)
                if not emails or not valid_email(emails[0], check_mx=False) or txt.strip().lower().startswith(('location:', 'seeking')) or not any(w in txt.lower() for w in ('hiring', 'apply', 'careers', 'role', 'position', 'openings', 'looking for')) or not matches_criteria(txt[:80], txt, check_location=False):
                    continue
                low = txt.lower()
                comp = txt.strip().split("|")[0][:50].strip() or "Tech Employer"
                if any(k in low for k in ("luxembourg", "europe", "eu ", "cet", "emea")):
                    rows.append({"lane": "luxembourg", "company": comp, "role": "Software / Cloud / Data Engineer", "email": emails[0], "apply_url": "", "source": "hn_eu"})
                elif any(k in low for k in ("dubai", "abu dhabi", "uae", "united arab emirates", "mena", "gulf")):
                    rows.append({"lane": "uae", "company": comp, "role": "Software / Cloud / Data Engineer", "email": emails[0], "apply_url": "", "source": "hn_uae"})
                elif any(k in low for k in ("india", "kolkata", "bangalore", "ist", "apac")):
                    rows.append({"lane": "kolkata", "company": comp, "role": "Software / Oracle / Data Role", "email": emails[0], "apply_url": "", "source": "hn_in"})
    except Exception as e:
        print("HN regional err:", e)
    return rows

REGIONAL_TARGETS = [
    ("kolkata", "FusionCharts (Kolkata Startup)", "Frontend / UI-UX / JS Engineer", "careers@fusioncharts.com"),
    ("kolkata", "Data Sutram (Kolkata AI Startup)", "Data Analyst / Python Engineer", "careers@datasutram.com"),
    ("kolkata", "TagMango (Kolkata SaaS Startup)", "Full Stack / Frontend Engineer", "careers@tagmango.com"),
    ("kolkata", "Mihup (Kolkata AI Startup)", "Python / Backend / Data Engineer", "hr@mihup.com"),
    ("kolkata", "Capital Numbers (Sector V)", "Frontend / UI-UX / Python Developer", "careers@capitalnumbers.com"),
    ("kolkata", "Indus Net Technologies (Sector V)", "Oracle DBA / SQL / Software Engineer", "careers@indusnet.co.in"),
    ("kolkata", "BlueCopper Technologies (Kolkata)", "Software / Database / UI Engineer", "hr@bluecoppertech.com"),
    ("kolkata", "ITC Infotech (Kolkata)", "Oracle DBA / SQL / Cloud Engineer", "careers@itcinfotech.com"),
    ("luxembourg", "Finologee (Lux Fintech Startup)", "Software / API / Cloud Engineer", "jobs@finologee.com"),
    ("luxembourg", "Salonkee (Lux Scale-up)", "Frontend / UI-UX / Backend Engineer", "jobs@salonkee.com"),
    ("luxembourg", "Scorechain (Lux RegTech Startup)", "Data Analyst / Python Engineer", "jobs@scorechain.com"),
    ("luxembourg", "Docler Holding (Luxembourg)", "Software / Database / Cloud Engineer", "recruitment@doclerholding.com"),
    ("luxembourg", "Talkwalker (Luxembourg)", "Data Analyst / Backend Engineer", "careers@talkwalker.com"),
    ("luxembourg", "NSI Luxembourg", "Oracle DBA / Java / Python Engineer", "recruitment@nsi-sa.lu"),
]

def run():
    static_rows = [{"lane": l, "company": c, "role": r, "email": e, "apply_url": "", "source": "regional_hr"} for l, c, r, e in REGIONAL_TARGETS]
    added = save_jobs(fetch_hn_regional() + static_rows)
    print(f"[Booster] Added {added} new regional jobs.")

if __name__ == "__main__":
    run()
