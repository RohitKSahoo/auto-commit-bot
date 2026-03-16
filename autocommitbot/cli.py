import typer
from rich.console import Console
from rich.panel import Panel
import json
import os

from autocommitbot.setup_repos import run_setup
from autocommitbot.auto_commit import run_bot
from autocommitbot.scheduler import create_startup_task

app = typer.Typer(
    help="AutoCommitBot — Automate repository maintenance commits.",
    add_completion=False
)

console = Console()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION = "1.0.1"


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold cyan]AutoCommitBot[/bold cyan]\n"
                "Automated GitHub repository activity tool.\n\n"
                "Use [bold]autocommit --help[/bold] to see available commands.",
                expand=False
            )
        )


@app.command(help="Run the repository setup wizard.")
def setup():
    console.print("[cyan]Running setup...[/cyan]")
    run_setup()


@app.command(help="Run the auto commit bot immediately.")
def run():
    console.print("[green]Starting auto commit bot...[/green]")
    run_bot()


@app.command(help="Run the bot manually without scheduler.")
def start():
    console.print("[green]Running bot manually...[/green]")
    run_bot()


@app.command(help="Disable the automatic startup scheduler.")
def disable():
    import subprocess

    console.print("[yellow]Disabling startup task...[/yellow]")

    subprocess.run(["schtasks", "/delete", "/tn", "AutoCommitBot", "/f"])

    console.print("[green]Startup task removed.[/green]")


@app.command(help="Enable automatic startup scheduler.")
def enable():
    console.print("[cyan]Creating startup scheduler...[/cyan]")
    create_startup_task()
    console.print("[green]Startup task created.[/green]")


@app.command(help="Show configured repositories.")
def status():

    config_path = os.path.join(BASE_DIR, "config.json")

    try:
        with open(config_path) as f:
            config = json.load(f)

        console.print("\n[bold]Configured repositories:[/bold]\n")

        for repo in config["repositories"]:
            console.print(f"• {repo}")

    except Exception:
        console.print("[red]No configuration found. Run 'autocommit setup' first.[/red]")


@app.command(help="Show installed CLI version.")
def version():
    console.print(f"[bold cyan]AutoCommitBot version {VERSION}[/bold cyan]")


if __name__ == "__main__":
    app()