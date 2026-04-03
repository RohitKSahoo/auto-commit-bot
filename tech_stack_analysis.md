# Project Tech Stack Analysis: AutoCommitBot

A comprehensive breakdown of the technologies, libraries, and architectural patterns used in the **AutoCommitBot** codebase.

## 💻 Languages
*   **Python (Primary)**: Core logic, CLI development, and AI integration (>= 3.8).
*   **PowerShell**: System-level automation, Windows Task Scheduler configuration, and environment stabilization.
*   **Batch/CMD**: Invoked for privilege elevation (UAC) and legacy system interactions.

## 🛠 Frameworks & Libraries
*   **Typer**: High-performance CLI framework for command routing and help generation.
*   **Rich**: Powering the advanced terminal UI, including tables, progress logs, and colored output.
*   **Requests**: Robust HTTP client used for Gemini AI API calls and PyPI update checks.
*   **GitPython**: Direct interaction with the Git engine for staging, committing, and pushing.
*   **Questionary**: Interactive wizard-style prompts for user configuration.
*   **Pyfiglet**: ASCII art generation for the application banner.
*   **Ctypes**: Windows-specific library for checking and requesting administrative privileges.

## ⚙️ Tools & Platforms
*   **GitHub CLI (`gh`)**: The primary authentication layer; the bot trusts the active `gh` session for repository access.
*   **Windows Task Scheduler**: Background execution engine using `schtasks` for persistent automation.
*   **Git**: The underlying version control system.
*   **Google Gemini AI Platform**: Infrastructure for intelligent commit message generation.
*   **PyPI**: Packaging and update distribution platform.
*   **Setuptools**: Build system for package distribution.

## 🗄 Databases & Storage
*   **JSON Persistent Storage**: 
    *   `config.json`: Stores user preferences, tracked repositories, and API keys.
    *   `history.json`: Auditable log of every automated commit and system operation.
*   **ZIP Snapshots**: Automated binary backups of codebases before bot commits to ensure zero-loss recovery.

## 🏗 Architecture & Concepts
*   **CLI-First Design**: Modular command structure (`setup`, `run`, `dashboard`, `restore`).
*   **Background Agent**: Uses PowerShell-wrapped task scheduling to survive reboots and logons.
*   **Secret Shield (Security Architecture)**: 
    *   Regex-based scanning for API keys (e.g., Google/OpenAI keys).
    *   Automatic `.gitignore` injection and file untracking.
*   **Snapshot-Based Recovery**: State-based rollback mechanism that allows users to undo bot actions locally and on GitHub.
*   **Smart Activity Simulation**: 
    *   **Natural Activity Mode**: Probability-based commit triggers to simulate human work rhythms.
    *   **Logon Triggers**: Immediate synchronization upon system startup.

## 🤖 AI/ML Components
*   **Generative AI Integration**:
    *   **Models**: Gemini 1.5 Flash, 2.0 Flash, and Gemini Pro.
    *   **Logic**: Multi-model fallback strategy—tries the latest models first, falling back to stable ones if unavailable.
    *   **Contextual Analysis**: Parses `git diff` outputs to generate structured, bulleted commit messages.

## 🔌 APIs & Integrations
*   **Google Gemini API**: RESTful integration for content generation.
*   **GitHub API**: Accessed via `gh api` for user identity and repository metadata.
*   **PyPI JSON API**: For version checking and update notifications.
*   **Google DNS (8.8.8.8)**: Low-level socket check for internet availability.
