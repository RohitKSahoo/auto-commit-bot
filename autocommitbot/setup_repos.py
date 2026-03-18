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

    from rich.console import Console
    console = Console()

    custom_style = questionary.Style([
        ('qmark', 'fg:#00ffff bold'),
        ('question', 'bold'),
        ('selected', 'fg:#00ff00 bold'),
        ('pointer', 'fg:#00ffff bold'),
        ('highlighted', 'fg:#00ffff bold'),
        ('answer', 'fg:#00ff00 bold'),
    ])

    step = 1
    username = ""
    repos = []
    selected_repos = []
    base_path = ""
    schedule_choice = ""
    schedule_type = "onlogon"
    schedule_time = None
    use_ai = False
    gemini_key = ""

    while True:
        if step == 1:
            ans = input("Enter your GitHub username (or 'q' to quit): ").strip()
            if ans.lower() == 'q': return
            if not ans: continue
            username = ans

            url = f"https://api.github.com/users/{username}/repos?per_page=100"
            response = requests.get(url)

            if response.status_code != 200:
                print("Failed to fetch repositories from GitHub.")
                continue

            repos = response.json()
            if not repos:
                print("No repositories found.")
                continue
            
            step = 2

        elif step == 2:
            console.print("\n[bold cyan]Navigation Instructions:[/bold cyan]")
            console.print("  [bold yellow]↑/↓[/bold yellow]     : Move cursor up and down")
            console.print("  [bold green]Space[/bold green]   : Select or deselect a repository")
            console.print("  [bold magenta]Enter[/bold magenta]   : Confirm your final selection\n")

            repo_names = ["<-- Go Back"] + [repo["name"] for repo in repos]

            ans = questionary.checkbox(
                "Select repositories to automate:",
                choices=repo_names,
                qmark="?",
                instruction=" ",
                style=custom_style
            ).ask()

            if not ans:
                print("No repositories selected.")
                continue

            if "<-- Go Back" in ans:
                step = 1
                continue

            selected_repos = ans
            step = 3

        elif step == 3:
            ans = input("\nEnter the base folder (example: D:\\Projects) or 'b' to go back: ").strip()
            if ans.lower() == 'b':
                step = 2
                continue
            if not ans: continue
            base_path = ans
            step = 4

        elif step == 4:
            console.print("\n[bold cyan]Schedule Selection:[/bold cyan]")
            console.print("  [bold yellow]↑/↓[/bold yellow]     : Move cursor up and down")
            console.print("  [bold magenta]Enter[/bold magenta]   : Confirm your schedule option\n")

            ans = questionary.select(
                "When do you want AutoCommitBot to run automatically?",
                choices=[
                    "<-- Go Back",
                    "When I log in to my system (ONLOGON)",
                    "At a specific time of day",
                    "At a random time (daily)",
                    "On random days & times (Natural activity)"
                ],
                qmark="?",
                instruction=" ",
                style=custom_style
            ).ask()

            if not ans or ans == "<-- Go Back":
                step = 3
                continue
            
            schedule_choice = ans
            
            if schedule_choice == "At a specific time of day":
                st = questionary.text(
                    "Enter the time (24-hour format HH:MM, e.g. 14:30) or 'b' to go back:",
                    validate=lambda x: x.lower() == 'b' or (len(x) == 5 and x[2] == ':' and x[:2].isdigit() and x[3:].isdigit() and int(x[:2]) < 24 and int(x[3:]) < 60)
                ).ask()
                
                if st.lower() == 'b':
                    continue
                
                schedule_time = st
                schedule_type = "time"
            elif schedule_choice == "At a random time (daily)":
                hh = random.randint(9, 23)
                mm = random.randint(0, 59)
                schedule_time = f"{hh:02d}:{mm:02d}"
                schedule_type = "time"
                print(f"Randomly picked {schedule_time} as your daily commit time!")
            elif schedule_choice == "On random days & times (Natural activity)":
                schedule_type = "random_day_time"
                schedule_time = None
                print(f"Natural Activity mode selected! The bot will skip days dynamically.")
            else:
                schedule_type = "onlogon"
                schedule_time = None

            step = 5

        elif step == 5:
            ans = questionary.confirm(
                "Enable AI-generated commit messages? (Requires a free Gemini API key)",
                default=False,
                style=custom_style
            ).ask()

            if ans:
                key_ans = input("Enter your Gemini API key (or 'b' to go back): ").strip()
                if key_ans.lower() == 'b':
                    step = 4
                    continue
                gemini_key = key_ans
                use_ai = True
            else:
                gemini_key = ""
                use_ai = False
                
            if ans is None:
                step = 4
                continue

            step = 6

        elif step == 6:
            if not os.path.exists(base_path):
                print("Folder does not exist. Creating it...")
                os.makedirs(base_path)

            repo_paths = []

            for repo in selected_repos:
                repo_path = os.path.join(base_path, repo)
                if os.path.exists(repo_path):
                    print(f"\nRepository already exists locally: {repo_path}")
                else:
                    print(f"\nCloning repository: {repo}")
                    clone_url = f"https://github.com/{username}/{repo}.git"
                    subprocess.run(["git", "clone", clone_url, repo_path])

                repo_paths.append(repo_path)

            print("\nChecking GitHub authentication...\n")
            auth_ok = True
            for path in repo_paths:
                if not check_git_auth(path):
                    auth_ok = False
                    break

            if not auth_ok:
                print("Git authentication not detected.\n")
                print("Please authenticate once using Git.")
                print("Example: cd into any repository and run 'git push'.\n")
                return

            print("Git authentication verified.\n")

            config = {
                "repositories": repo_paths,
                "schedule_type": schedule_type,
                "schedule_time": schedule_time,
                "use_ai": use_ai,
                "gemini_key": gemini_key
            }

            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)

            print("Setup complete.\n")
            print("Repositories configured for automation:\n")
            for path in repo_paths:
                print("-", path)

            print("\nCreating startup scheduler...")
            create_startup_task()
            break