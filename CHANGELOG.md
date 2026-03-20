# Changelog

All notable changes to AutoCommitBot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Fixed
- Auth verification during setup no longer hangs forever when a repo has missing or expired credentials — `git ls-remote` now has a hard 10-second timeout and `stdin` is closed to prevent interactive credential prompts from blocking the process
- All repos are now checked during verification even if one fails — failures are collected and shown as a grouped summary with a fix tip at the end, instead of stopping on the first bad repo

## [1.2.4] - 2025-03-20

### Added
- Smart daily limit — real code changes always push through, the 5/day cap now only applies to random activity commits
- "What's New" display — after updating, `autocommit version` shows what changed in the latest release
- CHANGELOG.md — version history now tracked in the repository for full transparency

### Changed
- Daily commit cap logic moved from global gate to random-activity-only gate, so genuine user changes are never blocked

---

## [1.2.3] - 2025-03-19

### Added
- AI Key Validation — real-time verification of Gemini API key during setup
- Secret Shield — automatic detection and exclusion of sensitive files and credentials before commit
- `autocommit clear-backups` command — bulk delete all backup snapshots with size summary
- `autocommit uninstall` command — cleanly removes scheduler task before pip uninstall
- `autocommit version` command — shows installed version and checks PyPI for updates
- `autocommit add [path]` command — track a new repo without re-running full setup
- `autocommit remove` command — stop tracking a repo interactively
- Backup expiry configuration via `autocommit config-backup <days>`
- Dashboard with last 50 commits and commit type breakdown
- Selective re-setup menu — update repos, schedule, or AI key individually

### Changed
- Commit messages are now AI-generated via Gemini with model fallback chain (2.5 Flash → 2.0 Flash → 1.5 Flash → Pro)
- Setup wizard now supports backward navigation between steps

---

## [1.2.0] - 2025-03-15

### Added
- Natural Activity Mode — probabilistic commit scheduling with 48-hour enforcement
- Randomized daily execution window (9 AM – 11 PM)
- Fixed-time daily scheduling option
- On-logon scheduling with daily commit cap
- Backup & Restore system with ZIP snapshots and force-push rollback
- Automatic `git pull` → merge → push workflow
- Push retry logic on failure

---

## [1.0.0] - 2025-03-10

### Added
- Initial release
- GitHub repository discovery via API
- Interactive multi-select repository setup
- Automatic cloning of missing repos
- Git authentication verification
- Basic commit engine with change detection
- Random activity commits when idle
- Windows Task Scheduler integration
- Internet availability check with retry
