import re, requests, xml.etree.ElementTree as ET
from fetchers.config import EMAIL_REGEX, matches_criteria, save_jobs
from mailer.lead_guard import valid_email

UAE_SR_COMPANIES = [
    ("Capgemini", "careers.me@capgemini.com"),
    ("Cognizant", "careersuae@cognizant.com"),
    ("Wipro", "helpdesk.recruitment@wipro.com"),
    ("Deloitte", "mecareers@deloitte.com"),
    ("EY", "recruitment.mena@ae.ey.com"),
    ("PwCMiddleEast", "me_recruitment@pwc.com"),
    ("MajidAlFuttaim", "careers@maf.ae"),
    ("ChalhoubGroup", "careers@chalhoub.com"),
    ("Accor", "talent.middleeast@accor.com"),
    ("Talabat", "careers@talabat.com"),
    ("AlFuttaim", "careers@alfuttaim.com"),
    ("EmiratesNBD", "careers@emiratesnbd.com"),
    ("FirstAbuDhabiBank", "careers@bankfab.com"),
    ("DPWorld", "careers@dpworld.com"),
    ("Etihad", "recruitment@etihad.ae"),
]

# Greenhouse & Lever public JSON APIs for UAE-hiring tech companies
UAE_GREENHOUSE_BOARDS = [
    ("careem", "Careem (Dubai)", "jobs@careem.com"),
    ("tabby", "Tabby (Dubai Fintech)", "careers@tabby.ai"),
    ("propertyfinder", "Property Finder (Dubai)", "careers@propertyfinder.ae"),
    ("kitopi", "Kitopi (Dubai)", "talent@kitopi.com"),
    ("foodics", "Foodics (Dubai/Riyadh)", "careers@foodics.com"),
    ("anghami", "Anghami (Abu Dhabi)", "careers@anghami.com"),
    ("starzplay", "STARZPLAY (Abu Dhabi)", "careers@starzplay.com"),
]

UAE_TARGETS = [
    ("uae", "Bayut & dubizzle (Dubai)", "Backend / Python / Frontend Engineer", "careers@dubizzle.com"),
    ("uae", "Ziina (Dubai Fintech)", "Backend / Full Stack Software Engineer", "careers@ziina.com"),
    ("uae", "Alaan (Dubai Fintech)", "Software / Frontend / Data Engineer", "careers@alaanpay.com"),
    ("uae", "Yalla Group (Dubai)", "Software / Frontend / Database Engineer", "hr@yallagroup.com"),
    ("uae", "ValueLabs (Dubai)", "Python / SQL / Software Developer", "careers@valuelabs.com"),
    ("uae", "G42 (Abu Dhabi AI)", "Python / Data / Cloud Engineer", "careers@g42.ai"),
    ("uae", "Alpheya (Abu Dhabi Fintech)", "Software / Frontend / Backend Engineer", "careers@alpheya.com"),
]

def fetch_sr_uae():
    rows = []
    for comp, hr_email in UAE_SR_COMPANIES:
        try:
            r = requests.get(f"https://api.smartrecruiters.com/v1/companies/{comp}/postings?country=ae", timeout=10)
            for j in r.json().get("content", []):
                title = j.get("name", "")
                if matches_criteria(title, "", check_location=False):
                    rows.append({
                        "lane": "uae", "company": comp, "role": title.strip(),
                        "email": hr_email, "apply_url": f"https://jobs.smartrecruiters.com/{comp}/{j.get('id')}",
                        "source": "smartrecruiters_ae"
                    })
        except Exception:
            pass
    return rows

def fetch_greenhouse_uae():
    rows = []
    for slug, label, hr_email in UAE_GREENHOUSE_BOARDS:
        try:
            r = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", timeout=10)
            for j in r.json().get("jobs", []):
                title = j.get("title", "")
                loc = (j.get("location") or {}).get("name", "").lower()
                if any(k in loc for k in ("dubai", "abu dhabi", "uae", "emirates", "remote", "mena")):
                    if matches_criteria(title, loc, check_location=False):
                        rows.append({
                            "lane": "uae", "company": label, "role": title.strip(),
                            "email": hr_email, "apply_url": j.get("absolute_url", ""),
                            "source": "greenhouse_ae"
                        })
        except Exception:
            pass
    return rows

def fetch_rss_uae():
    rows = []
    queries = [
        "(Dubai+OR+%22Abu+Dhabi%22)+(Python+OR+%22Software+Engineer%22+OR+Frontend+OR+%22Data+Analyst%22)+hiring",
        "(Dubai+OR+UAE)+(Oracle+OR+DBA+OR+SQL+OR+AWS+OR+Backend)+hiring",
    ]
    for q in queries:
        try:
            xml_data = requests.get(f"https://news.google.com/rss/search?q={q}&hl=en-AE&gl=AE&ceid=AE:en", timeout=15).text
            root = ET.fromstring(xml_data)
            for item in root.findall(".//item")[:25]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                if matches_criteria(title, "", check_location=False):
                    parts = title.rsplit(" - ", 1)
                    role = parts[0][:65].strip()
                    comp = parts[1].strip() if len(parts) > 1 else "UAE Tech Employer"
                    rows.append({
                        "lane": "uae", "company": comp, "role": role,
                        "email": "", "apply_url": link, "source": "google_rss_ae"
                    })
        except Exception:
            pass
    return rows

def run():
    static_rows = [{"lane": l, "company": c, "role": r, "email": e, "apply_url": "", "source": "uae_hr"} for l, c, r, e in UAE_TARGETS]
    fetched = fetch_sr_uae() + fetch_greenhouse_uae() + fetch_rss_uae() + static_rows
    added = save_jobs(fetched)
    print(f"[UAE] Fetched {len(fetched)} matching postings -> Added {added} new unique jobs.")

if __name__ == "__main__":
    run()
