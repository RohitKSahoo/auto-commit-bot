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
import sys
from rich.console import Console

# Force UTF-8 and terminal colors even when redirected to capture logs better
console = Console(force_terminal=True) if not sys.stdout.isatty() else Console()



from autocommitbot.paths import CONFIG_FILE, HISTORY_FILE, LOG_FILE, BACKUP_DIR

SAFE_FILE = ".dev_activity_log"

# Global timeout for any git command to prevent background hangs
GIT_TIMEOUT = 90  # seconds


def log_to_file(message):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


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
                    snap_path = os.path.join(str(BACKUP_DIR), entry["snapshot"])
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
        tracked = subprocess.run(["git", "ls-files"], cwd=repo_path, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=GIT_TIMEOUT)
        untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=repo_path, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=GIT_TIMEOUT)
        
        all_files = tracked.stdout.splitlines() + untracked.stdout.splitlines()
        
        if not all_files:
            return None
            
        repo_name = os.path.basename(os.path.abspath(repo_path))
        snapshot_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"{repo_name}_{snapshot_id}.zip"
        
        os.makedirs(str(BACKUP_DIR), exist_ok=True)
        zip_path = os.path.join(str(BACKUP_DIR), zip_name)
        
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


def get_daily_commit_count():
    try:
        if not os.path.exists(HISTORY_FILE):
            return 0
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        with open(HISTORY_FILE, "r") as f:
            hist = json.load(f)
        return sum(
            1 for entry in hist
            if entry.get("timestamp", "").startswith(today_str)
        )
    except Exception:
        return 0


def internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except Exception:
        return False


def wait_for_internet(max_attempts=30):
    log_to_file("Checking internet connection...")
    console.print("[dim]Checking internet connection...[/dim]")

    # Initial delay for system stability (especially on logon)
    time.sleep(5)

    attempts = 0
    while not internet_available():
        if attempts >= max_attempts:
            log_to_file("Internet not available after 5 minutes. Skipping run.")
            console.print("[bold red]Internet not available. Skipping run.[/bold red]")
            return False

        console.print("[yellow]Waiting for internet...[/yellow]")
        time.sleep(10)
        attempts += 1

    log_to_file("Internet detected.")
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
    """Safety check to detect and shield sensitive data.
    If found, adds to gitignore, untracks from git, and halts the push.
    """
    gitignore_path = os.path.join(repo_path, ".gitignore")
    existing_ignore = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
            existing_ignore = f.read()

    found_secrets = False
    new_ignores = set()

    # 1. Check for sensitive files being tracked or staged
    try:
        # Get list of all tracked and untracked files
        files_process = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--cached"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=GIT_TIMEOUT
        )
        all_relevant_files = files_process.stdout.splitlines()

        for s_pattern in SENSITIVE_FILES:
            raw_pattern = s_pattern.replace("*", "")
            for f_path in all_relevant_files:
                if s_pattern in f_path or (raw_pattern and f_path.endswith(raw_pattern)):
                    if s_pattern not in existing_ignore and f_path not in existing_ignore:
                        new_ignores.add(f_path if "*" not in s_pattern else s_pattern)
                    
                    # If this sensitive file is already staged/tracked, it's a risk
                    found_secrets = True
                    console.print(f"[blue][SHIELD][/blue] [bold red]RISK:[/bold red] Sensitive file detected: [cyan]{f_path}[/cyan]")

    except Exception:
        pass

    # 2. Key Scanning in Diffs
    try:
        # Get all staged changes at once rather than per-file for performance
        diff_process = subprocess.run(
            ["git", "diff", "--cached"], 
            cwd=repo_path, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore',
            timeout=GIT_TIMEOUT
        )
        all_diffs = diff_process.stdout
        
        # Check the entire diff for patterns
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, all_diffs):
                console.print(f"[blue][SHIELD][/blue] [bold red]CRITICAL:[/bold red] API Key detected in staged changes!")
                found_secrets = True
                
        # Also check for sensitive filenames in staged file list
        staged_files_process = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=GIT_TIMEOUT
        )
        changed_files = staged_files_process.stdout.splitlines()
        
        for f_path in changed_files:
            for s_pattern in SENSITIVE_FILES:
                raw_pattern = s_pattern.replace("*", "")
                if s_pattern in f_path or (raw_pattern and f_path.endswith(raw_pattern)):
                    if s_pattern not in existing_ignore:
                        new_ignores.add(f_path if "*" not in s_pattern else s_pattern)
                    found_secrets = True

    except Exception:
        pass

    # 3. Take Action
    if found_secrets:
        # Update .gitignore if needed
        if new_ignores:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                if not existing_ignore:
                    f.write("\n# AutoCommitBot Secret Shield - Automation Rules\n")
                else:
                    f.write("\n\n# AutoCommitBot - New Sensitive Files Detected\n")
                for item in new_ignores:
                    f.write(f"{item}\n")
            console.print(f"[blue][SHIELD][/blue] [green]✔ Added {len(new_ignores)} items to .gitignore.[/green]")

        # Try to un-track the files if they are in the index
        subprocess.run(["git", "rm", "-r", "--cached", "."], cwd=repo_path, capture_output=True, timeout=GIT_TIMEOUT)
        subprocess.run(["git", "add", ".gitignore"], cwd=repo_path, capture_output=True, timeout=GIT_TIMEOUT)

        console.print("\n[bold yellow]⚠ SECRET SHIELD ALERT[/bold yellow]")
        console.print(f"[white]The bot found sensitive information in repository:[/white] [bold]{repo_path}[/bold]")
        console.print("[white]1. We have added the suspected files to your [bold].gitignore[/bold].[/white]")
        console.print("[white]2. We have removed them from Git tracking (they are safe locally).[/white]")
        console.print("[white]3. [bold]Action Required:[/bold] Please check your staged changes manually.[/white]")
        console.print("[white]4. If everything is safe, you can push manually or re-run the bot.[/white]\n")
        
        return False # HALT this repo only

    return True # SAFE to proceed

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
            errors='ignore',
            timeout=GIT_TIMEOUT
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
        prompt = (
            "Write a clear and informative git commit message for the following changes.\n"
            "Format:\n"
            "1. A concise, one-line summary (under 60 characters).\n"
            "2. A blank line.\n"
            "3. A bulleted list explaining exactly what was changed and added.\n"
            "Do NOT use markdown headers, backticks, or code blocks. Use plain text only.\n\n"
            f"{diff_text}"
        )
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
                    break
            except Exception:
                continue
        
        if success and data:
            try:
                # Extract the full multiline message from AI response
                raw_message = data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Sanitize: Remove leading/trailing quotes and markdown code fences if AI added them
                clean_message = raw_message.strip('"').strip("'")
                if clean_message.startswith("```"):
                   clean_message = re.sub(r"```(text|plaintext|git)?\s*", "", clean_message)
                   clean_message = clean_message.replace("```", "")
                
                if clean_message:
                    # Append timestamp and automated tag as a footer
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    footer = f"\n\n---\n[Auto-Generated-By: AutoCommitBot | {timestamp}]"
                    return clean_message.strip() + footer
            except (KeyError, IndexError):
                pass
    except Exception:
        pass
        
    return fallback_message

def run_bot(force_run=False, manual_mode=None):
    """
    Main bot execution logic.
    
    manual_mode options:
    - None: System chooses based on force_run (Default for background).
    - 'user': Explicitly scan and commit user changes.
    - 'random': Explicitly perform a random activity commit.
    """
    log_to_file(f"Bot execution started (force_run={force_run}, manual_mode={manual_mode})")
    
    if not wait_for_internet():
        return

    if not os.path.exists(CONFIG_FILE):
        log_to_file("Error: Configuration file not found.")
        console.print("[bold red]Configuration file not found.[/bold red]")
        return

    log_to_file("Loading configuration...")
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    repos = config.get("repositories", [])

    if not repos:
        log_to_file("No repositories configured.")
        console.print("[bold red]No repositories configured.[/bold red]")
        return

    # Determine what to do based on mode
    # If it's a Background run (not forced, no mode), it's strictly Random
    is_background = not force_run and manual_mode is None
    
    target_mode = manual_mode
    if target_mode is None:
        if is_background:
            target_mode = "random"
        else:
            # Default fallback for manual if no mode specified (though CLI should provide it)
            target_mode = "user"

    log_to_file(f"Target mode determined: {target_mode}")

    # --- SHARED CLEANUP ---
    log_to_file("Performing snapshot cleanup...")
    cleanup_expired_snapshots()

    # --- PATH A: USER CHANGES ---
    if target_mode == "user":
        console.print("\n[bold cyan]Scanning repositories for your changes...[/bold cyan]")
        repos_with_changes = []

        for path in repos:
            try:
                git_folder = os.path.join(path, ".git")
                if not os.path.isdir(git_folder):
                    continue

                log_to_file(f"Scanning for changes: {path}")
                
                # Run Secret Shield
                if not shield_sensitive_data(path):
                    log_to_file(f"Skipping {path} due to security risk.")
                    continue

                result = subprocess.run(
                    ["git", "-C", path, "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    stdin=subprocess.DEVNULL,
                    timeout=GIT_TIMEOUT
                )
                if result.stdout.strip():
                    repos_with_changes.append(path)
            except Exception as e:
                log_to_file(f"Error checking repo {path}: {e}")

        if repos_with_changes:
            console.print(f"[bold green]Found changes in {len(repos_with_changes)} repositories.[/bold green]")
            for repo_path in repos_with_changes:
                log_to_file(f"Processing manual repo: {repo_path}")
                console.print(f"\n[cyan]>> Committing changes for:[/cyan] [bold]{repo_path}[/bold]")
                
                console.print(f"[dim]Creating snapshot...[/dim]")
                snapshot_file = take_snapshot(repo_path)
                
                os.chdir(repo_path)

                add_process = subprocess.run(["git", "add", "."], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=GIT_TIMEOUT)
                if add_process.returncode != 0:
                    console.print(f"[bold red]Git add failed:[/bold red] {add_process.stderr.strip()}")
                    continue

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fallback_msg = f"Auto commit of user changes | {timestamp}"
                commit_message = generate_ai_commit_message(repo_path, fallback_msg, config)
                
                console.print(f"[magenta]Commit message:[/magenta] {commit_message}")
                
                commit_process = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=GIT_TIMEOUT)
                
                if "nothing to commit" in commit_process.stdout.lower():
                    console.print("[yellow]Nothing new to commit.[/yellow]")
                    continue
                    
                push_process = subprocess.run(["git", "push"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=GIT_TIMEOUT)
                
                if push_process.returncode == 0:
                    console.print("[green]✔ Pushed successfully.[/green]")
                    log_commit(repo_path, commit_message, is_random=False, snapshot_file=snapshot_file)
                else:
                    console.print("[yellow]Push failed. Retrying with pull...[/yellow]")
                    pull_process = subprocess.run(["git", "pull", "--no-rebase", "--no-edit", "-s", "recursive", "-X", "ours"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=GIT_TIMEOUT)
                    if pull_process.returncode == 0:
                        retry_push = subprocess.run(["git", "push"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=GIT_TIMEOUT)
                        if retry_push.returncode == 0:
                            console.print("[bold green]✔ Successfully pulled and pushed.[/bold green]")
                            log_commit(repo_path, commit_message, is_random=False, snapshot_file=snapshot_file)
        else:
            console.print("[yellow]No changes found in any tracked repositories.[/yellow]")

    # --- PATH B: RANDOM ACTIVITY (STRICT) ---
    elif target_mode == "random":
        if is_background:
            # Check Natural activity timing only in background
            if config.get("schedule_type") == "random_day_time":
                try:
                    if os.path.exists(HISTORY_FILE):
                        with open(HISTORY_FILE, "r") as f:
                            hist = json.load(f)
                        if hist:
                            last_commit_dt = datetime.datetime.strptime(hist[-1]["timestamp"], "%Y-%m-%d %H:%M:%S")
                            hours_since = (datetime.datetime.now() - last_commit_dt).total_seconds() / 3600.0
                            if hours_since < 12:
                                console.print(f"[dim]Natural Activity Mode: Skipped. Only {int(hours_since)} hours since last commit.[/dim]")
                                return
                            elif hours_since < 48 and random.random() > 0.10:
                                console.print("[dim]Natural Activity Mode: Skipped to simulate natural gaps.[/dim]")
                                return
                except Exception:
                    pass

            # Daily limit for random commits in background
            try:
                today_str = datetime.datetime.now().strftime("%Y-%m-%d")
                if os.path.exists(HISTORY_FILE):
                    with open(HISTORY_FILE, "r") as f:
                        hist = json.load(f)
                    random_today = sum(1 for e in hist if e.get("timestamp", "").startswith(today_str) and e.get("type") == "Random Activity")
                    if random_today >= 5:
                        console.print(f"[yellow]Daily limit reached ({random_today}/5). Skipping.[/yellow]")
                        return
            except Exception:
                pass

        log_to_file("Executing random activity commit.")
        console.print("\n[yellow]Executing random activity (heartbeat) commit...[/yellow]")
        
        repo_path = random.choice(repos)
        log_to_file(f"Selected repo: {repo_path}")
        console.print(f"[cyan]>> Selected repository:[/cyan] [bold]{repo_path}[/bold]")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            console.print(f"[bold red]Not a git repository:[/bold red] {repo_path}")
            return

        console.print("[dim]Creating snapshot...[/dim]")
        snapshot_file = take_snapshot(repo_path)

        os.chdir(repo_path)
        with open(SAFE_FILE, "a") as f:
            f.write(f"automation activity: {datetime.datetime.now()}\n")

        commit_msg = random.choice(commit_messages)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"{commit_msg} | {timestamp}"

        console.print(f"[magenta]Commit message:[/magenta] {full_msg}")

        subprocess.run(["git", "add", SAFE_FILE], capture_output=True, timeout=GIT_TIMEOUT)
        commit_process = subprocess.run(["git", "commit", "-m", full_msg], capture_output=True, text=True, timeout=GIT_TIMEOUT)

        if "nothing to commit" in commit_process.stdout.lower():
            console.print("[yellow]Nothing new to commit.[/yellow]")
            return

        push_process = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=GIT_TIMEOUT)

        if push_process.returncode == 0:
            console.print("[green]✔ Pushed successfully.[/green]")
            log_commit(repo_path, full_msg, is_random=True, snapshot_file=snapshot_file)
        else:
            console.print("[yellow]Push failed. Retrying with pull...[/yellow]")
            subprocess.run(["git", "pull", "--no-rebase", "--no-edit", "-s", "recursive", "-X", "ours"], capture_output=True, timeout=GIT_TIMEOUT)
            retry_push = subprocess.run(["git", "push"], capture_output=True, timeout=GIT_TIMEOUT)
            if retry_push.returncode == 0:
                console.print("[bold green]✔ Successfully pulled and pushed.[/bold green]")
                log_commit(repo_path, full_msg, is_random=True, snapshot_file=snapshot_file)


if __name__ == "__main__":
    try:
        run_bot()
    except Exception as e:
        import traceback
        log_to_file(f"CRITICAL CRASH: {e}")
        log_to_file(traceback.format_exc())
        print(f"CRITICAL ERROR: {e}")
