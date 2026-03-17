import typer
from rich.console import Console
from rich.table import Table
import json
import os

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
        table.add_row("autocommit remove", "Remove a repository from the automation list")
        
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