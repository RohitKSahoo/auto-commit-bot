import typer
from rich.console import Console
from rich.table import Table
import json
import os
import sys
import zipfile
import shutil
import subprocess
import requests
from importlib.metadata import version as get_version, PackageNotFoundError

from autocommitbot.setup_repos import run_setup
from autocommitbot.auto_commit import run_bot
from autocommitbot.scheduler import create_startup_task, remove_startup_task
import re

def get_dynamic_version():
    """Returns the live version from pyproject.toml (dev) or package metadata."""
    # 1. Try reading from pyproject.toml at the root (for development)
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        toml_path = os.path.join(root_dir, "pyproject.toml")
        if os.path.exists(toml_path):
            with open(toml_path, "r") as f:
                content = f.read()
                # Find version = "x.y.z"
                match = re.search(r'version\s*=\s*"([^"]+)"', content)
                if match:
                    return match.group(1)
    except Exception:
        pass
        
    # 2. Standard package fallback
    try:
        return get_version("autocommitbot")
    except PackageNotFoundError:
        return "1.2.9" # Absolute fallback match for current dev state

app = typer.Typer(help="AutoCommitBot CLI")
console = Console()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """AutoCommitBot CLI"""
    if ctx.invoked_subcommand is None:
        # EXACT ANSI Shadow font to match the image
        banner = r"""
 █████╗ ██╗   ██╗████████╗ ██████╗  ██████╗ ██████╗ ███╗   ███╗███╗   ███╗██╗████████╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔════╝██╔═══██╗████╗ ████║████╗ ████║██║╚══██╔══╝
███████║██║   ██║   ██║   ██║   ██║██║     ██║   ██║██╔████╔██║██╔████╔██║██║   ██║   
██╔══██║██║   ██║   ██║   ██║   ██║██║     ██║   ██║██║╚██╔╝██║██║╚██╔╝██║██║   ██║   
██║  ██║╚██████╔╝   ██║   ╚██████╔╝╚██████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║██║   ██║   
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝   ╚═╝   
                                                                                BOT"""
        console.print(f"[bold cyan]{banner}[/bold cyan]")
        console.print("                                              [bold yellow]Developed by @RohitKSahoo[/bold yellow]\n")
        _ver = get_dynamic_version()
        console.print(f"[bold green]✔ Installation complete!  v{_ver}[/bold green]\n")

        console.print("[dim]  All commands follow:[/dim]  [bold cyan]autocommit [cyan]<command>[/cyan]\n")

        table = Table(
            show_header=True,
            header_style="bold magenta",
            border_style="dim",
            show_lines=False,
            padding=(0, 2),
            expand=False
        )
        table.add_column("Command", style="bold cyan", no_wrap=True, min_width=18)
        table.add_column("What it does", style="white", min_width=40)

        # Setup & Config
        table.add_row("[dim]  \u2500\u2500\u2500 Setup & Config[/dim]", "")
        table.add_row("  setup",          "First-time wizard, or edit repos / schedule / AI")
        table.add_row("  config-backup",  "Set how long backups are kept", end_section=True)

        # Repositories
        table.add_row("[dim]  \u2500\u2500\u2500 Repositories[/dim]", "")
        table.add_row("  add [path]",     "Track a new local git repo")
        table.add_row("  remove",         "Stop tracking a repo")
        table.add_row("  status",         "List all tracked repos", end_section=True)

        # Automation
        table.add_row("[dim]  \u2500\u2500\u2500 Automation[/dim]", "")
        table.add_row("  run",            "Commit & push all changes now")
        table.add_row("  enable",         "Register the Windows auto-start task")
        table.add_row("  disable",        "Remove the Windows auto-start task", end_section=True)

        # History & System
        table.add_row("[dim]  \u2500\u2500\u2500 History & System[/dim]", "")
        table.add_row("  dashboard",      "View commit history & stats")
        table.add_row("  restore",        "Roll back a bot commit from snapshot")
        table.add_row("  clear-backups",  "Delete all backup snapshots to free disk space")
        table.add_row("  version",        "Check installed version & updates")
        table.add_row("  uninstall",      "Remove scheduler task then pip uninstall")

        console.print(table)

        # Footer
        console.print("\n[dim]  Run [/dim][cyan]autocommit <command> --help[/cyan][dim] for full details on any command.[/dim]\n")


@app.command()
def setup():
    """Run the setup wizard — first-time or selective re-configuration.

    First run: walks through all steps (GitHub username, repo selection,
    base folder, schedule, and optional Gemini AI key).

    Subsequent runs: shows a menu to update just one section —
    Repositories, Automation Schedule, or AI Settings — without
    repeating unrelated steps.
    """
    console.print("[cyan]Running setup...[/cyan]")
    run_setup()


@app.command()
def run():
    """Scan all tracked repos and commit any pending changes immediately.

    Stages, commits, and pushes changes in all tracked repositories right now.
    Skips the schedule — useful for testing or forcing an immediate commit.
    Also available as: autocommit start
    """
    console.print("[green]Starting auto commit bot...[/green]")
    run_bot(force_run=True)


@app.command()
def start():
    """Alias for 'run' — commit & push all tracked repos immediately."""
    console.print("[green]Running bot manually...[/green]")
    run_bot(force_run=True)


@app.command()
def disable():
    """Remove the AutoCommitBot task from Windows Task Scheduler.

    Stops all automated background commits. The bot will no longer run
    automatically on logon or on a schedule. Your config and repos are
    untouched. Run 'autocommit enable' to re-register the task.
    """
    from autocommitbot.scheduler import is_admin, request_admin_and_exit
    if not is_admin():
        request_admin_and_exit()

    console.print("[yellow]Disabling AutoCommitBot startup...[/yellow]")

    remove_startup_task()

    console.print("[green]Startup task removed.[/green]")

@app.command()
def enable():
    """Register the AutoCommitBot task in Windows Task Scheduler.

    Uses the schedule type saved in your config (logon / daily time /
    natural activity). Run 'autocommit set-schedule' first if you want
    to change when it triggers.
    """
    from autocommitbot.scheduler import is_admin, request_admin_and_exit
    if not is_admin():
        request_admin_and_exit()

    console.print("[cyan]Creating startup scheduler...[/cyan]")

    create_startup_task()

    console.print("[green]Startup task created.[/green]")




@app.command()
def remove():
    """Stop tracking a repository — removes it from automation.

    Presents a numbered list of tracked repos and lets you pick one to remove.
    Does NOT delete the repo's files from disk.
    """
    config_path = os.path.join(BASE_DIR, "config.json")

    if not os.path.exists(config_path):
        console.print("[red]No configuration found. Run 'autocommit setup' first.[/red]")
        return

    try:
        with open(config_path) as f:
            config = json.load(f)

        repos = config.get("repositories", [])

        if not repos:
            console.print("[yellow]No repositories configured to remove.[/yellow]")
            return

        console.print("\n[bold]Select a repository to remove:[/bold]\n")

        for i, repo in enumerate(repos):
            console.print(f"{i+1}. {repo}")

        import builtins
        selection = builtins.input("\nEnter the number to remove (or 'q' to cancel): ").strip()

        if selection.lower() == 'q':
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        try:
            index = int(selection) - 1
            if index < 0 or index >= len(repos):
                console.print("[red]Invalid selection number.[/red]")
                return

            removed = repos.pop(index)

            config["repositories"] = repos
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)

            console.print(f"[green]Successfully removed:[/green] {removed}")

        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")

    except Exception:
        console.print("[red]Failed to update configuration file.[/red]")


@app.command()
def add(path: str = typer.Argument(None, help="Path to the repository (defaults to current folder)")):
    """Start tracking a local git repository.

    Validates that the folder exists and contains a .git directory, then
    adds it to the automation list. Defaults to the current working directory
    if no path is given. Also checks that git push authentication works.
    """
    if path is None:
        target_path = os.getcwd()
    else:
        target_path = os.path.abspath(path)

    if not os.path.isdir(target_path):
        console.print(f"[red]Error: '{target_path}' is not a valid directory.[/red]")
        return

    if not os.path.isdir(os.path.join(target_path, ".git")):
        console.print(f"[red]Error: '{target_path}' does not appear to be a Git repository (no .git folder).[/red]")
        return

    config_path = os.path.join(BASE_DIR, "config.json")
    
    # Load or initialize config
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        # Fallback if someone tries to add before setup
        console.print("[yellow]No config found. Creating new configuration...[/yellow]")
        config = {
            "repositories": [],
            "schedule_type": "onlogon",
            "schedule_time": None,
            "use_ai": False,
            "gemini_key": ""
        }

    repos = config.get("repositories", [])
    
    # Normalize paths for comparison
    norm_target = os.path.normpath(target_path)
    if any(os.path.normpath(r) == norm_target for r in repos):
        console.print(f"[yellow]'{target_path}' is already being tracked.[/yellow]")
        return

    repos.append(target_path)
    config["repositories"] = repos

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    console.print(f"[green]✔ Successfully added repo:[/green] {target_path}")
    
    # Check auth as a helper
    from autocommitbot.setup_repos import check_git_auth
    if not check_git_auth(target_path):
        console.print("[yellow]Warning: This repo might need authentication. Try running 'git push' manually once.[/yellow]")



@app.command()
def status():
    """Show all repositories currently being tracked by the bot."""

    config_path = os.path.join(BASE_DIR, "config.json")

    if not os.path.exists(config_path):
        console.print("[red]No configuration found. Run 'autocommit setup' first.[/red]")
        return

    try:
        with open(config_path) as f:
            config = json.load(f)

        repos = config.get("repositories", [])

        if not repos:
            console.print("[yellow]No repositories configured.[/yellow]")
            return

        console.print("\n[bold]Configured repositories:[/bold]\n")

        for repo in repos:
            console.print(f"• {repo}")

    except Exception:
        console.print("[red]Failed to read configuration file.[/red]")


@app.command()
def dashboard():
    """Display a rich table of the last 50 automated commits.

    Shows timestamp, repository name, commit type (User Changes vs Random
    Activity), and the commit message. Also prints a summary of total
    commits broken down by type.
    """
    history_path = os.path.join(BASE_DIR, "history.json")
    
    if not os.path.exists(history_path):
        console.print("[yellow]No commit history found yet. The bot hasn't made any commits.[/yellow]")
        return
        
    try:
        with open(history_path, "r") as f:
            history = json.load(f)
    except Exception:
        console.print("[red]Failed to read history file.[/red]")
        return
        
    if not history:
        console.print("[yellow]Commit history is empty.[/yellow]")
        return
        
    console.print("\n[bold cyan]AutoCommitBot - Commit Dashboard[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta", border_style="dim")
    table.add_column("Date & Time", style="cyan", width=20)
    table.add_column("Repository", style="green", width=25)
    table.add_column("Commit Type", style="yellow", width=20)
    table.add_column("Message", style="white")
    
    history_copy = history.copy()
    history_copy.reverse()
    
    for entry in history_copy[:50]:
        table.add_row(
            entry.get("timestamp", "N/A"),
            entry.get("repo", "Unknown"),
            entry.get("type", "Unknown"),
            entry.get("message", "N/A")
        )
        
    console.print(table)
    
    total_commits = len(history)
    random_count = sum(1 for e in history if e.get("type") == "Random Activity")
    user_count = total_commits - random_count
    
    console.print(f"\n[dim]Total Automated Commits: {total_commits} ({user_count} User Changes, {random_count} Random Activities)[/dim]\n")


@app.command()
def config_backup(days: int = typer.Argument(..., help="Number of days to keep backup snapshots")):
    """Set how long pre-commit backup snapshots are kept before auto-deletion.

    Example: autocommit config-backup 14
    This keeps all snapshots for 14 days, after which they are deleted
    automatically the next time the bot runs.
    """
    config_path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
        
    config["backup_expiry_days"] = days
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
        
    console.print(f"[green]✔ Successfully updated backups to expire after {days} days.[/green]")


@app.command()
def restore():
    """Roll back a bot commit by restoring a pre-commit file snapshot.

    Lists available backup snapshots (ZIP files saved before each commit).
    After you pick one, files are restored locally AND a force-push rolls
    back the remote GitHub repo to that state too.
    
    Note: uses 'git push --force' which rewrites remote history.
    """
    history_path = os.path.join(BASE_DIR, "history.json")
    
    if not os.path.exists(history_path):
        console.print("[yellow]No commit history found.[/yellow]")
        return
        
    with open(history_path, "r") as f:
        history = json.load(f)
        
    snapshots = [entry for entry in history if "snapshot" in entry and os.path.exists(os.path.join(BASE_DIR, "backups", entry["snapshot"]))]
    
    if not snapshots:
        console.print("[yellow]No physical backup snapshots are currently available to restore.[/yellow]")
        return
        
    console.print("\n[bold cyan]Available Backup Snapshots for Restore:[/bold cyan]\n")
    
    snapshots.reverse()
    
    for i, s in enumerate(snapshots[:20]):
        console.print(f"[{i+1}] {s['timestamp']} - {s['repo']} - {s['message']} (Closes: {s.get('expiry', 'Never')})")
        
    try:
        import builtins
        selection = builtins.input("\nEnter the number to restore (or 'q' to cancel): ").strip()
    except EOFError:
        return
        
    if selection.lower() == 'q':
        return
        
    try:
        index = int(selection) - 1
        if index < 0 or index >= len(snapshots):
            console.print("[red]Invalid selection.[/red]")
            return
            
        selected = snapshots[index]
        snap_path = os.path.join(BASE_DIR, "backups", selected["snapshot"])
        
        config_path = os.path.join(BASE_DIR, "config.json")
        with open(config_path, "r") as f:
            repos = json.load(f).get("repositories", [])
            
        repo_path = next((r for r in repos if os.path.basename(os.path.normpath(r)) == selected["repo"]), None)
        
        if not repo_path or not os.path.exists(repo_path):
            console.print("[red]Could not locate the original repository mapping on disk.[/red]")
            return
            
        console.print(f"\n[yellow]Restoring files to {repo_path}...[/yellow]")
        
        with zipfile.ZipFile(snap_path, 'r') as zipf:
            zipf.extractall(repo_path)
            
        console.print("[green]✔ Files successfully restored from snapshot![/green]")
        
        # New Universal Undo: Automatically sync the restore to GitHub
        console.print("[yellow]Syncing restored state to GitHub...[/yellow]")
        os.chdir(repo_path)
        subprocess.run(["git", "add", "."], capture_output=True)
        undo_msg = f"Undo/Restore to snapshot from {selected['timestamp']}"
        subprocess.run(["git", "commit", "-m", undo_msg], capture_output=True)
        
        push_res = subprocess.run(["git", "push", "--force"], capture_output=True, text=True)
        
        if push_res.returncode == 0:
            console.print("[bold green]✔ SUCCESS![/bold green] Your repository (local and GitHub) has been rolled back.")
        else:
            console.print(f"[red]Restored locally, but GitHub push failed: {push_res.stderr.strip()}[/red]")
            console.print("[dim]You may need to manually 'git push --force' if your branch is protected.[/dim]")

    except ValueError:
        console.print("[red]Invalid input.[/red]")


@app.command()
def clear_backups():
    """Delete all backup snapshots to free disk space.

    Removes every ZIP snapshot stored in the backups folder and clears the
    corresponding snapshot references from commit history. Commit history
    entries themselves are preserved — only their snapshot links are removed.

    Useful when backup files are consuming too much disk space.
    """
    backup_dir = os.path.join(BASE_DIR, "backups")

    if not os.path.isdir(backup_dir):
        console.print("[yellow]No backups directory found. Nothing to clear.[/yellow]")
        return

    zip_files = [f for f in os.listdir(backup_dir) if f.endswith(".zip")]

    if not zip_files:
        console.print("[yellow]Backups folder is already empty.[/yellow]")
        return

    # Calculate total size
    total_bytes = sum(
        os.path.getsize(os.path.join(backup_dir, f)) for f in zip_files
    )

    def _fmt_size(b: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"

    console.print(f"\n[bold cyan]Backup Cleanup[/bold cyan]")
    console.print(f"  Snapshots found : [yellow]{len(zip_files)}[/yellow]")
    console.print(f"  Total size      : [yellow]{_fmt_size(total_bytes)}[/yellow]\n")

    import builtins
    confirm = builtins.input("Delete all backup snapshots? (yes/N): ").strip().lower()
    if confirm != "yes":
        console.print("[yellow]Operation cancelled.[/yellow]")
        return

    # Delete every ZIP file
    deleted = 0
    for f in zip_files:
        try:
            os.remove(os.path.join(backup_dir, f))
            deleted += 1
        except Exception as e:
            console.print(f"[red]Failed to delete {f}: {e}[/red]")

    # Clean snapshot references from history.json
    history_path = os.path.join(BASE_DIR, "history.json")
    if os.path.exists(history_path):
        try:
            with open(history_path, "r") as f:
                history = json.load(f)

            changed = False
            for entry in history:
                if "snapshot" in entry:
                    del entry["snapshot"]
                    changed = True
                if "expiry" in entry:
                    del entry["expiry"]
                    changed = True

            if changed:
                with open(history_path, "w") as f:
                    json.dump(history, f, indent=4)
        except Exception:
            pass

    console.print(f"\n[bold green]✔ Cleared {deleted}/{len(zip_files)} backup snapshots ({_fmt_size(total_bytes)} freed).[/bold green]")
    console.print("[dim]Commit history entries are preserved — only snapshot files were removed.[/dim]\n")



@app.command()
def uninstall():
    """Cleanly remove AutoCommitBot — scheduler task + pip package.

    Step 1: Deletes the 'AutoCommitBot' task from Windows Task Scheduler
    so it stops running automatically (requires Admin privileges).

    Step 2: Runs 'pip uninstall autocommitbot -y' to remove the package.

    Your cloned git repositories and their files are NOT deleted.
    Always prefer this over running 'pip uninstall' directly.
    """
    from autocommitbot.scheduler import is_admin, request_admin_and_exit
    if not is_admin():
        request_admin_and_exit()

    console.print("[bold red]\n⚠ AutoCommitBot Uninstall[/bold red]\n")
    console.print("This will:")
    console.print("  [yellow]1.[/yellow] Remove the AutoCommitBot task from Windows Task Scheduler")
    console.print("  [yellow]2.[/yellow] Uninstall the autocommitbot package via pip\n")

    import builtins
    confirm = builtins.input("Are you sure you want to uninstall? (yes/N): ").strip().lower()
    if confirm != "yes":
        console.print("[yellow]Uninstall cancelled.[/yellow]")
        return

    # Step 1: Remove the scheduler task
    console.print("\n[cyan]Step 1: Removing Task Scheduler entry...[/cyan]")
    try:
        remove_startup_task()
        console.print("[green]✔ Scheduler task removed.[/green]")
    except Exception as e:
        console.print(f"[red]Could not remove scheduler task: {e}[/red]")
        console.print("[dim]You can remove it manually: open Task Scheduler and delete 'AutoCommitBot'.[/dim]")

    # Step 2: Uninstall the package
    console.print("\n[cyan]Step 2: Uninstalling autocommitbot package...[/cyan]")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "autocommitbot", "-y"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        console.print("[bold green]✔ autocommitbot successfully uninstalled.[/bold green]")
        console.print("[dim]Your cloned repositories and their files have NOT been deleted.[/dim]")
    else:
        console.print(f"[red]pip uninstall failed:[/red] {result.stderr.strip()}")


@app.command()
def version():
    """Show the installed version and check PyPI for available updates.

    Compares your installed version against the latest release on PyPI.
    If a newer version is available, prints the pip upgrade command along
    with a summary of what's new in that release.

    Requires an internet connection to check for updates.
    """
    from autocommitbot.changelog import get_whats_new

    installed = get_dynamic_version()

    console.print(f"\n[bold cyan]AutoCommitBot[/bold cyan]  v{installed}")

    # Check PyPI for the latest version
    console.print("[dim]Checking for updates...[/dim]")
    try:
        response = requests.get(
            "https://pypi.org/pypi/autocommitbot/json",
            timeout=5
        )
        if response.status_code == 200:
            latest = response.json()["info"]["version"]
            if latest == installed:
                console.print(f"[green]✔ You are on the latest version ({installed}).[/green]")

                # Show what's new in the current version
                highlights = get_whats_new(installed)
                if highlights:
                    console.print(f"\n[bold magenta]🎉 New in this version (v{installed}):[/bold magenta]")
                    for item in highlights:
                        console.print(f"  [dim]•[/dim] {item}")
                console.print()
            else:
                console.print(f"[yellow]⚡ New version available: [bold]{latest}[/bold] (you have {installed})[/yellow]")

                # Show what's new in the available version
                highlights = get_whats_new(latest)
                if highlights:
                    console.print(f"\n[bold magenta]📋 What's New in v{latest}:[/bold magenta]")
                    for item in highlights:
                        console.print(f"  [dim]•[/dim] {item}")

                console.print(f"\n[dim]Run to update:[/dim]  [bold cyan]pip install --upgrade autocommitbot[/bold cyan]\n")
        else:
            console.print("[dim]Could not reach PyPI to check for updates.[/dim]\n")
    except Exception:
        console.print("[dim]Could not reach PyPI to check for updates.[/dim]\n")


if __name__ == "__main__":
    app()