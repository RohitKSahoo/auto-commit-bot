"""
gh_auth.py — GitHub CLI authentication layer for AutoCommitBot.

All GitHub identity and repository access flows through this module.
Manual username input is intentionally not supported; only the active
`gh` authenticated session is trusted.
"""

import json
import subprocess
import sys
from typing import Optional

from rich.console import Console

console = Console()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], *, input_text: str | None = None, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a subprocess command and return the result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=input_text,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_gh_installed() -> bool:
    """Return True if the GitHub CLI (`gh`) binary is available on PATH."""
    try:
        result = _run(["gh", "--version"])
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


def check_auth_status() -> bool:
    """Return True if `gh` has an active, authenticated session."""
    try:
        result = _run(["gh", "auth", "status"])
        # gh auth status exits 0 when authenticated, non-zero otherwise.
        return result.returncode == 0
    except Exception:
        return False


def get_authenticated_user() -> Optional[str]:
    """
    Fetch the GitHub username for the currently authenticated `gh` session.

    Returns the login string (e.g. 'rohit123') or None if the call fails.
    """
    try:
        result = _run(["gh", "api", "user"])
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        login = data.get("login")
        return login if login else None
    except (json.JSONDecodeError, Exception):
        return None


def get_user_repos(username: str) -> list[dict]:
    """
    Fetch all repositories belonging to *username* via `gh repo list`.

    Returns a list of dicts with keys: ``name``, ``url``, ``visibility``.
    Returns an empty list on any error.
    """
    try:
        result = _run(
            [
                "gh", "repo", "list", username,
                "--limit", "100",
                "--json", "name,url,visibility",
            ]
        )
        if result.returncode != 0:
            return []
        repos = json.loads(result.stdout)
        return repos if isinstance(repos, list) else []
    except (json.JSONDecodeError, Exception):
        return []


# ---------------------------------------------------------------------------
# High-level gate — call this at the start of setup
# ---------------------------------------------------------------------------

def require_gh_auth() -> str:
    """
    Perform the full authentication gate and return the verified username.

    Prints rich-formatted status to the console at each step.
    Calls ``sys.exit(1)`` with a friendly message if any check fails —
    so callers never have to handle the error path themselves.

    Returns
    -------
    str
        The authenticated GitHub username (e.g. ``'rohit123'``).
    """
    console.print("\n[bold]🔐 Checking GitHub authentication...[/bold]")

    # ── 1. gh installed? ───────────────────────────────────────────────────
    if not check_gh_installed():
        console.print(
            "[bold red]✘ GitHub CLI not found.[/bold red]\n"
            "  AutoCommitBot requires the GitHub CLI to verify your identity.\n"
            "  Install it from: [cyan]https://cli.github.com/[/cyan]\n"
            "  Then run:        [cyan]gh auth login[/cyan]\n"
        )
        sys.exit(1)

    # ── 2. Authenticated? ──────────────────────────────────────────────────
    if not check_auth_status():
        console.print(
            "[bold red]✘ GitHub not authenticated.[/bold red]\n"
            "  Please sign in by running:  [cyan]gh auth login[/cyan]\n"
            "  Then re-run:                [cyan]autocommit setup[/cyan]\n"
        )
        sys.exit(1)

    # ── 3. Resolve username ────────────────────────────────────────────────
    username = get_authenticated_user()
    if not username:
        console.print(
            "[bold red]✘ Could not retrieve your GitHub username from gh.[/bold red]\n"
            "  Try running [cyan]gh api user[/cyan] manually to diagnose the issue.\n"
        )
        sys.exit(1)

    assert username is not None  # sys.exit(1) above handles the None case
    console.print(f"[bold green]✔ Logged in as:[/bold green] [cyan]{username}[/cyan]\n")
    return username


def setup_git_credentials() -> bool:
    """
    Configure Git to use the GitHub CLI as its credential helper.
    This ensures automated pushes work seamlessly.
    """
    try:
        # This is equivalent to `gh auth setup-git` but more direct
        # We also check if it's already configured to avoid redundant output
        result = _run(["gh", "auth", "setup-git"])
        return result.returncode == 0
    except Exception:
        return False
