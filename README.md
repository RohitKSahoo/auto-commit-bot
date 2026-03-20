# 🚀 AutoCommitBot (v1.2.4)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license)
[![GitHub activity](https://img.shields.io/badge/github-automated-orange.svg)](https://github.com/RohitKSahoo/auto-commit-bot)

**Maintain a professional GitHub presence with AI-powered automation and built-in security.**

AutoCommitBot is an intelligent, cross-platform CLI tool designed for developers who want to maintain a consistent contribution history without the manual overhead. It monitors your local repositories, generates meaningful commit messages using Google's Gemini AI, and manages the full Git lifecycle automatically.

---

## 🖥️ Preview

<p align="center">
  <img src="assets/CLI.png" alt="AutoCommitBot CLI" width="750"/>
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
* **Dashboard & Analytics** — CLI-based insights into commit history and activity
* **Execution Reliability** — Built-in retry logic, conflict handling, and network checks and much more... Check Below 👇🏻


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

* Logon trigger (Windows Task Scheduler) — **5/day cap on random activity only; real code changes always push through**
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
* **AI Key Validation** — Real-time verification of your API key during setup
* Model fallback chain: 2.5 Flash → 2.0 Flash → 1.5 Flash → Pro
* Diff truncation for large inputs (8000 chars)

---

### 💾 Backup & Restore

* ZIP snapshot before every commit
* Configurable backup retention (`config-backup`)
* Restore command with snapshot selection
* Automatic GitHub rollback via force push
* Clear all backups on demand (`clear-backups`)

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
| `autocommit setup` | First-time wizard, **or** edit repos / schedule / AI |
| `autocommit config-backup <days>` | Set how long backups are kept |

> **Tip:** Running `autocommit setup` again on a configured machine shows a short menu so you can update just one section (Repositories, Schedule, or AI key) without repeating the full wizard.

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
| `autocommit clear-backups` | Delete all backup snapshots to free disk space |
| `autocommit version` | Check installed version & updates |
| `autocommit uninstall` | Remove scheduler task then pip uninstall |

---

### ⚠️ Notes

* Automation runs only on tracked repositories
* `restore` performs a **force push** — rewrites remote history, use with caution
* `run` is for manual triggering, not regular use
* Internet connection required for push, version check, and AI commit messages
* **On Logon mode** caps **random activity** at 5 per calendar day — real code changes always push through, even after the cap is reached
* Always use `autocommit uninstall` instead of `pip uninstall` directly — running pip uninstall alone will leave an orphaned task in Windows Task Scheduler that silently fails on every trigger


---

## 🔄 Staying Up to Date

Run the following command to check your current version and see if a newer release is available:

```bash
autocommit version
```

Example output when up to date:
```
AutoCommitBot  v1.2.4
Checking for updates...
✔ You are on the latest version (1.2.4).

🎉 New in this version (v1.2.4):
  • Smart daily limit — real code changes always push, 5/day cap only applies to random activity commits
  • "What's New" display — see what changed after updating the bot
  • CHANGELOG.md — full version history now tracked in the repository
```

Example output when an update is available:
```
AutoCommitBot  v1.2.3
Checking for updates...
⚡ New version available: 1.2.4 (you have 1.2.3)

📋 What's New in v1.2.4:
  • Smart daily limit — real code changes always push, 5/day cap only applies to random activity commits
  • "What's New" display — see what changed after updating the bot
  • CHANGELOG.md — full version history now tracked in the repository

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

This project is licensed under the GNU General Public License v3.0.

You are free to use, modify, and distribute this software under the terms of the license. Any derivative work must also be open-sourced under GPL v3.

See the LICENSE file for full details.

---

## 🧾 TL;DR

AutoCommitBot is a smart Git automation layer with AI, security, and recovery built in.
it’s a **smart Git workflow layer with AI, security, and recovery built in**.
