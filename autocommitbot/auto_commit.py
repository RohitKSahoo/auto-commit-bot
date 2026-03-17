import os
import subprocess
import time
import datetime
import socket
import json
import random


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
SAFE_FILE = ".dev_activity_log"


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
    print("Checking internet connection...")

    attempts = 0

    while not internet_available():

        if attempts >= max_attempts:
            print("Internet not available. Skipping run.")
            return False

        print("Waiting for internet...")
        time.sleep(10)
        attempts += 1

    print("Internet detected")
    return True


def run_bot():

    if not wait_for_internet():
        return

    if not os.path.exists(CONFIG_FILE):
        print("Configuration file not found.")
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    repos = config.get("repositories", [])

    if not repos:
        print("No repositories configured.")
        return

    repos_with_changes = []

    for path in repos:
        git_folder = os.path.join(path, ".git")
        if not os.path.isdir(git_folder):
            continue

        result = subprocess.run(
            ["git", "-C", path, "status", "--porcelain"],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL
        )
        if result.stdout.strip():
            repos_with_changes.append(path)

    if repos_with_changes:
        print(f"Found uncommitted changes in {len(repos_with_changes)} repositories.")
        for repo_path in repos_with_changes:
            print("Committing uncommitted user changes for:", repo_path)
            os.chdir(repo_path)
            
            add_process = subprocess.run(
                ["git", "add", "."], 
                capture_output=True, 
                text=True, 
                stdin=subprocess.DEVNULL
            )
            if add_process.returncode != 0:
                print(f"Git add failed: {add_process.stderr.strip()}")
                continue

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto commit of user changes | {timestamp}"
            
            print("Commit message:", commit_message)
            
            commit_process = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL
            )
            
            if "nothing to commit" in commit_process.stdout.lower():
                print("Nothing new to commit.")
                continue
                
            push_process = subprocess.run(["git", "push"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
            
            if push_process.returncode == 0:
                print("Commit pushed successfully.")
            else:
                print("Push failed.")
    else:
        print("All changes are already committed. Performing a random activity commit.")
        repo_path = random.choice(repos)

        print("Selected repository:", repo_path)

        git_folder = os.path.join(repo_path, ".git")

        if not os.path.isdir(git_folder):
            print("Selected folder is not a git repository:", repo_path)
            return

        os.chdir(repo_path)

        with open(SAFE_FILE, "a") as f:
            f.write(f"automation activity: {datetime.datetime.now()}\n")

        commit_message = random.choice(commit_messages)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        commit_message = f"{commit_message} | {timestamp}"

        print("Commit message:", commit_message)

        add_process = subprocess.run(
            ["git", "add", SAFE_FILE], 
            capture_output=True, 
            text=True, 
            stdin=subprocess.DEVNULL
        )
        if add_process.returncode != 0:
            print(f"Git add failed: {add_process.stderr.strip()}")
            return

        commit_process = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL
        )

        if "nothing to commit" in commit_process.stdout.lower():
            print("Nothing new to commit.")
            return

        push_process = subprocess.run(["git", "push"], capture_output=True, text=True, stdin=subprocess.DEVNULL)

        if push_process.returncode == 0:
            print("Commit pushed successfully.")
        else:
            print("Push failed.")

if __name__ == "__main__":
    run_bot()