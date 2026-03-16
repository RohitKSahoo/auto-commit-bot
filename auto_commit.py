import os
import subprocess
import time
import datetime
import socket
import json
import random


# -------------------------------------------------------------
# CONFIGURATION SECTION
# -------------------------------------------------------------

# config file that stores user selected repositories
CONFIG_FILE = "config.json"

# safe file that automation is allowed to modify
SAFE_FILE = ".dev_activity_log"


# -------------------------------------------------------------
# COMMIT MESSAGE POOL
# Random message will be selected each time a commit is created
# -------------------------------------------------------------

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


# -------------------------------------------------------------
# FUNCTION: Check Internet Connectivity
# The script waits until internet is available before running
# -------------------------------------------------------------

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


# -------------------------------------------------------------
# LOAD USER CONFIGURATION
# Reads config.json to get repository list
# -------------------------------------------------------------

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

repos = config["repositories"]

if not repos:
    print("No repositories configured.")
    exit()


# -------------------------------------------------------------
# SELECT RANDOM REPOSITORY
# Randomly choose one repo from the configured list
# -------------------------------------------------------------

repo_path = random.choice(repos)

print("Selected repository:", repo_path)


# -------------------------------------------------------------
# VALIDATE GIT REPOSITORY
# Ensures selected folder actually contains a git repo
# -------------------------------------------------------------

git_folder = os.path.join(repo_path, ".git")

if not os.path.isdir(git_folder):
    print("Selected folder is not a git repository:", repo_path)
    exit()


# move script execution into repository
os.chdir(repo_path)


# -------------------------------------------------------------
# UPDATE SAFE AUTOMATION FILE
# Only this file is modified by the automation
# -------------------------------------------------------------

with open(SAFE_FILE, "a") as f:
    f.write(f"automation activity: {datetime.datetime.now()}\n")


# -------------------------------------------------------------
# GENERATE RANDOM COMMIT MESSAGE
# -------------------------------------------------------------

commit_message = random.choice(commit_messages)
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

commit_message = f"{commit_message} | {timestamp}"

print("Commit message:", commit_message)


# -------------------------------------------------------------
# STAGE ONLY SAFE FILE
# Prevents automation from touching other project files
# -------------------------------------------------------------

subprocess.run(["git", "add", SAFE_FILE])


# -------------------------------------------------------------
# CREATE COMMIT
# -------------------------------------------------------------

commit_process = subprocess.run(
    ["git", "commit", "-m", commit_message],
    capture_output=True,
    text=True
)


# -------------------------------------------------------------
# CHECK IF THERE WAS ANYTHING TO COMMIT
# -------------------------------------------------------------

if "nothing to commit" in commit_process.stdout.lower():
    print("Nothing new to commit.")
else:
    subprocess.run(["git", "push"])
    print("Commit pushed successfully.")