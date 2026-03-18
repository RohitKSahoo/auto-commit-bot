# 🚀 AutoCommitBot (v1.1.5)

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

* 🤖 **AI-Powered Commit Messages** — No more "Update file.py." Generates contextual, human-like commits
* 🛡️ **Secret Shield Security** — Prevents accidental leaks of `.env`, API keys, configs
* 🕒 **Natural Activity Mode** — Mimics real developer behavior (no bot patterns)
* 🔄 **Universal Undo** — Full rollback with local + GitHub sync
* 💻 **Windows Native Automation** — Runs automatically on system login

---

## ✨ Features

### Smart Commits

* **Multi-Model Support**: Gemini 2.0 Flash, 1.5 Flash, and Pro fallback support
* **Robust Sync**: Handles `git pull`, merges, and conflict resolution automatically

### Security & Privacy

* **Auto `.gitignore` Healing**: Adds sensitive patterns like `*.key`, `.env`, `secrets.json`
* **Credential Scanner**: Detects API keys before pushing

### User Experience

* **Interactive Setup Wizard**
* **Visual Dashboard** with commit stats and activity insights

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

## 🧠 Example Commit

**Input (diff):**

```diff
+ Added validation in login form
```

**Generated commit:**

```bash
feat(auth): add input validation for login form
```

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

### Common Commands

| Command                     | Description                 |
| --------------------------- | --------------------------- |
| `autocommit setup`          | Launch configuration wizard |
| `autocommit add [path]`     | Add a repository            |
| `autocommit run`            | Force commit cycle          |
| `autocommit dashboard`      | View stats                  |
| `autocommit status`         | Show tracked repos          |
| `autocommit restore`        | Rollback changes            |
| `autocommit enable/disable` | Manage background task      |

---

### Quick Add Example

```bash
autocommit add .
```

---

## 🔐 Security Notes

* Your code is **not stored externally** (only analyzed for commit messages)
* Sensitive files are automatically excluded via `.gitignore`
* `restore` uses **force push** — use with caution

---

## ❓ FAQ

**Does it work without Gemini API?**
Yes, but commit messages will be basic.

**Will it spam commits?**
No. Natural Mode ensures realistic activity patterns.

**Can I disable automation?**
Yes:

```bash
autocommit disable
```

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
