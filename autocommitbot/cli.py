import typer
from rich.console import Console
import json
import os

from autocommitbot.setup_repos import run_setup
from autocommitbot.auto_commit import run_bot
from autocommitbot.scheduler import create_startup_task, remove_startup_task

app = typer.Typer(help="AutoCommitBot CLI")
console = Console()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.command()
def setup():
    """Run repository setup"""
    console.print("[cyan]Running setup...[/cyan]")
    run_setup()


@app.command()
def run():
    """Run auto commit bot immediately"""
    console.print("[green]Starting auto commit bot...[/green]")
    run_bot()


@app.command()
def start():
    """Run bot manually"""
    console.print("[green]Running bot manually...[/green]")
    run_bot()


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


if __name__ == "__main__":
    app()