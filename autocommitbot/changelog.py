"""
Changelog parser for AutoCommitBot.
Reads CHANGELOG.md at runtime — the 'What's New' display in
`autocommit version` is always automatically in sync with the file.
No manual updates needed when releasing a new version.
"""

from __future__ import annotations

import os
import re

# CHANGELOG.md is bundled inside the package directory so it's available
# both during development and after `pip install`.
_CHANGELOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CHANGELOG.md")


def _parse_changelog() -> dict[str, list[str]]:
    """
    Parse CHANGELOG.md and return a mapping of version → list of bullet strings.

    Recognises headings like:
        ## [1.2.5] - 2026-03-20
    and collects every bullet line (starting with '- ') underneath until the
    next version heading or end of file.  Section sub-headings (### Added,
    ### Fixed, …) are ignored — all bullets for a version are flattened into
    one list.
    """
    result: dict[str, list[str]] = {}

    try:
        with open(_CHANGELOG_PATH, encoding="utf-8") as fh:
            lines = fh.readlines()
    except FileNotFoundError:
        return result

    version_heading = re.compile(r"^##\s+\[(\d+\.\d+[\.\d]*)\]")
    current_version: str | None = None

    for line in lines:
        line = line.rstrip("\n\r")

        match = version_heading.match(line)
        if match:
            current_version = match.group(1)
            result.setdefault(current_version, [])
            continue

        if current_version and line.lstrip().startswith("- "):
            # Strip the leading "- " and any extra whitespace
            bullet = line.lstrip()[2:].strip()
            if bullet:
                result[current_version].append(bullet)

    return result


# Module-level cache so the file is only read once per process
_CACHE: dict[str, list[str]] | None = None


def _get_cache() -> dict[str, list[str]]:
    global _CACHE
    if _CACHE is None:
        _CACHE = _parse_changelog()
    return _CACHE


def get_whats_new(version: str) -> list[str]:
    """Return the list of change highlights for *version*, or an empty list."""
    return _get_cache().get(version, [])


def get_all_versions() -> list[str]:
    """Return all known versions in descending order."""
    return sorted(
        _get_cache().keys(),
        key=lambda v: list(map(int, v.split("."))),
        reverse=True,
    )
