import os
import sys

STARTUP_FILE = "autocommitbot_startup.vbs"


def get_startup_folder():
    """Return the Windows Startup folder path."""
    return os.path.join(
        os.getenv("APPDATA"),
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )


def create_startup_task():
    """Create a silent startup launcher using VBScript."""

    python_path = sys.executable
    startup_folder = get_startup_folder()
    script_path = os.path.join(startup_folder, STARTUP_FILE)

    # We use Chr(34) to safely wrap the Python path in quotes for VBScript
    vbs_content = f'''
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run Chr(34) & "{python_path}" & Chr(34) & " -m autocommitbot.auto_commit", 0, False
Set WshShell = Nothing
'''

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(vbs_content.strip())

    print("Startup launcher created successfully.")
    print(f"Location: {script_path}")

def remove_startup_task():
    """Remove the VBScript startup launcher."""
    startup_folder = get_startup_folder()
    script_path = os.path.join(startup_folder, STARTUP_FILE)

    if os.path.exists(script_path):
        os.remove(script_path)
        print("Startup launcher removed.")
    else:
        print("Startup launcher not found.")