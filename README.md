# 🚀 AutoCommitBot (v1.1.5)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license)
[![GitHub activity](https://img.shields.io/badge/github-automated-orange.svg)](https://github.com/RohitKSahoo/auto-commit-bot)

**Maintain a professional GitHub presence with AI-powered automation and built-in security.**

AutoCommitBot is an intelligent, cross-platform CLI tool designed for developers who want to maintain a consistent contribution history without the manual overhead. It monitors your local repositories, creates smart commit messages using Google's Gemini AI, and handles the entire push-pull-merge lifecycle seamlessly.

---

## 🌟 Why AutoCommitBot?

*   **🤖 AI-Powered Commit Messages**: No more "Update file.py." The bot analyzes your code `diff` with Gemini AI to generate natural, descriptive commit messages.
*   **🛡️ "Secret Shield" Security**: Built-in protection that automatically updates `.gitignore` and un-tracks sensitive files (like `.env`, `config.json`, or API keys) if they were accidentally staged.
*   **🕒 Natural Activity Mode**: Mimics human behavior by skipping random days and varying commit times to avoid looking like a scripted bot.
*   **🔄 Universal Undo**: A "Time Machine" feature that takes full ZIP backups before every commit. You can roll back both local files and GitHub state with a single command.
*   **💻 Windows Native**: Integrated with Windows Task Scheduler to start automatically on logon.

---

## ✨ Features

### Smart Commits
- **Multi-Model Support**: Automatically detects and falls back between Gemini 2.0 Flash, 1.5 Flash, and Pro models.
- **Robust Sync**: Automatically handles `git pull` and merge conflicts if remote changes are detected.

### Security & Privacy
- **Automatic `.gitignore` Healing**: Proactively adds sensitive patterns like `*.key`, `*.pem`, and `secrets.json`.
- **Credential Scanner**: Warns you if an API key pattern is detected inside your code changes before pushing.

### User Experience
- **Interactive Setup**: A friendly wizard that guides you through API keys, scheduling, and repository selection.
- **Visual Dashboard**: Beautiful terminal tables displaying your history, commit frequency, and bot status.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher.
- Git installed and configured globally.
- (Recommended) A [Google Gemini API Key](https://aistudio.google.com/app/apikey).

### Installation

1. **Clone the project:**
   ```bash
   git clone https://github.com/RohitKSahoo/auto-commit-bot.git
   cd auto-commit-bot
   ```

2. **Install the package:**
   ```bash
   pip install -e .
   ```

### First Time Setup

Run the interactive wizard to configure your bot:
```bash
autocommit setup
```
Follow the prompts to add your repositories, choose your schedule, and paste your Gemini API key.

---

## 🛠️ Usage

### Common Commands

| Command | Description |
| :--- | :--- |
| `autocommit setup` | Launch the configuration wizard. |
| `autocommit add [path]` | Quickly add a new repository to tracking. |
| `autocommit run` | Force an immediate scan and commit cycle. |
| `autocommit dashboard` | View your commit history and bot statistics. |
| `autocommit status` | List all repositories currently being managed. |
| `autocommit restore` | Choose a past snapshot and roll back local/remote states. |
| `autocommit enable/disable` | Manage the background logon task. |

### Adding a Repository Quickly
```bash
# In the repository you want to add:
autocommit add .
```

---

## 🆘 Support & Contributions

- **Issues**: If you find a bug or have a feature request, please [submit an issue](https://github.com/RohitKSahoo/auto-commit-bot/issues).
- **Contribute**: Pull requests are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
- **Documentation**: More detailed docs can be found in the [docs/](docs/) directory.

---

## 👤 Maintainers

Maintained by **[@RohitKSahoo](https://github.com/RohitKSahoo)**. Contributions are always welcome!

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
