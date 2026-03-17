import requests
import json
import os
import subprocess
import questionary
import random

from autocommitbot.scheduler import create_startup_task

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")


def check_git_installed():
    """Check if Git is installed"""
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except Exception:
        return False


def check_git_auth(repo_path):
    """Check if GitHub authentication works"""
    try:
        subprocess.run(
            ["git", "ls-remote"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def run_setup():
    """Main setup routine"""

    from autocommitbot.scheduler import is_admin, request_admin_and_exit
    
    if not is_admin():
        request_admin_and_exit()
        return

    print("\nAUTO COMMIT BOT SETUP\n")

    # ---------------------------------------------------------
    # Step 0: Verify git installation
    # ---------------------------------------------------------

    if not check_git_installed():
        print("Git is not installed on this system.")
        print("Install Git first: https://git-scm.com/downloads")
        return

    print("Git detected.\n")

    # ---------------------------------------------------------
    # Step 1: Get GitHub username
    # ---------------------------------------------------------

    username = input("Enter your GitHub username: ").strip()

    url = f"https://api.github.com/users/{username}/repos?per_page=100"

    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch repositories from GitHub.")
        return

    repos = response.json()

    if not repos:
        print("No repositories found.")
        return

    # ---------------------------------------------------------
    # Step 2: Select repos interactively
    # ---------------------------------------------------------

    repo_names = [repo["name"] for repo in repos]
    
    from rich.console import Console
    console = Console()
    console.print("\n[bold cyan]Navigation Instructions:[/bold cyan]")
    console.print("  [bold yellow]↑/↓[/bold yellow]     : Move cursor up and down")
    console.print("  [bold green]Space[/bold green]   : Select or deselect a repository")
    console.print("  [bold magenta]Enter[/bold magenta]   : Confirm your final selection\n")

    # Custom styling for the selector question
    custom_style = questionary.Style([
        ('qmark', 'fg:#00ffff bold'),
        ('question', 'bold'),
        ('selected', 'fg:#00ff00 bold'),
        ('pointer', 'fg:#00ffff bold'),
        ('highlighted', 'fg:#00ffff bold'),
        ('answer', 'fg:#00ff00 bold'),
    ])

    selected_repos = questionary.checkbox(
        "Select repositories to automate:",
        choices=repo_names,
        qmark="?",
        instruction=" ",
        style=custom_style
    ).ask()

    if not selected_repos:
        print("No repositories selected.")
        return

    # ---------------------------------------------------------
    # Step 4: Ask base folder
    # ---------------------------------------------------------

    base_path = input(
        "\nEnter the base folder where repositories should exist (example: D:\\Projects): "
    ).strip()

    if not os.path.exists(base_path):
        print("Folder does not exist. Creating it...")
        os.makedirs(base_path)

    repo_paths = []

    # ---------------------------------------------------------
    # Step 5: Clone or detect repos
    # ---------------------------------------------------------

    for repo in selected_repos:

        repo_path = os.path.join(base_path, repo)

        if os.path.exists(repo_path):
            print(f"\nRepository already exists locally: {repo_path}")

        else:
            print(f"\nCloning repository: {repo}")

            clone_url = f"https://github.com/{username}/{repo}.git"

            subprocess.run(["git", "clone", clone_url, repo_path])

        repo_paths.append(repo_path)

    # ---------------------------------------------------------
    # Step 6: Verify authentication
    # ---------------------------------------------------------

    print("\nChecking GitHub authentication...\n")

    auth_ok = True

    for path in repo_paths:
        if not check_git_auth(path):
            auth_ok = False
            break

    if not auth_ok:

        print("Git authentication not detected.\n")
        print("Please authenticate once using Git.\n")
        print("Example:")
        print("cd into any repository and run:")
        print("git push\n")
        print("Git will ask you to login.")
        print("After that rerun this setup.\n")

        return

    print("Git authentication verified.\n")

    # ---------------------------------------------------------
    # Step 7: Select Schedule
    # ---------------------------------------------------------

    console.print("\n[bold cyan]Schedule Selection:[/bold cyan]")
    console.print("  [bold yellow]↑/↓[/bold yellow]     : Move cursor up and down")
    console.print("  [bold magenta]Enter[/bold magenta]   : Confirm your schedule option\n")

    schedule_choice = questionary.select(
        "When do you want AutoCommitBot to run automatically?",
        choices=[
            "When I log in to my system (ONLOGON)",
            "At a specific time of day",
            "At a random time (daily)"
        ],
        qmark="?",
        instruction=" ",
        style=custom_style
    ).ask()

    schedule_type = "onlogon"
    schedule_time = None

    if schedule_choice == "At a specific time of day":
        schedule_time = questionary.text(
            "Enter the time (24-hour format HH:MM, e.g. 14:30):",
            validate=lambda x: len(x) == 5 and x[2] == ':' and x[:2].isdigit() and x[3:].isdigit() and int(x[:2]) < 24 and int(x[3:]) < 60
        ).ask()
        schedule_type = "time"
    elif schedule_choice == "At a random time (daily)":
        hh = random.randint(9, 23)
        mm = random.randint(0, 59)
        schedule_time = f"{hh:02d}:{mm:02d}"
        schedule_type = "time"
        print(f"Randomly picked {schedule_time} as your daily commit time!")

    # ---------------------------------------------------------
    # Step 8: Save configuration
    # ---------------------------------------------------------

    config = {
        "repositories": repo_paths,
        "schedule_type": schedule_type,
        "schedule_time": schedule_time
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    # ---------------------------------------------------------
    # Final Output
    # ---------------------------------------------------------

    print("Setup complete.\n")

    print("Repositories configured for automation:\n")

    for path in repo_paths:
        print("-", path)

    print("\nCreating startup scheduler...")
    create_startup_task()