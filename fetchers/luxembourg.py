import requests
from fetchers.config import matches_criteria, save_jobs

COMPANIES = ["Devoteam", "ALTEN", "Capgemini", "EY", "PwCLuxembourg", "NTTData", "SopraSteria"]

def fetch_lux():
    rows = []
    for c in COMPANIES:
        try:
            r = requests.get(f"https://api.smartrecruiters.com/v1/companies/{c}/postings?country=lu", timeout=10)
            for j in r.json().get("content", []):
                title = j.get("name", "")
                if matches_criteria(title, "", check_location=False):
                    rows.append({"lane": "luxembourg", "company": c, "role": title.strip(),
                                 "email": "", "apply_url": f"https://jobs.smartrecruiters.com/{c}/{j.get('id')}",
                                 "source": "smartrecruiters"})
        except Exception:
            pass
    return rows

def run():
    added = save_jobs(fetch_lux())
    print(f"[Luxembourg] Added {added} new jobs.")

if __name__ == "__main__":
    run()
