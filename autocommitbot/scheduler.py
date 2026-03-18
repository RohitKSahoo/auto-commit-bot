import os
import sys
import ctypes
import subprocess

TASK_NAME = "AutoCommitBot"


def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()  # type: ignore
    except:
        return False


def request_admin_and_exit():
    """Relaunches the script as administrator in a new window."""
    print("Requesting administrator privileges...")
    
    executable = sys.executable
    args = " ".join([f'"{a}"' if ' ' in a else a for a in sys.argv[1:]])  # type: ignore
    
    # We force the new process to always use the module invocation
    # instead of the potentially broken pip-installed script path.
    command_to_run = f'"{executable}" -m autocommitbot.cli {args}'
        
    # Launch via cmd.exe /c and pause so the user can see the status before the window closes
    cmd_args = f'/c "{command_to_run} & pause"'
    
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", cmd_args, None, 1)  # type: ignore
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        
    sys.exit(0)


import json

def get_schedule_settings():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                c = json.load(f)
                return c.get("schedule_type", "onlogon"), c.get("schedule_time", None)
    except:
        pass
    return "onlogon", None

def create_startup_task():
    """Create a Windows Task Scheduler task."""
    if not is_admin():
        request_admin_and_exit()
        return

    python_path = sys.executable
    # The command needs to run the auto_commit module
    command = f'"{python_path}" -m autocommitbot.auto_commit'

    schedule_type, schedule_time = get_schedule_settings()

    print("Creating Task Scheduler task: AutoCommitBot...")

    # schtasks command to create a task with highest privileges
    schtasks_cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", command,
        "/RL", "HIGHEST",
        "/F"
    ]

    if schedule_type == "time" and schedule_time:
        schtasks_cmd.extend(["/SC", "DAILY", "/ST", schedule_time])
        print(f"Scheduling to run daily at: {schedule_time}")
    elif schedule_type == "random_day_time":
        schtasks_cmd.extend(["/SC", "MINUTE", "/MO", "60"])
        print("Scheduling to run periodically in the background (will organically vary commits).")
    else:
        schtasks_cmd.extend(["/SC", "ONLOGON"])
        print("Scheduling to run on Logon.")

    try:
        subprocess.run(schtasks_cmd, capture_output=True, text=True, check=True)
        print("Startup task scheduled successfully via Task Scheduler.")
        
        print("Configuring task to run on battery power...")
        ps_script = (
            f"$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries "
            f"-DontStopIfGoingOnBatteries; "
            f"Set-ScheduledTask -TaskName '{TASK_NAME}' -Settings $settings"
        )
        ps_cmd = ["powershell", "-NoProfile", "-Command", ps_script]
        
        try:
            subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
            print("Task configured to run even when on battery power.")
        except subprocess.CalledProcessError as e:
            print("Warning: Could not configure the task to run on battery power:")
            print(e.stderr.strip())

    except subprocess.CalledProcessError as e:
        print("Failed to create scheduled task:")
        print(e.stderr.strip())


def remove_startup_task():
    """Remove the Windows Task Scheduler task."""
    if not is_admin():
        request_admin_and_exit()
        return

    print("Removing Task Scheduler task: AutoCommitBot...")

    schtasks_cmd = [
        "schtasks", "/Delete",
        "/TN", TASK_NAME,
        "/F"
    ]

    try:
        subprocess.run(schtasks_cmd, capture_output=True, text=True, check=True)
        print("Startup task removed successfully from Task Scheduler.")
    except subprocess.CalledProcessError as e:
        print("Failed to remove scheduled task. It might not exist.")