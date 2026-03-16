import subprocess
import sys
import os


def create_startup_task():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    bot_script = os.path.join(script_dir, "auto_commit.py")

    python_path = sys.executable

    command = f'"{python_path}" "{bot_script}"'

    task_name = "AutoCommitBot"

    subprocess.run([
        "schtasks",
        "/create",
        "/sc", "onlogon",
        "/tn", task_name,
        "/tr", command,
        "/rl", "highest",
        "/f"
    ])

    print("Startup task created successfully.")