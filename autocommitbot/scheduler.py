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
    """Create a Windows Task Scheduler task using modern PowerShell commands to bypass legacy path limits."""
    if not is_admin():
        request_admin_and_exit()
        return

    python_path = sys.executable
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Error log path
    error_log = os.path.join(os.path.expanduser("~"), ".autocommitbot", "bot_error.log")
    os.makedirs(os.path.dirname(error_log), exist_ok=True)

    schedule_type, schedule_time = get_schedule_settings()

    # 1. Define the Trigger logic for PowerShell
    if schedule_type == "time" and schedule_time:
        ps_trigger = f"New-ScheduledTaskTrigger -DailyAt '{schedule_time}'"
    elif schedule_type == "random_day_time":
        # Run every hour for random checks
        ps_trigger = "New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 60)"
    else:
        ps_trigger = "New-ScheduledTaskTrigger -AtLogon"

    # 2. Define the Action logic
    # We use single quotes for the inner command and properly escape them for PS
    inner_cmd = (
        f"$env:PYTHONUTF8=1; sleep 10; cd '{project_root}'; "
        f"& '{python_path}' -m autocommitbot.auto_commit >> '{error_log}' 2>&1"
    )
    # Double the single quotes for PowerShell escaping
    escaped_inner_cmd = inner_cmd.replace("'", "''")
    
    ps_action = f"New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-nop -w h -c \"{escaped_inner_cmd}\"'"

    # 3. Define Settings (Batteries, etc.)
    ps_settings = "New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable"

    # 4. Combine into a registration command
    register_cmd = (
        f"$Action = {ps_action}; "
        f"$Trigger = {ps_trigger}; "
        f"$Settings = {ps_settings}; "
        f"Register-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings -TaskName '{TASK_NAME}' -RunLevel Highest -Force"
    )

    print(f"Creating Task Scheduler task: {TASK_NAME} ({schedule_type})...")

    try:
        # We run the whole registration script via PowerShell to bypass schtasks.exe limits
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", register_cmd],
            capture_output=True,
            text=True,
            check=True
        )
        print("Startup task scheduled successfully.")
        
    except subprocess.CalledProcessError as e:
        print("Failed to create scheduled task via PowerShell:")
        print(e.stderr.strip() or e.stdout.strip())


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