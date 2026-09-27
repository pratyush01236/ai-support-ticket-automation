# AI Support Ticket Automation

AI-assisted workflow that converts unresolved customer conversations into structured support tickets.

## What it does
- Extracts customer, order, product, issue, evidence, and contact details.
- Requests missing mandatory information.
- Calculates priority from severity, sentiment, waiting time, customer impact, and SLA.
- Excludes configured weekends and holidays from SLA time.
- Warns at 75% SLA consumption and escalates after breach.
- Routes by skill, availability, workload, and business hours.
- Detects duplicates, groups related issues, and separates unrelated issues.
- Generates a masked handoff summary.
- Supports runtime changes to SLA rules, weekends, holidays, and clock time.

## Structure
```
ai-support-ticket-automation/
├── ai/extractor.py
├── core/models.py
├── core/extraction.py
├── core/priority.py
├── core/sla.py
├── core/routing.py
├── core/duplicates.py
├── core/handoff.py
├── config.py
├── app.py
├── tests/test_workflow.py
├── requirements.txt
└── .env.example
```

## Run
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
pytest -q
```

Set `GEMINI_API_KEY` in `.env` for AI extraction. The extractor falls back safely when Gemini is unavailable.

### Runtime SLA
```env
SLA_RULES_JSON={"critical":120,"high":240,"medium":480,"low":1440}
WEEKENDS=5,6
HOLIDAYS=2026-01-01,2026-10-02
BUSINESS_START=09:00
BUSINESS_END=18:00
```

All SLA values are working minutes. Never commit `.env`.
