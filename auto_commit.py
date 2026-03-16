import os
import subprocess
import time
import datetime
import socket
import random

REPO_PATH = r"D:\Projects\auto-commit-tracker"

commit_messages = [
    "update development log",
    "system activity update",
    "environment sync",
    "routine maintenance update",
    "minor repo housekeeping",
    "development log refresh",
    "background system update",
    "auto maintenance commit",
    "daily repository update",
    "internal log update",
    "environment health check",
    "repo activity update",
    "system sync update",
    "repository housekeeping",
    "minor maintenance task",
    "development environment update",
    "routine system update",
    "repo maintenance update",
    "activity log refresh",
    "internal repository update",
    "system maintenance commit",
    "background activity update",
    "minor system sync",
    "development log checkpoint",
    "automated environment update",
    "internal maintenance update",
    "repo health update",
    "development environment checkpoint",
    "system state update",
    "repository activity maintenance"
]

def internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except:
        return False


print("Checking internet connection...")

while not internet_available():
    print("Waiting for internet...")
    time.sleep(10)

print("Internet detected")

os.chdir(REPO_PATH)

# update activity file
with open("activity.txt", "a") as f:
    f.write(f"Boot commit: {datetime.datetime.now()}\n")

# choose random commit message
commit_message = random.choice(commit_messages)

# add timestamp to make each commit unique
commit_message = f"{commit_message} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

print("Using commit message:", commit_message)

# git commands
subprocess.run(["git", "add", "."])

commit_process = subprocess.run(
    ["git", "commit", "-m", commit_message],
    capture_output=True,
    text=True
)

# check if commit happened
if "nothing to commit" in commit_process.stdout.lower():
    print("Nothing new to commit.")
else:
    subprocess.run(["git", "push"])
    print("Commit pushed successfully.")