# 🚀 AutoCommitBot (v1.1.6)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license)
[![GitHub activity](https://img.shields.io/badge/github-automated-orange.svg)](https://github.com/RohitKSahoo/auto-commit-bot)

**Maintain a professional GitHub presence with AI-powered automation and built-in security.**

AutoCommitBot is an intelligent, cross-platform CLI tool designed for developers who want to maintain a consistent contribution history without the manual overhead. It monitors your local repositories, generates meaningful commit messages using Google's Gemini AI, and manages the full Git lifecycle automatically.

---

## 🖥️ Preview

<p align="center">
  <img src="assets/CLI_2.png" alt="AutoCommitBot CLI" width="750"/>
</p>

---

## 🌟 Why AutoCommitBot?

* **AI Commit Messages** — Generates meaningful, context-aware commits instead of generic updates
* **Security (Secret Shield)** — Prevents accidental exposure of sensitive files and credentials
* **Natural Activity Mode** — Simulates realistic developer commit patterns
* **Backup & Restore** — Enables complete rollback of local and remote states
* **Automated Execution** — Runs seamlessly in the background on system logon

---

## ✨ Features

### Core Capabilities

* **AI Commit Generation** — Context-aware commit messages using Gemini with model fallback
* **Security Layer (Secret Shield)** — Automatic protection against sensitive file and credential exposure
* **Scheduling Engine** — Supports logon, fixed-time, and natural activity-based execution
* **Backup & Restore** — Pre-commit snapshots with full local and remote rollback capability
* **Repository Management** — GitHub repo discovery, selection, and automatic cloning
* **Dashboard & Analytics** — CLI-based insights into commit history and activity
* **Execution Reliability** — Built-in retry logic, conflict handling, and network checks


<details>
<summary>🔍 View Full Feature Breakdown</summary>

### ⚙️ Setup & Configuration

* GitHub Repository Discovery via API
* Interactive multi-select repo setup
* Base folder configuration
* Automatic cloning of missing repos
* Git authentication verification
* Backward navigation during setup

---

### 🕐 Scheduling System

* Logon trigger (Windows Task Scheduler)
* Fixed-time daily scheduling
* Randomized daily execution (9 AM – 11 PM)
* Natural Activity Mode (probabilistic commits with 48h enforcement)
* Runs with highest privileges
* Works on battery power

---

### 🔁 Commit Engine

* Smart change detection across repositories
* Commits real user changes with descriptive messages
* Generates fallback activity commits when idle
* Automatic pull → merge → push workflow
* Push retry logic on failure

---

### 🤖 AI Commit System

* Gemini AI integration for commit messages
* Model fallback chain: 2.5 Flash → 2.0 Flash → 1.5 Flash → Pro
* Diff truncation for large inputs (8000 chars)

---

### 💾 Backup & Restore

* ZIP snapshot before every commit
* Configurable backup retention (`config-backup`)
* Restore command with snapshot selection
* Automatic GitHub rollback via force push

---

### 📊 Dashboard & Management

* Dashboard with last 50 commits (rich table view)
* Commit classification (User vs Activity)
* Status command for tracked repos
* Add/remove repositories dynamically
* Persistent history tracking (500 entries)
* Clean uninstall command — removes scheduler task before uninstalling
* Version check command — shows installed version and detects available updates

---

### 🌐 Reliability Layer

* Internet availability check (retry up to 2 minutes)
* Automatic admin privilege escalation
* Resilient Git operations with fallback handling

</details>

---

## ⚙️ How It Works

1. Detects changes in tracked repositories
2. Syncs with remote using `git pull`
3. Analyzes `git diff` using Gemini AI
4. Generates a contextual commit message
5. Runs security checks (Secret Shield)
6. Commits and pushes changes
7. Stores a backup snapshot

All of this runs automatically in the background.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* Git installed and configured
* (Recommended) Gemini API Key → https://aistudio.google.com/app/apikey

---

## 📦 Installation

### Option 1: From Source

```bash
git clone https://github.com/RohitKSahoo/auto-commit-bot.git
cd auto-commit-bot
pip install -e .
```

### Option 2: Via pip (Recommended)

```bash
pip install autocommitbot
```

---

## 🛠️ Usage

All commands follow the pattern: `autocommit <command>`

> Run `autocommit <command> --help` for full details on any command.

### ⚙️ Setup & Config

| Command | What it does |
|---|---|
| `autocommit setup` | First-time wizard: repos, schedule & AI |
| `autocommit set-schedule` | Change when the bot runs |
| `autocommit config-backup <days>` | Set how long backups are kept |

### 📁 Repositories

| Command | What it does |
|---|---|
| `autocommit add [path]` | Track a new local git repo |
| `autocommit remove` | Stop tracking a repo |
| `autocommit status` | List all tracked repos |

### 🔁 Automation

| Command | What it does |
|---|---|
| `autocommit run` | Commit & push all changes now |
| `autocommit enable` | Register the Windows auto-start task |
| `autocommit disable` | Remove the Windows auto-start task |

### 📊 History & System

| Command | What it does |
|---|---|
| `autocommit dashboard` | View commit history & stats |
| `autocommit restore` | Roll back a bot commit from snapshot |
| `autocommit version` | Check installed version & updates |
| `autocommit uninstall` | Remove scheduler task then pip uninstall |

---

### ⚠️ Notes

* Automation runs only on tracked repositories
* `restore` performs a **force push** — rewrites remote history, use with caution
* `run` is for manual triggering, not regular use
* Internet connection required for push, version check, and AI commit messages
* Always use `autocommit uninstall` instead of `pip uninstall` directly — running pip uninstall alone will leave an orphaned task in Windows Task Scheduler that silently fails on every trigger


---

## 🔄 Staying Up to Date

Run the following command to check your current version and see if a newer release is available:

```bash
autocommit version
```

Example output when up to date:
```
AutoCommitBot  v1.1.6
Checking for updates...
✔ You are on the latest version (1.1.6).
```

Example output when an update is available:
```
AutoCommitBot  v1.1.5
Checking for updates...
⚡ New version available: 1.1.6 (you have 1.1.5)
Run to update:  pip install --upgrade autocommitbot
```

To update manually at any time:

```bash
pip install --upgrade autocommitbot
```

---


## 🔐 Security Notes

* Your code is **not stored externally** (only analyzed for commit messages)
* Sensitive files are automatically excluded via `.gitignore`
* `restore` uses **force push** — use with caution

---

## 🆘 Support & Contributions

* Report issues: https://github.com/RohitKSahoo/auto-commit-bot/issues
* Contributions welcome (see `CONTRIBUTING.md`)
* Additional docs in `/docs`

---

## 👤 Maintainer

Maintained by **[@RohitKSahoo](https://github.com/RohitKSahoo)**

---

## 📄 License

Licensed under the MIT License. See `LICENSE` for details.

---

## 🧾 TL;DR

AutoCommitBot is not just automation—
it’s a **smart Git workflow layer with AI, security, and recovery built in**.
