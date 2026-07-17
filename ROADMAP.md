# Roadmap

This roadmap tracks meaningful maintenance work for OBE-ExamViz. It is intentionally focused on reliability, privacy, and teacher-facing usability rather than adding features for their own sake.

## Near Term

- Keep GitHub Actions CI green on `main`.
- Review the weekly Security Audit workflow and Dependabot pull requests.
- Add more parser tests for non-template score workbooks ([#14](https://github.com/YfengJ/OBE-ExamViz/issues/14)).
- Evaluate frontend code-splitting for large chart and UI vendor chunks ([#15](https://github.com/YfengJ/OBE-ExamViz/issues/15)).
- Expand README screenshots when the UI changes, using demo data only.

## Completed Maintenance

- Generate a sanitized teacher-facing zip from CI and upload it as a GitHub Actions artifact.
- Add GitHub issue forms and a Security Audit workflow for safer public maintenance.

## Medium Term

- Add frontend component or end-to-end tests for the main teacher workflow.
- Add Alembic migration scripts for production database upgrades.
- Add a safer report-template fixture so public CI can test Word export without private template content.
- Improve internationalization readiness for English and Chinese interface copy.

## Long Term

- Provide a documented deployment mode for PostgreSQL.
- Add a minimal admin guide for backing up and restoring local data.
- Support release notes and versioned teacher delivery packages.

## Non-Goals

- Do not store or publish real student data in the repository.
- Do not require teachers to manually provide system-computed statistics such as averages, attainment values, or charts.
- Do not make external AI calls mandatory for the core report workflow.
