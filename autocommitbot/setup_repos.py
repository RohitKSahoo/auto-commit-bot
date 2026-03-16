import requests
import json
import os
import subprocess

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
    # Step 2: Display repositories
    # ---------------------------------------------------------

    print("\nRepositories found:\n")

    repo_names = []

    for i, repo in enumerate(repos):
        print(f"{i+1}. {repo['name']}")
        repo_names.append(repo["name"])

    # ---------------------------------------------------------
    # Step 3: Select repos
    # ---------------------------------------------------------

    print("\nSelect repositories to automate (comma separated numbers)")
    selection = input("Example: 1,3,5 : ")

    try:
        indexes = [int(x.strip()) - 1 for x in selection.split(",")]
    except Exception:
        print("Invalid selection format.")
        return

    selected_repos = []

    for i in indexes:
        if i < 0 or i >= len(repo_names):
            print("Invalid repository number:", i + 1)
            return
        selected_repos.append(repo_names[i])

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
    # Step 7: Save configuration
    # ---------------------------------------------------------

    config = {
        "repositories": repo_paths
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

from autocommitbot.scheduler import create_startup_task

create_startup_task()