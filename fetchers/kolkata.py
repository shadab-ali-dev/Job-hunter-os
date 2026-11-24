import re, requests, xml.etree.ElementTree as ET
from fetchers.config import matches_criteria, save_jobs

KOL_COMPANIES = ["Capgemini", "Cognizant", "Genpact", "Wipro", "Deloitte", "EY", "PwCIndia"]

def fetch_sr_kolkata():
    rows = []
    for c in KOL_COMPANIES:
        try:
            r = requests.get(f"https://api.smartrecruiters.com/v1/companies/{c}/postings?country=in&city=Kolkata", timeout=10)
            for j in r.json().get("content", []):
                title = j.get("name", "")
                if matches_criteria(title, "", check_location=False):
                    rows.append({"lane": "kolkata", "company": c, "role": title.strip(),
                                 "email": "", "apply_url": f"https://jobs.smartrecruiters.com/{c}/{j.get('id')}",
                                 "source": "smartrecruiters"})
        except Exception:
            pass
    return rows

def fetch_rss_kolkata():
    rows = []
    q = "Kolkata+(Oracle+OR+DBA+OR+Python+OR+Frontend+OR+%22Data+Analyst%22+OR+%22Software+Engineer%22)+hiring"
    try:
        xml_data = requests.get(f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en", timeout=15).text
        root = ET.fromstring(xml_data)
        for item in root.findall(".//item")[:25]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if matches_criteria(title, "", check_location=False):
                parts = title.rsplit(" - ", 1)
                role = parts[0][:65].strip()
                comp = parts[1].strip() if len(parts) > 1 else "Kolkata IT Employer"
                rows.append({"lane": "kolkata", "company": comp, "role": role,
                             "email": "", "apply_url": link, "source": "google_rss"})
    except Exception as e:
        print("RSS err:", e)
    return rows

def run():
    added = save_jobs(fetch_sr_kolkata() + fetch_rss_kolkata())
    print(f"[Kolkata] Added {added} new jobs.")

if __name__ == "__main__":
    run()
