import typer
from rich.console import Console
from rich.table import Table
import json
import os
import zipfile
import datetime
import subprocess

from autocommitbot.setup_repos import run_setup
from autocommitbot.auto_commit import run_bot
from autocommitbot.scheduler import create_startup_task, remove_startup_task

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
        console.print("[bold green]✔ Installation complete![/bold green]\n")
        
        console.print("[dim]==== Command Overview ====[/dim]\n")
        
        table = Table(show_header=True, header_style="bold magenta", border_style="dim")
        table.add_column("Command", style="cyan", width=25)
        table.add_column("Description", style="white")
        
        table.add_row("autocommit setup", "Run the initial wizard to select tracked repositories")
        table.add_row("autocommit run", "Immediately scan folders and commit changes right now (also 'start')")
        table.add_row("autocommit enable", "Enable automatic background commits on Windows Logon")
        table.add_row("autocommit disable", "Disable the scheduled background task completely")
        table.add_row("autocommit status", "Show the list of currently tracked repositories")
        table.add_row("autocommit add [path]", "Add a local folder to automation (default: current folder)")
        table.add_row("autocommit remove", "Remove a repository from the automation list")
        table.add_row("autocommit dashboard", "View history of all automated commits and system stats")
        table.add_row("autocommit restore", "Undo a bot commit by restoring the physical file backups")
        table.add_row("autocommit config-backup", "Configure how many days backup snapshots are kept")
        
        console.print(table)
        
        # Footer
        console.print("\n[dim]Run 'autocommit <command> --help' for details on a specific command.[/dim]\n")


@app.command()
def setup():
    """Run repository setup"""
    console.print("[cyan]Running setup...[/cyan]")
    run_setup()


@app.command()
def run():
    """Run auto commit bot immediately"""
    console.print("[green]Starting auto commit bot...[/green]")
    run_bot(force_run=True)


@app.command()
def start():
    """Run bot manually"""
    console.print("[green]Running bot manually...[/green]")
    run_bot(force_run=True)


@app.command()
def disable():
    """Disable Windows startup"""
    console.print("[yellow]Disabling AutoCommitBot startup...[/yellow]")

    remove_startup_task()

    console.print("[green]Startup task removed.[/green]")

@app.command()
def enable():
    """Enable Windows startup scheduler"""
    console.print("[cyan]Creating startup scheduler...[/cyan]")

    create_startup_task()

    console.print("[green]Startup task created.[/green]")


@app.command()
def remove():
    """Remove a repository from the configuration"""
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

    except Exception as e:
        console.print("[red]Failed to update configuration file.[/red]")


@app.command()
def add(path: str = typer.Argument(None, help="Path to the repository (defaults to current folder)")):
    """Add a local repository to the configuration"""
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
    """Show configured repositories"""

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
    """Show commit history dashboard"""
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
    """Configure snapshot backup expiration (days)"""
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
    """Restore repository files from a background sync backup snapshot"""
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

if __name__ == "__main__":
    app()