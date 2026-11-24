# Job-Hunter OS

Autonomous multi-region job discovery, deliverability verification, and LLM-personalized email outreach engine with a local web command center.

## Key Features
- **4-Lane Ingestion:** Crawls Worldwide Remote, Luxembourg, Kolkata, and UAE openings via SmartRecruiters, Greenhouse, Remotive, Hacker News Algolia, and Google News RSS APIs.
- **Zero-Bounce Deliverability Guard:** Performs real-time Cloudflare `1.1.1.1` DNS-over-HTTPS MX record verification and auto-harvests Gmail `mailer-daemon` bounces via IMAP.
- **LLM Fit Scoring & Dynamic Resume Routing:** Uses Groq LLMs to score role alignment (1–10), write tailored first-person hooks, attach role-matched PDF resumes, and enforce quota-paced SMTP dispatch with automated 5–12 day follow-ups.
- **Live Command Center UI:** Mobile-first `ThreadingHTTPServer` web dashboard with real-time background log streaming, queue freshness ranking, and AST/bytecode self-auditing.
