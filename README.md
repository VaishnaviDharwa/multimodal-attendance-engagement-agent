# Multimodal Attendance & Engagement Agent

A privacy-conscious final-year project MVP for recording class attendance and summarizing participation signals.

## Features
- Create course sessions with unique session codes
- Record and prevent duplicate attendance check-ins
- Record participation events (questions, poll responses, group activity, task completion)
- Session dashboard with basic charts
- Export attendance and participation records as CSV
- Local CSV storage for easy demonstration

## Privacy and scope
This MVP intentionally does **not** use face recognition, emotion detection, or covert audio/video recording. It treats participation counts as limited indicators, not proof of attention or learning. Any optional multimodal sensor feature in a future version should be opt-in, transparent, locally processed where possible, and approved by the institution.

## Setup
Requires Python 3.10 or newer.

```bash
python -m venv .venv
```

Activate the environment:
- Windows: `.venv\\Scripts\\activate`
- macOS/Linux: `source .venv/bin/activate`

Install and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser. Data is stored in `data/` as CSV files.

## Suggested final-year extensions
1. Add teacher/student authentication and role-based access.
2. Generate rotating, expiring QR tokens for check-in.
3. Add consent management and audit logs.
4. Add anonymous aggregate classroom activity analytics.
5. Add a session-summary agent that explains trends without ranking students.
6. Add tests, database migrations, and deployment configuration.

## Limitations
- This is an academic prototype, not a production attendance system.
- Session codes are not secure authentication; implement expiring tokens before deployment.
- CSV files are not encrypted and should only contain demo data.
