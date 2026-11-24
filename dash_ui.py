import html
from collections import Counter
from mailer.ai_personalizer import is_obviously_fake_or_noise

MODS = [
    ("Live DNS MX & Bounce Shield", "mailer/bounce_shield.py", "Cloudflare 1.1.1.1 DoH MX lookup + disposable/trap domain blocker before SMTP."),
    ("Anti-Fake & Noise Gate", "mailer/ai_personalizer.py", "0ms rule filter stripping SEEKING WORK posts, fee scams, and brand impersonators."),
    ("Groq AI Fit Scorer & Hook", "mailer/ai_personalizer.py", "Scores roles 1–10 and crafts a tailored 1-sentence hook per company."),
    ("5–12 Day Auto Follow-Ups", "mailer/followup.py", "IMAP-verified thread bumps for un-replied leads with 60–150s pacing."),
    ("IMAP Recruiter Reply Watcher", "mailer/reply_watcher.py", "Real-time inbox scanner triggering native Android Termux alerts."),
    ("Multi-Lane Resume Router", "fetchers/* & send_daily.py", "Remote, Luxembourg, Kolkata & UAE crawlers with role-matched PDF attachments.")
]

def render_page(q, s, b, res, banner=""):
    lanes = Counter((r.get("lane") or "other").lower() for r in q)
    slanes = Counter((r.get("lane") or "other").lower() for r in s)
    clean_cos = [(r.get("company") or "").strip() for r in q if (r.get("company") or "").strip() and not is_obviously_fake_or_noise(r.get("company", ""), r.get("role", ""), r.get("email", ""))[0]]
    top_co = Counter(clean_cos).most_common(10)
    tot = max(len(q), 1)
    pr, pl, pk, pu = round(lanes.get('remote',0)*100/tot, 1), round(lanes.get('luxembourg',0)*100/tot, 1), round(lanes.get('kolkata',0)*100/tot, 1), round(lanes.get('uae',0)*100/tot, 1)
    q_rows = "".join(f"<tr><td><span class='tag t-{html.escape(r.get('lane','').lower())}'>{html.escape(r.get('lane','').upper())}</span></td><td><div class='ct'>{html.escape(r.get('company','')[:32])}</div><div class='sb'>{html.escape(r.get('role','')[:44])}</div></td><td class='mn'>{html.escape(r.get('email','')[:30])}</td></tr>" for r in q[:30]) or "<tr><td colspan='3' class='sb'>Queue empty</td></tr>"
    s_rows = "".join(f"<tr><td><div class='mn'>{html.escape(r.get('date','')[:10])}</div><span class='tag t-{html.escape(r.get('lane','').lower())}'>{html.escape(r.get('lane','').upper())}</span></td><td><div class='ct'>{html.escape(r.get('company','')[:30])}</div><div class='sb'>{html.escape(r.get('role','')[:40])}</div></td><td class='mn'>{html.escape(r.get('email','')[:28])}</td></tr>" for r in reversed(s[-30:])) or "<tr><td colspan='3' class='sb'>No sent emails yet</td></tr>"
    pills = "".join(f"<span class='chip'>{html.escape(c)}<i>{n}</i></span>" for c, n in top_co) or "<span class='sb'>No companies yet</span>"
    rlist = "".join(f"<div class='ritem'><svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#60a5fa' stroke-width='2'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><polyline points='14 2 14 8 20 8'/></svg><div><div class='ct'>{html.escape(x)}</div><div class='sb'>Auto-attached by role specialty</div></div></div>" for x in res)
    mcards = "".join(f"<div class='mcard'><div class='mhead'><span class='ct'>{i:02d} · {html.escape(t)}</span><span class='badge-ok'>ACTIVE</span></div><div class='mn' style='margin:5px 0'>{html.escape(p)}</div><div class='sb'>{html.escape(d)}</div></div>" for i, (t, p, d) in enumerate(MODS, 1))
    al = f"<div class='console'><div class='chead'><span>TERMINAL OUTPUT</span><span onclick='this.parentElement.parentElement.remove()' style='cursor:pointer'>✕</span></div><pre>{html.escape(banner)}</pre></div>" if banner else ""
    from dash_tpl import HTML_TPL
    return HTML_TPL.format(al=al, qn=len(q), sn=len(s), bn=len(b), rn=len(res), qr=lanes.get('remote',0), sr=slanes.get('remote',0), pr=pr, ql=lanes.get('luxembourg',0), sl=slanes.get('luxembourg',0), pl=pl, qk=lanes.get('kolkata',0), sk=slanes.get('kolkata',0), pk=pk, qu=lanes.get('uae',0), su=slanes.get('uae',0), pu=pu, o2=-pr, o3=-(pr+pl), o4=-(pr+pl+pk), pills=pills, rlist=rlist, q_rows=q_rows, s_rows=s_rows, mcards=mcards)
