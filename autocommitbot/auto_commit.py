import os
import subprocess
import time
import datetime
import socket
import json
import random
import zipfile
import requests
import re
from rich.console import Console

console = Console()



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
SAFE_FILE = ".dev_activity_log"


HISTORY_FILE = os.path.join(BASE_DIR, "history.json")


def cleanup_expired_snapshots():
    try:
        if not os.path.exists(HISTORY_FILE):
            return
            
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
            
        changed = False
        now = datetime.datetime.now()
        
        for entry in history:
            if "snapshot" in entry and entry.get("expiry"):
                expiry_dt = datetime.datetime.strptime(entry["expiry"], "%Y-%m-%d %H:%M:%S")
                if now > expiry_dt:
                    snap_path = os.path.join(BASE_DIR, "backups", entry["snapshot"])
                    if os.path.exists(snap_path):
                        os.remove(snap_path)
                    del entry["snapshot"]
                    del entry["expiry"]
                    changed = True
                    
        if changed:
            with open(HISTORY_FILE, "w") as f:
                json.dump(history, f, indent=4)
    except Exception:
        pass


def take_snapshot(repo_path):
    try:
        tracked = subprocess.run(["git", "ls-files"], cwd=repo_path, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=repo_path, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        
        all_files = tracked.stdout.splitlines() + untracked.stdout.splitlines()
        
        if not all_files:
            return None
            
        repo_name = os.path.basename(os.path.abspath(repo_path))
        snapshot_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"{repo_name}_{snapshot_id}.zip"
        
        backup_dir = os.path.join(BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        zip_path = os.path.join(backup_dir, zip_name)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in all_files:
                abs_file = os.path.join(repo_path, file)
                if os.path.isfile(abs_file):
                    zipf.write(abs_file, file)
                    
        return zip_name
    except Exception as e:
        console.print(f"[bold red]Snapshot failed:[/bold red] {e}")
        return None


def log_commit(repo_path, message, is_random, snapshot_file=None):
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []
    except Exception:
        history = []

    repo_name = os.path.basename(os.path.normpath(repo_path))
    entry = {
        "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "repo": repo_name,
        "message": message,
        "type": "Random Activity" if is_random else "User Changes"
    }
    
    if snapshot_file:
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            expiry_days = config.get("backup_expiry_days", 7)
        except Exception:
            expiry_days = 7
            
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=expiry_days)
        entry["snapshot"] = snapshot_file
        entry["expiry"] = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
    
    history.append(entry)
    
    if len(history) > 500:
        history = history[-500:]  # type: ignore
        
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
    except Exception:
        pass


commit_messages = [
    "development log update",
    "system maintenance update",
    "repository activity update",
    "background environment sync",
    "routine maintenance commit",
    "repository health update",
    "environment checkpoint",
    "minor system update",
    "automated repository maintenance",
    "development activity checkpoint",
    "internal maintenance update",
    "repository housekeeping update",
    "environment state update",
    "system activity checkpoint",
    "automated activity log update",
    "environment maintenance update",
    "repository sync operation",
]


def internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except Exception:
        return False


def wait_for_internet(max_attempts=12):
    console.print("[dim]Checking internet connection...[/dim]")

    attempts = 0

    while not internet_available():

        if attempts >= max_attempts:
            console.print("[bold red]Internet not available. Skipping run.[/bold red]")
            return False

        console.print("[yellow]Waiting for internet...[/yellow]")
        time.sleep(10)
        attempts += 1

    console.print("[bold green]✔ Internet detected[/bold green]")
    return True

# --- Secret Shield Configuration ---
SENSITIVE_FILES = [
    ".env", "secrets.json", "credentials.json", 
    "*.key", "*.pem", "*.db", "*.sqlite", 
    "config.json", "history.json", "backups/"
]
SENSITIVE_PATTERNS = [r"AIzaSy[A-Za-z0-9_-]{33}", r"sk-[A-Za-z0-9]{48}"]

def shield_sensitive_data(repo_path):
    """Safety check to prevent pushing secrets and forcefully un-track them if exposed"""
    # 1. Update .gitignore
    gitignore = os.path.join(repo_path, ".gitignore")
    existing_content = ""
    if os.path.exists(gitignore):
        with open(gitignore, "r") as f:
            existing_content = f.read()
    
    to_ignore = [f for f in SENSITIVE_FILES if f not in existing_content]
    if to_ignore:
        console.print(f"[bold blue]🛡️  [SHIELD][/bold blue] [green]SECURED:[/green] Protecting new sensitive patterns: [bold cyan]{', '.join(to_ignore)}[/bold cyan]")
        with open(gitignore, "a") as f:
            if not existing_content:
                f.write("\n# AutoCommitBot Secret Shield - Self Healing\n")
            for item in to_ignore:
                f.write(f"\n{item}")

    # 2. PROACTIVE UN-TRACKING: Check if any sensitive file is currently being tracked by Git
    # This fixes the issue where a file is in .gitignore but still exists in the repo
    try:
        # Get list of all tracked files
        tracked_process = subprocess.run(
            ["git", "ls-files"], 
            cwd=repo_path, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        tracked_files = tracked_process.stdout.splitlines()
        
        needs_untracking = False
        for s_file in SENSITIVE_FILES:
            # Check if this sensitive pattern matches any tracked file
            # (Matches exact filename or wildcards like *.key)
            cleaned_pattern = s_file.replace("*.", "")
            for t_file in tracked_files:
                if t_file == s_file or t_file.endswith(cleaned_pattern) or os.path.basename(t_file) == s_file:
                    console.print(f"[bold blue]🛡️  [SHIELD][/bold blue] [bold red]URGENT:[/bold red] '[cyan]{t_file}[/cyan]' is exposed on GitHub! Un-tracking now...")
                    subprocess.run(["git", "rm", "-r", "--cached", t_file], cwd=repo_path, capture_output=True)
                    needs_untracking = True
        
        if needs_untracking:
            subprocess.run(["git", "add", ".gitignore"], cwd=repo_path, capture_output=True)
            console.print("[bold blue]🛡️  [SHIELD][/bold blue] [bold green]✔ Exposed files have been removed from Git tracking.[/bold green]")
            console.print("[bold blue]🛡️  [SHIELD][/bold blue] [dim]They will disappear from GitHub on your next push.[/dim]")

    except Exception as e:
        console.print(f"[bold red][SHIELD ERROR] Audit failed:[/bold red] {e}")

    # 3. Key Scanning (Purely informative if found in tracked files)
    try:
        # Check staged changes
        diff = subprocess.run(
            ["git", "diff", "--cached"], 
            cwd=repo_path, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore'
        ).stdout
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, diff):
                console.print("[bold blue]🛡️  [SHIELD][/bold blue] [bold yellow]WARNING:[/bold yellow] [red]I detected an API Key pattern inside one of your files![/red]")
                console.print("[bold blue]🛡️  [SHIELD][/bold blue] [dim]I'm pushing this commit, but you should move that key to a .env file ASAP![/dim]")
    except Exception:
        pass
    
    return True # Always continue now as requested

def generate_ai_commit_message(repo_path, fallback_message, config):
    if not config.get("use_ai") or not config.get("gemini_key"):
        return fallback_message
        
    console.print("[dim]Analyzing code diff with Gemini AI...[/dim]")
    try:
        diff_process = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        diff_text = diff_process.stdout.strip()
        
        if not diff_text:
            return fallback_message
            
        if len(diff_text) > 8000:
            diff_text = diff_text[:8000] + "\n...[diff truncated]..."
            
        # Preferred models in order of priority (Newest -> Most Stable)
        preferred_models = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-pro"
        ]
        
        headers = {"Content-Type": "application/json"}
        prompt = f"Write a concise, natural, human-like 1-line git commit message for the following changes. Do not use quotes, backticks, or markdown, just the raw text of the message:\n\n{diff_text}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        success = False
        data = None
        
        for model in preferred_models:
            url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={config['gemini_key']}"
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    success = True
                    break
                elif response.status_code == 404:
                    continue # Try next model
                else:
                    # Other error (like 429 rate limit or 401), stop and use fallback
                    break
            except Exception:
                continue
        
        if success and data:
            try:
                message = data['candidates'][0]['content']['parts'][0]['text'].strip()
                message = message.strip('"').strip("'").split('\n')[0]
                if message:
                    return f"{message} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            except (KeyError, IndexError):
                pass
    except Exception:
        pass
        
    return fallback_message

def run_bot(force_run=False):

    if not wait_for_internet():
        return

    if not os.path.exists(CONFIG_FILE):
        console.print("[bold red]Configuration file not found.[/bold red]")
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    repos = config.get("repositories", [])

    if not repos:
        console.print("[bold red]No repositories configured.[/bold red]")
        return
        
    if not force_run and config.get("schedule_type") == "random_day_time":
        try:
            with open(HISTORY_FILE, "r") as f:
                hist = json.load(f)
            
            if hist:
                last_commit_dt = datetime.datetime.strptime(hist[-1]["timestamp"], "%Y-%m-%d %H:%M:%S")
                hours_since = (datetime.datetime.now() - last_commit_dt).total_seconds() / 3600.0
                
                if hours_since < 12:
                    console.print(f"[dim]Natural Activity Mode: Skipped. Only {int(hours_since)} hours since last commit.[/dim]")
                    return
                elif hours_since < 48:
                    if random.random() > 0.10:
                        console.print("[dim]Natural Activity Mode: Skipped this hour to simulate natural gaps (10% execution chance).[/dim]")
                        return
                    console.print(f"[bold cyan]Natural Activity Mode:[/bold cyan] [yellow]Random trigger unexpectedly hit after {int(hours_since)} hours![/yellow]")
                else:
                    console.print(f"[bold cyan]Natural Activity Mode:[/bold cyan] [yellow]Enforcing commit since it's been {int(hours_since)} hours to prevent gaps.[/yellow]")
        except Exception:
            pass

    # NOTE: Daily limit for random activity commits is checked later,
    # only in the fallback path. Real user changes always push through.

    cleanup_expired_snapshots()

    repos_with_changes = []

    for path in repos:
        git_folder = os.path.join(path, ".git")
        if not os.path.isdir(git_folder):
            continue

        # --- SAFETY FIRST: Run Secret Shield BEFORE anything else ---
        # This ensures we fix vulnerabilities even if there are no code changes
        shield_sensitive_data(path)

        result = subprocess.run(
            ["git", "-C", path, "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            stdin=subprocess.DEVNULL
        )
        if result.stdout.strip():
            repos_with_changes.append(path)

    if repos_with_changes:
        console.print(f"\n[bold green]✔ Found uncommitted changes in {len(repos_with_changes)} repositories.[/bold green]")
        for repo_path in repos_with_changes:
            console.print(f"\n[bold yellow]Committing changes for:[/bold yellow] [cyan]{repo_path}[/cyan]")
            
            # Take physical backup of files before they get committed by bot
            console.print(f"[dim]Creating snapshot...[/dim]")
            snapshot_file = take_snapshot(repo_path)
            
            os.chdir(repo_path)

            add_process = subprocess.run(
                ["git", "add", "."], 
                capture_output=True, 
                text=True, 
                stdin=subprocess.DEVNULL
            )
            if add_process.returncode != 0:
                console.print(f"[bold red]Git add failed:[/bold red] {add_process.stderr.strip()}")
                continue

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fallback_commit_message = f"Auto commit of user changes | {timestamp}"
            
            commit_message = generate_ai_commit_message(repo_path, fallback_commit_message, config)
            
            console.print(f"[bold magenta]Commit message:[/bold magenta] {commit_message}")
            
            commit_process = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL
            )
            
            if "nothing to commit" in commit_process.stdout.lower():
                console.print("[yellow]Nothing new to commit.[/yellow]")
                continue
                
            push_process = subprocess.run(["git", "push"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
            
            if push_process.returncode == 0:
                console.print("[bold green]✔ Commit pushed successfully.[/bold green]")
                log_commit(repo_path, commit_message, is_random=False, snapshot_file=snapshot_file)
            else:
                console.print("[bold yellow]Push failed. Attempting to pull remote changes and retry...[/bold yellow]")
                pull_process = subprocess.run(["git", "pull", "--no-rebase", "--no-edit", "-s", "recursive", "-X", "ours"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
                if pull_process.returncode == 0:
                    retry_push = subprocess.run(["git", "push"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
                    if retry_push.returncode == 0:
                        console.print("[bold green]✔ Successfully pulled remote changes and pushed.[/bold green]")
                        log_commit(repo_path, commit_message, is_random=False, snapshot_file=snapshot_file)
                    else:
                        console.print(f"[bold red]Git Push Retry Error:[/bold red] {retry_push.stderr.strip()}")
                else:
                    subprocess.run(["git", "merge", "--abort"], capture_output=True, stdin=subprocess.DEVNULL)
                    console.print(f"[bold red]Git Error:[/bold red] {push_process.stderr.strip()}")
                    console.print(f"[bold red]Git Pull Merge Error:[/bold red] {pull_process.stderr.strip()}")
    else:
        # --- Daily limit: cap random activity commits at 5 per day ---
        if not force_run:
            try:
                today_str = datetime.datetime.now().strftime("%Y-%m-%d")
                if os.path.exists(HISTORY_FILE):
                    with open(HISTORY_FILE, "r") as f:
                        hist = json.load(f)
                    random_today = sum(
                        1 for entry in hist
                        if entry.get("timestamp", "").startswith(today_str)
                        and entry.get("type") == "Random Activity"
                    )
                    if random_today >= 5:
                        console.print(f"[yellow]Daily limit reached ({random_today}/5 random activity commits today). Skipping.[/yellow]")
                        return
                    console.print(f"[dim]Random activity commits today: {random_today}/5[/dim]")
            except Exception:
                pass

        console.print("\n[bold yellow]No user changes found. Performing a random activity commit.[/bold yellow]")
        repo_path = random.choice(repos)

        console.print(f"[bold yellow]Selected repository:[/bold yellow] [cyan]{repo_path}[/cyan]")

        git_folder = os.path.join(repo_path, ".git")

        if not os.path.isdir(git_folder):
            console.print(f"[bold red]Selected folder is not a git repository:[/bold red] {repo_path}")
            return

        console.print("[dim]Creating snapshot...[/dim]")
        snapshot_file = take_snapshot(repo_path)

        os.chdir(repo_path)

        with open(SAFE_FILE, "a") as f:
            f.write(f"automation activity: {datetime.datetime.now()}\n")

        commit_message = random.choice(commit_messages)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        commit_message = f"{commit_message} | {timestamp}"

        console.print(f"[bold magenta]Commit message:[/bold magenta] {commit_message}")

        add_process = subprocess.run(
            ["git", "add", SAFE_FILE], 
            capture_output=True, 
            text=True, 
            stdin=subprocess.DEVNULL
        )
        if add_process.returncode != 0:
            console.print(f"[bold red]Git add failed:[/bold red] {add_process.stderr.strip()}")
            return

        commit_process = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL
        )

        if "nothing to commit" in commit_process.stdout.lower():
            console.print("[yellow]Nothing new to commit.[/yellow]")
            return

        push_process = subprocess.run(["git", "push"], capture_output=True, text=True, stdin=subprocess.DEVNULL)

        if push_process.returncode == 0:
            console.print("[bold green]✔ Commit pushed successfully.[/bold green]")
            log_commit(repo_path, commit_message, is_random=True, snapshot_file=snapshot_file)
        else:
            console.print("[bold yellow]Push failed. Attempting to pull remote changes and retry...[/bold yellow]")
            pull_process = subprocess.run(["git", "pull", "--no-rebase", "--no-edit", "-s", "recursive", "-X", "ours"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if pull_process.returncode == 0:
                retry_push = subprocess.run(["git", "push"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
                if retry_push.returncode == 0:
                    console.print("[bold green]✔ Successfully pulled remote changes and pushed.[/bold green]")
                    log_commit(repo_path, commit_message, is_random=True, snapshot_file=snapshot_file)
                else:
                    console.print(f"[bold red]Git Push Retry Error:[/bold red] {retry_push.stderr.strip()}")
            else:
                subprocess.run(["git", "merge", "--abort"], capture_output=True, stdin=subprocess.DEVNULL)
                console.print(f"[bold red]Git Error:[/bold red] {push_process.stderr.strip()}")
                console.print(f"[bold red]Git Pull Merge Error:[/bold red] {pull_process.stderr.strip()}")

if __name__ == "__main__":
    run_bot()