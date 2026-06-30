# Changelog

All notable public maintenance changes are tracked here.

## 2026-06-30

- Added `scripts/package_release.sh` to build a sanitized teacher-facing zip from tracked public files.
- Added package path and secret audits to reject local databases, `.env` files, private data folders, output folders, dependency folders, and unsupported Office files.
- Updated GitHub Actions to upload `OBE-ExamViz-teacher.zip` as a workflow artifact.
- Documented local and CI release packaging in README, checklist, and contribution docs.

## 2026-06-06

- Added bilingual README files with language switching.
- Added safe demo screenshots generated from placeholder data only.
- Added delivery verification guidance and privacy notes.
- Added sanitized teacher deployment documentation and checklist.
- Added GitHub Actions CI, Dependabot, Issue templates, and PR template.
- Added contribution, security, and roadmap documentation.

## 2026-05

- Improved trusted score import flow with preview confirmation.
- Added AI privacy safeguards for report generation.
- Added report readiness checks and blocked incomplete exports.
- Improved course, exam, and report preview workflows.

## 2026-04

- Added analysis-run-centered workflow.
- Added simplified score input template support.
- Added Word report export and OBE attainment calculations.
- Added public sample data for local testing.
