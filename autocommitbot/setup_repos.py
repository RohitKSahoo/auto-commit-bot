import json
import os
import requests
import subprocess
import questionary
import random

from autocommitbot.scheduler import create_startup_task
from autocommitbot.gh_auth import require_gh_auth, get_user_repos, setup_git_credentials

from autocommitbot.paths import CONFIG_FILE


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
    """Check if GitHub authentication works for a repo.
    
    Uses a hard 10-second timeout so a missing credential prompt
    can never block setup indefinitely.
    """
    try:
        result = subprocess.run(
            ["git", "ls-remote"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,   # prevents interactive credential prompts
            timeout=10                  # never hang longer than 10 s
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
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

    # ---------------------------------------------------------
    # Initial Check: Partial vs Full Setup
    # ---------------------------------------------------------
    # A user is considered "already set up" only when the config file exists
    # AND contains a non-empty repositories list.  An empty {} file (the
    # package default) or a file missing "repositories" always triggers the
    # full first-run wizard.
    current_config: dict = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                current_config = json.load(f)
            except Exception:
                current_config = {}

    is_partial = bool(current_config.get("repositories"))

    # Initialise wizard variables
    username = ""
    repos = []
    selected_repos = []
    base_path = ""

    choice_map = {
        "Update Repositories & Base Folder": 1,
        "Update Automation Schedule": 4,
        "Update AI Settings (Gemini API)": 5,
        "Run Full Re-Setup": 1
    }

    if is_partial:
        # Pre-fill state from existing config
        schedule_type = current_config.get("schedule_type", "onlogon")
        schedule_time = current_config.get("schedule_time")
        use_ai = current_config.get("use_ai", False)
        gemini_key = current_config.get("gemini_key", "")
        step = 0  # Returning user — show the mode-selection menu
    else:
        step = 1  # First run — go straight through the full wizard
        # Initialize defaults so they are always defined before step 6 uses them
        schedule_type = "onlogon"
        schedule_time = None
        use_ai = False
        gemini_key = ""

    while True:

        # ── Step 0: Mode-selection menu (partial re-config only) ──────────────
        if step == 0:
            mode = questionary.select(
                "AutoCommitBot is already configured. What would you like to do?",
                choices=list(choice_map.keys()) + ["Exit"],
                style=custom_style
            ).ask()

            if not mode or mode == "Exit":
                return

            is_partial = mode != "Run Full Re-Setup"
            step = choice_map[mode]

            # If full re-setup is chosen, reset is_partial flag
            if not is_partial:
                # Reset volatile state so full wizard starts clean
                username = ""
                repos = []
                selected_repos = []
                base_path = ""
                schedule_type = "onlogon"
                schedule_time = None
                use_ai = False
                gemini_key = ""
            continue

        # ── Step 1: Verify GitHub identity via gh CLI & fetch repos ─────────
        elif step == 1:
            # require_gh_auth() exits the process with a friendly message if
            # gh is missing or the user is not authenticated — no manual input.
            username = require_gh_auth()
            
            # Setup Git credentials immediately after GH auth
            step = 1.5
            continue
            raw_repos = get_user_repos(username)

            # Normalise to the shape the rest of setup expects:
            # a list of dicts with at least a "name" key.
            repos = raw_repos  # already [{"name": ..., "url": ..., "visibility": ...}]

            if not repos:
                console.print(
                    "[yellow]No repositories found for your account.[/yellow]\n"
                    "Create at least one repo on GitHub, then re-run setup."
                )
                return

            step = 2

        # ── Step 1.5: Setup Git Credentials ──────────────────────────────────
        elif step == 1.5:
            console.print("[dim]Configuring Git to use GitHub CLI for authentication...[/dim]")
            if setup_git_credentials():
                console.print("[green]✔ Git credentials configured.[/green]")
            else:
                console.print("[yellow]⚠ Could not automatically configure Git credentials.[/yellow]")
            step = 2

        # ── Step 2: Repo selection ────────────────────────────────────────────
        elif step == 2:
            console.print("\n[bold cyan]Navigation Instructions:[/bold cyan]")
            console.print("  [bold yellow]↑/↓[/bold yellow]     : Move cursor up and down")
            console.print("  [bold green]Space[/bold green]   : Select or deselect a repository")
            console.print("  [bold magenta]Enter[/bold magenta]   : Confirm your final selection\n")

            back_label_2 = "← Back to menu" if is_partial else "<-- Go Back"
            
            # Pre-select repositories already in the config
            current_repos = current_config.get("repositories", [])
            existing_names = [os.path.basename(os.path.normpath(r)) for r in current_repos]
            
            choices = [back_label_2]
            for repo in repos:
                name = repo["name"]
                choices.append(questionary.Choice(
                    title=name,
                    checked=name in existing_names
                ))

            ans = questionary.checkbox(
                "Select repositories to automate:",
                choices=choices,
                qmark="?",
                instruction=" ",
                style=custom_style
            ).ask()

            if not ans:
                print("No repositories selected.")
                continue

            if back_label_2 in ans:
                step = 0 if is_partial else 1
                continue

            selected_repos = ans
            step = 3

        # ── Step 3: Base folder ───────────────────────────────────────────────
        elif step == 3:
            # Try to infer base path from existing repos if available
            default_base = ""
            current_repos = current_config.get("repositories", [])
            if current_repos:
                default_base = os.path.dirname(os.path.normpath(current_repos[0]))

            prompt = f"\nEnter the base folder"
            if default_base:
                prompt += f" [default: {default_base}]"
            prompt += " (example: D:\\Projects) or 'b' to go back: "
            
            ans = input(prompt).strip()
            
            if ans.lower() == 'b':
                step = 2
                continue
            
            if not ans:
                if default_base:
                    ans = default_base
                else:
                    continue
            
            base_path = ans
            
            # CRITICAL FIX: If we are just updating repos (is_partial), 
            # we should skip to step 6 (cloning/saving) instead of going 
            # to step 4 (schedule) which would break without saving.
            if is_partial:
                step = 6
            else:
                step = 4  # Proceed to schedule selection for full setup

        # ── Step 4: Schedule ──────────────────────────────────────────────────
        elif step == 4:
            console.print("\n[bold cyan]Schedule Selection:[/bold cyan]")
            console.print("  [bold yellow]↑/↓[/bold yellow]     : Move cursor up and down")
            console.print("  [bold magenta]Enter[/bold magenta]   : Confirm your schedule option\n")

            back_label = "← Back to menu" if is_partial else "<-- Go Back"
            ans = questionary.select(
                "When do you want AutoCommitBot to run automatically?",
                choices=[
                    "When I log in to my system (ONLOGON)",
                    "At a specific time of day",
                    "At a random time (daily)",
                    "On random days & times (Natural activity)",
                    back_label,
                ],
                qmark="?",
                instruction=" ",
                style=custom_style
            ).ask()

            if not ans or ans == back_label:
                step = 0 if is_partial else 3
                continue

            schedule_choice = ans

            if schedule_choice == "At a specific time of day":
                st = questionary.text(
                    "Enter the time (24-hour format HH:MM, e.g. 14:30):",
                    validate=lambda x: (len(x) == 5 and x[2] == ':' and x[:2].isdigit() and x[3:].isdigit() and int(x[:2]) < 24 and int(x[3:]) < 60)
                ).ask()
                if not st:
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
            else:
                schedule_type = "onlogon"
                schedule_time = None

            # Confirmation
            summary = schedule_choice
            if schedule_type == "time" and schedule_time:
                summary = f"{schedule_choice} → {schedule_time}"
            console.print(f"\n[dim]Selected schedule:[/dim] [bold green]{summary}[/bold green]")

            confirm = questionary.select(
                "Confirm this schedule?",
                choices=["✔ Yes, confirm", "✘ Go back and choose again"],
                qmark="?",
                instruction=" ",
                style=custom_style
            ).ask()

            if not confirm or "Go back" in confirm:
                continue

            if is_partial:
                current_config["schedule_type"] = schedule_type
                current_config["schedule_time"] = schedule_time
                with open(CONFIG_FILE, "w") as f:
                    json.dump(current_config, f, indent=4)
                print("\nSchedule updated. Re-applying startup task...")
                create_startup_task()
                print("Done!")
                break

            step = 5

        # ── Step 5: AI / Gemini key ───────────────────────────────────────────
        elif step == 5:
            if is_partial:
                # In partial mode, offer a back option before the yes/no confirm
                back_choice = questionary.select(
                    "Update AI commit message settings?",
                    choices=["Yes — update AI settings", "← Back to menu"],
                    style=custom_style
                ).ask()
                if not back_choice or back_choice == "← Back to menu":
                    step = 0
                    continue
                ans = True
            else:
                ans = questionary.confirm(
                    "Enable AI-generated commit messages? (Requires a free Gemini API key)",
                    default=use_ai,
                    style=custom_style
                ).ask()

            if ans:
                while True:
                    key_ans = input("\nEnter your Gemini API key (or 's' to skip/disable AI): ").strip()

                    if key_ans.lower() == 's':
                        gemini_key = ""
                        use_ai = False
                        break

                    if not key_ans:
                        continue

                    console.print("Validating API key...")
                    try:
                        test_url = f"https://generativelanguage.googleapis.com/v1/models?key={key_ans}"
                        test_response = requests.get(test_url, timeout=10)

                        if test_response.status_code == 200:
                            console.print("[green]✔ API key is functional![/green]")
                            gemini_key = key_ans
                            use_ai = True
                            break
                        else:
                            error_data = test_response.json()
                            error_msg = error_data.get("error", {}).get("message", "Unknown error")
                            console.print(f"[red]✘ API key validation failed: {error_msg}[/red]")

                            retry = questionary.select(
                                "What would you like to do?",
                                choices=["Try another key", "Skip and use generic messages"],
                                style=custom_style
                            ).ask()

                            if retry == "Skip and use generic messages":
                                gemini_key = ""
                                use_ai = False
                                break
                    except Exception as e:
                        console.print(f"[red]✘ Could not reach Gemini API: {e}[/red]")
                        retry = questionary.select(
                            "What would you like to do?",
                            choices=["Try again", "Skip and use generic messages"],
                            style=custom_style
                        ).ask()
                        if retry == "Skip and use generic messages":
                            gemini_key = ""
                            use_ai = False
                            break
            else:
                gemini_key = ""
                use_ai = False

            if is_partial:
                current_config["use_ai"] = use_ai
                current_config["gemini_key"] = gemini_key
                with open(CONFIG_FILE, "w") as f:
                    json.dump(current_config, f, indent=4)
                print("\nAI Settings updated successfully!")
                break

            step = 6

        # ── Step 6: Clone repos & finalize ────────────────────────────────────
        elif step == 6:
            if not os.path.exists(base_path):
                os.makedirs(base_path, exist_ok=True)

            repo_paths = []
            for repo in selected_repos:
                repo_path = os.path.join(base_path, repo)
                if not os.path.exists(repo_path):
                    print(f"\nCloning repository: {repo}")
                    # Use gh to clone so the authenticated session is reused
                    clone_result = subprocess.run(
                        ["gh", "repo", "clone", f"{username}/{repo}", repo_path]
                    )
                    if clone_result.returncode != 0:
                        print(f"  ✘ Failed to clone {repo}. Skipping.")
                        continue
                repo_paths.append(repo_path)

            print("\nVerification...")
            failed_repos = []
            for path in repo_paths:
                print(f"  Checking: {os.path.basename(path)}...", end=" ", flush=True)
                if check_git_auth(path):
                    print("✔ OK")
                else:
                    print("✘ Auth warning")
                    failed_repos.append(path)  # log and move on — never block here

            if failed_repos:
                print("\n⚠️  GitHub authentication check failed for:")
                for fp in failed_repos:
                    print(f"   • {fp}")
                print("Tip: run 'git push' once inside each folder above to cache your credentials.\n")
            else:
                print("All repositories authenticated successfully.\n")

            if is_partial:
                current_config["repositories"] = repo_paths
                with open(CONFIG_FILE, "w") as f:
                    json.dump(current_config, f, indent=4)
                print("\nRepositories updated successfully!")
                break

            # Full setup — save everything
            config = {
                "repositories": repo_paths,
                "schedule_type": schedule_type,
                "schedule_time": schedule_time,
                "use_ai": use_ai,
                "gemini_key": gemini_key
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)

            print("\nSetup complete! Creating startup scheduler...")
            create_startup_task()
            break