# 🚀 AutoCommitBot

**Keep your GitHub profile active, safe, and professional—automatically.**

AutoCommitBot is a smart, AI-powered tool that manages your GitHub activity while you sleep. It uses Google's Gemini AI to analyze your code changes and write natural, human-like commit messages. Whether you're working on a big project or just want to maintain a consistent contribution graph, this bot handles the entire Git workflow for you.

---

## ✨ Key Features

### 🤖 Smart AI Commits
*   **AI Message Generation**: The bot analyzes your `git diff` and writes real commit messages (e.g., *"Added login validation logic"* instead of *"Update file.py"*).
*   **Universal Compatibility**: Automatically works with every Gemini model version (2.5, 2.0, 1.5, or Pro) based on your API key.

### 🛡️ "Secret Shield" Security
*   **Auto-Healing Gitignore**: If you forget to hide a sensitive file (like `.env` or `config.json`), the bot automatically adds it to your `.gitignore` for you.
*   **Proactive Un-tracking**: If a secret file was already accidentally pushed to GitHub in the past, the bot will detect it, un-track it, and remove it from GitHub’s view while keeping it safe on your local disk.
*   **API Key Scanner**: Scans your code for exposed keys (Gemini, OpenAI, etc.) and warns you before you leak them.

### 🕒 Natural Activity Scheduling
*   **Human-Like Behavior**: Instead of committing every hour like a robot, "Natural Mode" skips random days and varies its timing to look like a real developer's schedule.
*   **Logon Trigger**: Automatically starts when you turn on your computer and log in to Windows.

### 🔄 Universal Undo (The Time Machine)
*   **One-Click Restore**: If the bot ever commits something you don't like, simply use the `restore` command. It will roll back your local files **and** force-push the fix to GitHub automatically.
*   **Automatic Backups**: Creates a ZIP snapshot of your folder before every single commit, so your work is never lost.

---

## 🛠️ Commands Overview

| Command | What it does |
| :--- | :--- |
| `autocommit setup` | Run the friendly wizard to pick your repos and set your schedule. |
| `autocommit add` | Instantly add the current folder you are working in to the bot. |
| `autocommit run` | Force the bot to scan and commit everything right now. |
| `autocommit status` | See a list of all repositories the bot is currently tracking. |
| `autocommit dashboard` | View a beautiful table of your commit history and stats. |
| `autocommit restore` | Pick a past backup and roll back both your local and GitHub repo. |

---

## ⚙️ Installation

### 1. **Prerequisites**
*   **Python 3.10+** installed on your system.
*   **Git** installed and authenticated (run `git push` once manually in any repo to make sure it works).
*   **Gemini API Key** (Optional, but recommended for AI messages). Get it for free at [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. **Download & Setup**
1.  Clone this repository or download the source code.
2.  Open your terminal inside the project folder.
3.  Install the required packages:
    ```bash
    pip install -e .
    ```
4.  Run the setup wizard:
    ```bash
    autocommit setup
    ```

### 3. **Start Automating**
Once setup is complete, the bot will handle the rest! You can relax knowing your contributions and security are being managed by **AutoCommitBot**.

---
*Developed with ❤️ by **@RohitKSahoo***
