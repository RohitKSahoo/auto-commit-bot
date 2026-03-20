"""
Changelog data for AutoCommitBot.
Used by the CLI 'version' command to show "What's New" after updates.
"""

# Maps each version to its user-facing release highlights.
# Keep in sync with CHANGELOG.md when releasing a new version.
CHANGELOG = {
    "1.2.4": [
        "Smart daily limit — real code changes always push, 5/day cap only applies to random activity commits",
        "\"What's New\" display — see what changed after updating the bot",
        "CHANGELOG.md — full version history now tracked in the repository",
    ],
    "1.2.3": [
        "AI Key Validation — real-time Gemini API key verification during setup",
        "Secret Shield — automatic detection and exclusion of sensitive files before commit",
        "New commands: clear-backups, uninstall, version, add, remove",
        "Backup expiry configuration via config-backup",
        "Dashboard with last 50 commits and commit type breakdown",
        "Selective re-setup menu — update repos, schedule, or AI key individually",
        "AI commit messages via Gemini with model fallback chain",
    ],
    "1.2.0": [
        "Natural Activity Mode with probabilistic scheduling",
        "Randomized daily execution window (9 AM – 11 PM)",
        "Backup & Restore system with ZIP snapshots",
        "Automatic git pull → merge → push workflow",
        "Push retry logic on failure",
    ],
    "1.0.0": [
        "Initial release — repo discovery, auto-commit, Task Scheduler integration",
    ],
}


def get_whats_new(version: str) -> list:
    """Return the list of highlights for a given version, or empty list."""
    return CHANGELOG.get(version, [])


def get_all_versions() -> list:
    """Return all known versions in descending order."""
    return sorted(CHANGELOG.keys(), key=lambda v: list(map(int, v.split("."))), reverse=True)
