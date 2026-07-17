# Contributing

Thank you for helping maintain OBE-ExamViz. This project is built for privacy-aware local exam analysis, so contribution quality and data hygiene matter as much as code.

## Before You Start

- Read [README.md](README.md) and [CHECKLIST.md](CHECKLIST.md).
- Use public demo data or synthetic data only.
- Do not commit `.env`, databases, real score workbooks, real syllabi, exported reports, screenshots containing private teaching data, or API keys.

## Development Setup

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Verification

Before opening a pull request, run:

```bash
./scripts/verify_delivery.sh
```

This checks patch whitespace, AI privacy risk patterns, backend tests, frontend lint, and the frontend production build.

When dependency files change, also review production dependency audits:

```bash
cd frontend && npm audit --omit=dev
pip-audit --local
```

To verify the release package path, run:

```bash
./scripts/package_release.sh
```

The package audit rejects tracked `.env` files, databases, real data folders, local output folders, dependency folders, and unsupported Office files outside `backend/templates/`.

## Pull Request Checklist

- Explain what changed and why.
- Include screenshots when UI changed.
- Mention the verification commands you ran.
- Confirm no private score files, syllabi, databases, exports, or API keys are included.

## Data Privacy Rules

- Use `sample_data/` or freshly generated mock data for tests and screenshots.
- Keep AI prompts aggregated or anonymized.
- Never send student names or student numbers to external AI services.
- Keep local runtime files in ignored folders such as `data/`, `output/`, and `tmp/`.
