# Security Policy

## Supported Versions

The `main` branch is the actively maintained version of OBE-ExamViz.

## Reporting A Vulnerability

If you find a security or privacy issue, please do not publish private data in a public issue.

Use a private channel with the repository owner when possible, or open a public issue that describes the risk without including:

- API keys or tokens
- Student names or student numbers
- Real score workbooks
- Real teaching syllabi
- Local databases
- Exported reports containing private teaching data

## Privacy Commitments

The project is designed so that:

- Local `.env` files are ignored.
- Local SQLite databases are ignored.
- Real data folders and generated output folders are ignored.
- AI generation should use aggregated or anonymized context instead of direct student identifiers.

## Maintainer Checklist

Before publishing changes:

```bash
./scripts/verify_delivery.sh
git status --short
```

Also scan staged files for accidental private data when screenshots, spreadsheets, documents, or templates changed.

Dependency changes are checked by the GitHub Security Audit workflow. For a local audit, run `npm audit --omit=dev` in `frontend/` and `pip-audit --local` after installing the backend dependencies.
