try:
    from sync_export import refresh_export; refresh_export(quiet=True)
except Exception:
    pass
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import csv, json, os, subprocess
from urllib.parse import parse_qs

BASE = os.path.expanduser("~/job-hunter")
LOG_PATH = os.path.join(BASE, "data", "last_run.log")

def rcsv(p):
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8", errors="ignore") as f: return list(csv.DictReader(f))

def rjson(p):
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8") as f: return json.load(f)

def _launch_bg(label, cmd_str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as lf:
        lf.write(f"=== {label} STARTED ===\n")
    wrapped = (
        f"cd ~/job-hunter && PYTHONUNBUFFERED=1 {cmd_str} >> ~/job-hunter/data/last_run.log 2>&1; "
        f"RC=$?; ST=$([ $RC -eq 0 ] && echo COMPLETE || echo FAILED); "
        f"MSG=\"=== {label} $ST (Queue: $(tail -n +2 ~/job-hunter/data/jobs_queue.csv 2>/dev/null | wc -l) | Sent: $(tail -n +2 ~/job-hunter/data/sent_log.csv 2>/dev/null | wc -l)) ===\"; "
        f"echo -e \"\\n$MSG\" >> ~/job-hunter/data/last_run.log; "
        f"command -v termux-notification >/dev/null 2>&1 && termux-notification -t \"Job-Hunter: {label} $ST\" -c \"${{MSG//=/}}\" || true"
    )
    subprocess.Popen(["bash", "-c", wrapped])

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        act = parse_qs(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()).get("action", [""])[0]
        jobs = {
            "send": ("DAILY SEND", "PYTHONPATH=~/job-hunter python3 -m mailer.reply_watcher && send"),
            "dry": ("AI FIT DRY-RUN", "PYTHONPATH=~/job-hunter python3 -m mailer.send_daily --dry-run"),
            "hunt": ("FULL JOB HUNT", "PYTHONPATH=~/job-hunter python3 -m fetchers.remote && PYTHONPATH=~/job-hunter python3 -m fetchers.luxembourg && PYTHONPATH=~/job-hunter python3 -m fetchers.kolkata && PYTHONPATH=~/job-hunter python3 -m fetchers.uae && PYTHONPATH=~/job-hunter python3 -m fetchers.resolve_emails && PYTHONPATH=~/job-hunter python3 -m fetchers.booster && PYTHONPATH=~/job-hunter python3 mailer/queue_ranker.py --hunt"),
            "rank": ("QUEUE RE-RANK", "PYTHONPATH=~/job-hunter python3 mailer/queue_ranker.py"),
            "fup": ("FOLLOW-UP PREVIEW", "PYTHONPATH=~/job-hunter python3 -m mailer.followup --dry-run"),
            "replies": ("REPLY CHECK", "PYTHONPATH=~/job-hunter python3 -m mailer.reply_watcher"),
        }
        try:
            if act in jobs:
                _launch_bg(*jobs[act])
                msg = f"{jobs[act][0]} started — watch Live Activity Monitor below."
            elif act == "stop":
                subprocess.run(["pkill", "-f", "mailer\\.(send_daily|followup)|fetchers\\."])
                with open(LOG_PATH, "a", encoding="utf-8") as _lf: _lf.write("\n=== ACTIVITY STOPPED ===\n")
                msg = "Stopped active background task."
            else: msg = ""
        except Exception as e: msg = str(e)
        self.do_GET(banner=msg)

    def do_GET(self, banner=""):
        if self.path.startswith("/api/stats"):
            q, s = rcsv(f"{BASE}/data/jobs_queue.csv"), rcsv(f"{BASE}/data/sent_log.csv")
            log_txt = ""
            if os.path.exists(LOG_PATH):
                with open(LOG_PATH, encoding="utf-8", errors="ignore") as _lf: log_txt = _lf.read()
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"queued": len(q), "sent": len(s), "log": log_txt[-4000:]}).encode())
            return
        from dash_ui import render_page
        q, s, b = rcsv(f"{BASE}/data/jobs_queue.csv"), rcsv(f"{BASE}/data/sent_log.csv"), rjson(f"{BASE}/data/followup_sent.json")
        res = sorted({f for _, _, fs in os.walk(BASE) for f in fs if f.lower().endswith(".pdf")})
        poller = """<script>
async function poll(){try{const d=await(await fetch("/api/stats?t="+Date.now())).json();document.getElementById("live-counts").textContent=`Queue: ${d.queued} | Sent: ${d.sent}`;document.getElementById("kpi-qn").textContent=d.queued;document.getElementById("kpi-sn").textContent=d.sent;document.getElementById("tab-qn").textContent=d.queued;document.getElementById("tab-sn").textContent=d.sent;const lines=(d.log||"").trim().split("\\n").filter(Boolean),pre=document.getElementById("live-pre"),st=document.getElementById("live-status");if(lines.length){pre.textContent=lines.slice(-6).join("\\n");pre.scrollTop=pre.scrollHeight;const m=[...lines].reverse().find(l=>l.startsWith("==="));if(m&&m.includes("STARTED")){st.textContent="⏳ "+m.replace("STARTED","IN PROGRESS...").replace(/=/g,"").trim();st.style.color="#fbbf24";}else if(m){const ok=m.includes("COMPLETE");st.textContent=(ok?"✅ ":"⚠️ ")+m.replace(/=/g,"").trim();st.style.color=ok?"#4ade80":"#f87171";}}}catch(e){}}poll();setInterval(poll,2000);
</script>"""
        page = render_page(q, s, b, res, banner) + poller
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
        self.wfile.write(page.encode())

if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 5050), Handler).serve_forever()
