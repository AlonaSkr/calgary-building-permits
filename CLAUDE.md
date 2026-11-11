# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview
Calgary building-permits analysis following Ask/Prepare/Process/Analyze/Share/Act, documented in a single `README.md`. The user does the analysis in Power BI with DAX; this repo holds the pandas/numpy profiling and cleaning scripts and the DAX measures.

## Commands (run from repo root, with plain `python3`, not `-I`; pandas lives in user site-packages)
- Profile raw data: `python3 scripts/profile_permits.py`
- Check findings: `python3 scripts/verify_findings.py` (pandas version of the DAX rules; the README Findings section quotes its output)
- Clean data: `python3 scripts/clean_permits.py` — reads `data/raw/Building_Permits_20261106.csv`, writes `data/processed/building_permits_clean.csv` (paths are hardcoded relative to repo root).

## Conventions
- Data cleaning uses only pandas and numpy.
- The README embeds the full contents of `scripts/profile_permits.py`, `scripts/clean_permits.py`, `scripts/verify_findings.py` and `dax/measures.dax`. When you change one of those files, update the matching code block in `README.md`.
- `data/raw` and `data/processed` are git-ignored (CSV ~330 MB / 148 MB). Never commit data.
- DAX column references in `dax/measures.dax` must match the cleaned column names (`KEEP` in `clean_permits.py`); the model uses a `Permits` table and a `Calendar` table (active relationship on AppliedDate, inactive on IssuedDate).
- `calgary_permits.pbix` and `images/` (five page screenshots) are committed; the README Share section embeds the images. After changing the report, re-export the screenshots and replace the `.pbix` (each version adds ~35 MB to git history, so commit it sparingly).
- The cleaned file intentionally excludes `ApplicantName`, `ContractorName`, `Description` and `OriginalAddress` (personal/company details; the licence excludes personal information). Do not add them back, and do not commit raw data.
