# Changelog

All notable changes to AutoCommitBot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]
- No unreleased changes

## [1.3.1] - 2026-04-11

### Added
- **Interactive Manual Runs** — Added a new interactive menu when running `autocommit run` manually. Users can now choose between scanning for real code changes or performing a quick "Heartbeat" commit.
- **Strict Background Mode** — The background task (Windows Task Scheduler) now strictly performs "Random Activity" commits only, ignoring real code changes to prevent cluttered or poorly messaged automated commits in the background.
- **Improved CLI Experience** — Integrated `questionary` into the main execution flow for a more premium interactive experience.

## [1.3.0] - 2026-03-26

### Fixed
- **Background Task Reliability** — Fixed a major issue where the bot would hang indefinitely in the Windows Task Scheduler due to stdout buffer overflows. All output is now correctly redirected to log files.
- **Git Command Timeouts** — Added global 90-second timeouts to all Git operations (status, add, commit, push, pull) to prevent background process hangs.
- **Encoding & Unicode Support** — Fixed a "charmap" crash on Windows by forcing UTF-8 mode for both Python and the Rich console. Unicode checkmarks (✔) now log correctly in background mode.
- **Task Scheduler Path Limits** — Shortened the registration command using PowerShell aliases (`-nop -w h -c`) to stay within the legacy 261-character `schtasks` limit.

### Optimized
- **Secret Shield Performance** — Drastically reduced execution time by scanning all staged changes in a single operation instead of running individual diffs per file.

### Added
- **Detailed Execution Tracing** — Added granular logging for configuration loading, repository loops, and background maintenance steps to make troubleshooting easier.

## [1.2.9] - 2026-03-21

### Added
- **Refined CLI output** — Automated updates now use a subtle, professional color theme (using the Rich library) that is much easier on the eyes.
- **Improved Secret Shield logs** — Cleaner, more decent prefixes for security actions.
- **Smart setup defaults** — The setup wizard now automatically pre-selects your currently tracked repositories and suggests your existing base folder as the default path.

### Fixed
- **Setup flow bug** — Fixed a critical issue where updating repository selections in the configuration menu would exit early after the schedule step without actually saving the new repository list.
- **Base path inference** — The setup wizard now correctly remembers and suggests your base project folder during partial re-configurations.
- **Improved repository selection UI** — Existing repositories are now correctly marked as checked in the interactive setup checklist.

### Fixed
- First-time users no longer see the returning-user menu — setup now correctly detects a "configured" state by checking for a non-empty `repositories` list in `config.json`, not just whether the file exists
- Bundled `config.json` was shipped with personal repo paths and a live Gemini API key; it is now empty `{}` so new installs start clean
- Config parsing is now done once at startup (previously the file was opened twice in the partial-setup branch)

### Security
- Removed hardcoded Gemini API key and personal repository paths that were accidentally committed inside `autocommitbot/config.json`

---

## [1.2.7] - 2026-03-20

### Added
- GitHub CLI (`gh`) authentication layer — setup now verifies your identity through your active `gh` session instead of asking for a username
- New `gh_auth.py` module with `check_gh_installed`, `check_auth_status`, `get_authenticated_user`, `get_user_repos`, and `require_gh_auth` helpers
- Repo list is now fetched via `gh repo list` (authenticated) instead of the public GitHub REST API
- Cloning now uses `gh repo clone` so existing `gh` credentials are reused automatically — no extra token setup needed

### Changed
- `autocommit setup` no longer prompts for a GitHub username — the username is resolved from the active `gh` session
- Repositories are cloned via `gh repo clone` instead of a bare `git clone https://…` URL

### Removed
- Manual GitHub username input step from the setup wizard
- Unauthenticated `requests.get` call to the public GitHub API for repo discovery

---

## [1.2.6] - 2026-03-20

### Fixed
- "What's New" section in `autocommit version` now displays correctly after `pip install` — `CHANGELOG.md` is bundled inside the package so it's available at runtime (previously it was only at the project root and silently not found)

---

## [1.2.5] - 2026-03-20

### Fixed
- `UnboundLocalError` on first-time setup — `schedule_type` and related vars now always initialised with safe defaults
- First-time setup wizard now correctly advances through all steps (schedule + AI) instead of skipping them
- Auth verification no longer hangs — `git ls-remote` has a hard 10-second timeout with `stdin` closed
- All repos are now checked during verification even if one fails — grouped error summary shown at the end


## [1.2.4] - 2026-03-20

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
