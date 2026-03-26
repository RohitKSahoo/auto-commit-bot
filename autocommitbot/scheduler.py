import json
import os
import sys
import ctypes
import subprocess
from autocommitbot.paths import CONFIG_FILE

TASK_NAME = "AutoCommitBot"


def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()  # type: ignore
    except Exception:
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



def get_schedule_settings():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                c = json.load(f)
                return c.get("schedule_type", "onlogon"), c.get("schedule_time", None)
    except Exception:
        pass
    return "onlogon", None

def create_startup_task():
    """Create a Windows Task Scheduler task using PowerShell for robust path handling."""
    if not is_admin():
        request_admin_and_exit()
        return

    python_path = sys.executable
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # NEW LOG: We redirect stderr to a separate file so users can see startup crashes (e.g., ModuleNotFoundError)
    error_log = os.path.join(os.path.expanduser("~"), ".autocommitbot", "bot_error.log")

    # We use PowerShell for the task command because it handles spaces and drive letters much better than cmd.exe
    # IMPROVED LOGGING: We redirect both stdout (1) and stderr (2) to the log
    # This prevents the process from hanging if the output buffer fills up
    ps_task_cmd = (
        f"powershell.exe -NoProfile -WindowStyle Hidden -Command "
        f"\"Start-Sleep -s 10; cd '{project_root}'; "
        f"& '{python_path}' -m autocommitbot.auto_commit >> '{error_log}' 2>&1\""
    )

    schedule_type, schedule_time = get_schedule_settings()

    print(f"Creating Task Scheduler task: {TASK_NAME} ({schedule_type})...")

    # schtasks command to create a basic task with highest privileges
    schtasks_cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", ps_task_cmd,
        "/RL", "HIGHEST",
        "/F"
    ]

    if schedule_type == "time" and schedule_time:
        schtasks_cmd.extend(["/SC", "DAILY", "/ST", schedule_time])
        print(f"Scheduling to run daily at: {schedule_time}")
    elif schedule_type == "random_day_time":
        schtasks_cmd.extend(["/SC", "MINUTE", "/MO", "60"])
        print("Scheduling to run periodically in the background.")
    else:
        schtasks_cmd.extend(["/SC", "ONLOGON"])
        print("Scheduling to run on Logon.")

    try:
        subprocess.run(schtasks_cmd, capture_output=True, text=True, check=True)
        print("Startup task scheduled successfully.")
        
        # Configure battery settings via PowerShell
        ps_settings = f"Set-ScheduledTask -TaskName '{TASK_NAME}' -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries)"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_settings], capture_output=True, text=True)

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
    except subprocess.CalledProcessError:
        print("Failed to remove scheduled task. It might not exist.")