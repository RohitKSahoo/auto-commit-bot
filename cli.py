import typer
from rich.console import Console
import subprocess
import os
import sys

app = typer.Typer()
console = Console()

# Get project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.command()
def setup():
    """Run repository setup"""
    console.print("[cyan]Running setup...[/cyan]")

    script = os.path.join(BASE_DIR, "setup_repos.py")

    subprocess.run([sys.executable, script])


@app.command()
def run():
    """Run auto commit bot"""
    console.print("[green]Starting auto commit bot...[/green]")

    script = os.path.join(BASE_DIR, "auto_commit.py")

    subprocess.run([sys.executable, script])

@app.command()
def start():
    """Run bot manually"""
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "auto_commit.py")])


@app.command()
def disable():
    subprocess.run(["schtasks", "/delete", "/tn", "AutoCommitBot", "/f"])

@app.command()
def enable():
    from scheduler import create_startup_task
    create_startup_task()

    
@app.command()
def status():
    """Show configured repositories"""

    import json

    config_path = os.path.join(BASE_DIR, "config.json")

    try:
        with open(config_path) as f:
            config = json.load(f)

        console.print("\nConfigured repositories:\n")

        for repo in config["repositories"]:
            console.print(f"• {repo}")

    except:
        console.print("[red]No configuration found. Run 'autocommit setup' first.[/red]")


if __name__ == "__main__":
    app()