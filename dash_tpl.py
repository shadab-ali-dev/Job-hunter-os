HTML_TPL = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Job-Hunter Command Center</title><style>
*{{box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;background:#07090e;background-image:radial-gradient(rgba(148,163,184,.09) 1px,transparent 0);background-size:22px 22px;color:#e2e8f0;margin:0;padding-bottom:32px}}
.top{{background:rgba(7,9,14,.88);backdrop-filter:blur(18px);border-bottom:1px solid rgba(255,255,255,.08);padding:14px 16px;position:sticky;top:0;z-index:20}}
.brand{{display:flex;justify-content:space-between;align-items:center}}
.brand-l{{display:flex;align-items:center;gap:9px;font-weight:700;font-size:15px;letter-spacing:-.3px;color:#fff}}
.logo{{width:26px;height:26px;border-radius:7px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:grid;place-items:center;box-shadow:0 0 16px rgba(99,102,241,.45)}}
.tabs{{display:flex;gap:4px;margin-top:12px;background:rgba(255,255,255,.04);padding:4px;border-radius:10px;border:1px solid rgba(255,255,255,.06)}}
.tab{{flex:1;background:transparent;color:#94a3b8;border:none;padding:7px 8px;border-radius:7px;font-size:12px;font-weight:600;transition:.15s}}
.tab.active{{background:#181e2c;color:#fff;box-shadow:0 1px 3px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.1)}}
.wrap{{max-width:860px;margin:auto;padding:14px}}.sec{{display:none}}.sec.active{{display:block}}
.g{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}
.card,.mcard{{background:linear-gradient(180deg,rgba(24,30,44,.75),rgba(13,17,26,.85));border:1px solid rgba(255,255,255,.08);box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 10px 25px rgba(0,0,0,.35);border-radius:14px;padding:14px;position:relative;overflow:hidden}}
.k1::before,.k2::before,.k3::before,.k4::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px}}
.k1::before{{background:linear-gradient(90deg,#3b82f6,transparent)}}.k2::before{{background:linear-gradient(90deg,#10b981,transparent)}}.k3::before{{background:linear-gradient(90deg,#f59e0b,transparent)}}.k4::before{{background:linear-gradient(90deg,#8b5cf6,transparent)}}
.v{{font-size:28px;font-weight:800;letter-spacing:-.8px;color:#fff}}.l{{font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.6px;margin-top:4px}}
.donut-box{{display:flex;align-items:center;gap:16px;margin-top:10px}}
.legend{{flex:1;display:grid;gap:8px}}.lrow{{display:flex;justify-content:space-between;align-items:center;font-size:12px}}
.dot{{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:7px}}
h2{{font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:.8px;margin:18px 0 8px}}
.btn{{width:100%;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;gap:3px;padding:11px 12px;border:1px solid rgba(255,255,255,.09);border-radius:11px;background:#131824;color:#e2e8f0;text-align:left;box-shadow:inset 0 1px 0 rgba(255,255,255,.06);cursor:pointer}}
.btn:active{{transform:scale(.98)}}
.bt{{display:flex;align-items:center;gap:6px;font-weight:700;font-size:12.5px;color:#fff}}
.bd{{font-size:10.5px;line-height:1.3;color:rgba(255,255,255,.72);font-weight:400}}
.bg{{background:linear-gradient(135deg,#059669,#10b981);border:none;box-shadow:0 4px 18px rgba(16,185,129,.28)}}
.bb{{background:linear-gradient(135deg,#2563eb,#4f46e5);border:none;box-shadow:0 4px 18px rgba(59,130,246,.28)}}
.br{{background:linear-gradient(135deg,#b91c1c,#dc2626);border:none;box-shadow:0 4px 18px rgba(220,38,38,.25)}}
.mon{{background:#090d16;border:1px solid rgba(56,189,248,.28);border-radius:12px;padding:11px 12px;margin-top:12px}}
.mon-h{{display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:700;margin-bottom:6px}}
.mon pre{{font-family:ui-monospace,monospace;font-size:11px;line-height:1.45;white-space:pre-wrap;max-height:130px;overflow-y:auto;margin:0;color:#cbd5e1}}
.console{{background:#090c12;border:1px solid rgba(59,130,246,.35);border-radius:12px;padding:11px;margin-bottom:12px}}
.chead{{display:flex;justify-content:space-between;font-size:10px;font-weight:700;color:#60a5fa;letter-spacing:.8px}}
.console pre{{font-family:ui-monospace,monospace;font-size:11px;white-space:pre-wrap;max-height:140px;overflow:auto;margin:7px 0 0;color:#cbd5e1}}
.chip{{display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:5px 10px;font-size:12px;margin:3px}}
.chip i{{font-style:normal;font-size:10px;font-weight:700;background:rgba(59,130,246,.2);color:#60a5fa;padding:1px 6px;border-radius:5px}}
.tag{{padding:2px 7px;border-radius:5px;font-size:10px;font-weight:700}}
.t-remote{{background:rgba(59,130,246,.16);color:#60a5fa}}.t-luxembourg{{background:rgba(245,158,11,.16);color:#fbbf24}}.t-kolkata{{background:rgba(16,185,129,.16);color:#34d399}}.t-uae{{background:rgba(168,85,247,.16);color:#c084fc}}
.badge-ok{{background:rgba(16,185,129,.14);color:#34d399;border:1px solid rgba(16,185,129,.3);padding:2px 8px;border-radius:99px;font-size:10px;font-weight:700}}
.ct{{font-weight:600;color:#fff;font-size:13px}}.sb{{color:#94a3b8;font-size:12px;line-height:1.4;margin-top:2px}}
.mn{{font-family:ui-monospace,monospace;font-size:11px;color:#7dd3fc}}
.ritem{{display:flex;align-items:center;gap:10px;padding:9px 0;border-top:1px solid rgba(255,255,255,.06)}}.ritem:first-child{{border-top:none;padding-top:0}}
.mcard{{margin-bottom:9px}}.mhead{{display:flex;justify-content:space-between;align-items:center}}
table{{width:100%;border-collapse:collapse;background:#0f141f;border:1px solid rgba(255,255,255,.08);border-radius:12px;overflow:hidden}}
td{{padding:10px;border-top:1px solid rgba(255,255,255,.06);vertical-align:top}}
input{{width:100%;padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.1);background:#0f141f;color:#fff;margin-bottom:10px;font-size:13px}}
</style></head><body>
<div class='top'><div class='brand'><div class='brand-l'><div class='logo'><svg width='15' height='15' viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='2.5'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'/></svg></div><span>Job-Hunter OS</span></div><span class='badge-ok'>● 6 ENGINES LIVE</span></div>
<div class='tabs'>
<button class='tab active' onclick="st('ov',this)">Overview</button>
<button class='tab' onclick="st('qu',this)">Queue (<span id='tab-qn'>{qn}</span>)</button>
<button class='tab' onclick="st('se',this)">Sent (<span id='tab-sn'>{sn}</span>)</button>
<button class='tab' onclick="st('ar',this)">Engines</button>
</div></div><div class='wrap'>{al}
<div id='ov' class='sec active'>
<div class='g'>
<div class='card k1'><div class='v' id='kpi-qn'>{qn}</div><div class='l'>Queued Leads</div></div>
<div class='card k2'><div class='v' id='kpi-sn'>{sn}</div><div class='l'>Emails Sent</div></div>
<div class='card k3'><div class='v'>{bn}</div><div class='l'>Follow-Up Bumps</div></div>
<div class='card k4'><div class='v'>{rn}</div><div class='l'>Active Resumes</div></div>
</div>
<div class='card donut-box'>
<svg width='86' height='86' viewBox='0 0 36 36' style='transform:rotate(-90deg)'>
<circle cx='18' cy='18' r='15.915' fill='transparent' stroke='#1e293b' stroke-width='3.6'/>
<circle cx='18' cy='18' r='15.915' fill='transparent' stroke='#3b82f6' stroke-width='3.6' stroke-dasharray='{pr} 100' stroke-dashoffset='0'/>
<circle cx='18' cy='18' r='15.915' fill='transparent' stroke='#f59e0b' stroke-width='3.6' stroke-dasharray='{pl} 100' stroke-dashoffset='{o2}'/>
<circle cx='18' cy='18' r='15.915' fill='transparent' stroke='#10b981' stroke-width='3.6' stroke-dasharray='{pk} 100' stroke-dashoffset='{o3}'/>
<circle cx='18' cy='18' r='15.915' fill='transparent' stroke='#a855f7' stroke-width='3.6' stroke-dasharray='{pu} 100' stroke-dashoffset='{o4}'/>
</svg>
<div class='legend'>
<div class='lrow'><span><i class='dot' style='background:#3b82f6'></i>Worldwide Remote</span><b>{qr} <small style='color:#64748b'>({sr} sent)</small></b></div>
<div class='lrow'><span><i class='dot' style='background:#f59e0b'></i>Luxembourg</span><b>{ql} <small style='color:#64748b'>({sl} sent)</small></b></div>
<div class='lrow'><span><i class='dot' style='background:#10b981'></i>Kolkata</span><b>{qk} <small style='color:#64748b'>({sk} sent)</small></b></div>
<div class='lrow'><span><i class='dot' style='background:#a855f7'></i>UAE (Dubai/AD)</span><b>{qu} <small style='color:#64748b'>({su} sent)</small></b></div>
</div></div>
<div class='mon'>
<div class='mon-h'><span id='live-status' style='color:#38bdf8'>● LIVE ACTIVITY MONITOR</span><span id='live-counts' style='color:#4ade80'>Queue: {qn} | Sent: {sn}</span></div>
<pre id='live-pre'>Idle — tap any action below to run.</pre>
</div>
<h2>Pipeline Actions</h2>
<form method='post' class='g' onsubmit="this.style.opacity='.6'">
<button class='btn bg' name='action' value='send'><span class='bt'>▶ Run Daily Send</span><span class='bd'>Send up to 5 verified emails/lane (20 max) + 5d bumps</span></button>
<button class='btn br' name='action' value='stop'><span class='bt'>■ Stop Sending</span><span class='bd'>Immediately halt any running mail or hunt task</span></button>
<button class='btn bb' name='action' value='dry'><span class='bt'>✦ AI Fit Dry-Run</span><span class='bd'>Preview today's AI-scored picks without sending</span></button>
<button class='btn' name='action' value='hunt'><span class='bt'>⌕ Full Job Hunt</span><span class='bd'>Crawl Remote, Luxembourg, Kolkata & UAE boards</span></button>
<button class='btn' name='action' value='rank'><span class='bt'>⇅ Re-Rank Queue</span><span class='bd'>Sort leads by freshness & prune posts >30 days</span></button>
<button class='btn' name='action' value='fup'><span class='bt'>↻ Preview Follow-Ups</span><span class='bd'>List 5–12d un-replied leads eligible for a bump</span></button>
<button class='btn' name='action' value='replies' style='grid-column:span 2'><span class='bt'>✉ Check Recruiter Replies</span><span class='bd'>Scan Gmail inbox for new recruiter responses</span></button>
</form>
<h2>Top Hiring Companies</h2><div class='card'>{pills}</div>
<h2>Role-Matched Resumes</h2><div class='card'>{rlist}</div>
</div>
<div id='qu' class='sec'><input placeholder='Filter queued leads...' onkeyup="ft('qt',this.value)"><table id='qt'>{q_rows}</table></div>
<div id='se' class='sec'><input placeholder='Filter sent log...' onkeyup="ft('st',this.value)"><table id='st'>{s_rows}</table></div>
<div id='ar' class='sec'><h2>Active Automation Modules</h2>{mcards}</div>
</div><script>
function st(id,b){{document.querySelectorAll('.sec').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active');b.classList.add('active')}}
function ft(t,q){{q=q.toLowerCase();document.querySelectorAll('#'+t+' tr').forEach(r=>r.style.display=r.innerText.toLowerCase().includes(q)?'':'none')}}
</script></body></html>"""
