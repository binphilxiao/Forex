# Documentation Hub

Welcome to the consolidated documentation for the Forex data toolkit. This index explains what each document covers and points you to the most relevant guides.

- Project overview: `doc/overview/`
- End-to-end workflows: `doc/workflows/`
- Script and configuration references: `doc/reference/`
- Operations and troubleshooting: `doc/operations/`
- Release history: `doc/CHANGELOG.md`

## Quick Links

- **Getting started**: `../README.md`
- **Hands-on walkthrough**: `../QUICKSTART.md`
- **Release notes**: `doc/CHANGELOG.md`
- **Script catalogue**: `doc/reference/script_catalog.md`
- **Database schema**: `doc/reference/database_schema.md`
- **Data pipeline playbook**: `doc/workflows/data_pipeline.md`

## How the Docs Are Structured

| Section           | Purpose                                                   |
|-------------------|-----------------------------------------------------------|
| overview/         | High-level architecture and component map.                |
| workflows/        | Step-by-step guides for typical data and web workflows.   |
| reference/        | Command reference, configuration schema, glossary.        |
| operations/       | Maintenance checklists, troubleshooting tips.             |

## Maintenance Checklist

1. Update `doc/CHANGELOG.md` when scripted behaviour or user flow changes.
2. Keep command examples aligned with the CLI `--help` output of each script.
3. Run `python scripts\verify_docs.py` before tagging a release to catch broken links.
4. When adding a new script, document it in `doc/reference/script_catalog.md`.
