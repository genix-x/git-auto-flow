# Git Auto-Flow v2.0

[![version](https://img.shields.io/badge/version-2.0-blue)](https://github.com/user/project/releases)
[![ci](https://img.shields.io/github/actions/workflow/status/user/project/test-build.yml?branch=main)](https://github.com/user/project/actions)
[![downloads](https://img.shields.io/github/downloads/user/project/total)](https://github.com/user/project/releases)

> Boost your Git productivity with AI-powered commands.

---

### 🚀 Quick Install & Setup (30 seconds)

1.  **Install**
    ```bash
    curl -sL https://raw.githubusercontent.com/genix-x/git-auto-flow/main/install.sh | bash
    ```

2.  **Verify Installation**
    ```bash
    gitautoflow version
    ```
    *Expected output:* `gitautoflow version 2.0.0`

3.  **Next Steps: Authenticate**
    For AI features, set your API key. The tool will prompt you on first use.
    ```bash
    # Example: The first AI command will trigger the key setup
    gitautoflow issues suggest "Refactor login page"
    ```

---

### Table of Contents

- [Core Features](#core-features)
- [Simplified Workflow](#simplified-workflow)
- [Advanced Usage](#advanced-usage)

---

### ✨ Core Features

Here are the essential commands to get you started.

| Command | Description | Example |
| :--- | :--- | :--- |
| `repo create` | Create a new repository on GitHub. | `gitautoflow repo create my-new-project --private` |
| `issues suggest` | Get AI-powered suggestions for an issue. | `gitautoflow issues suggest "Implement dark mode"` |
| `features start` | Start a new feature branch from an issue. | `gitautoflow features start 123` |
| `prs create` | Create a pull request with an AI-generated description. | `gitautoflow prs create` |
| `version` | Check the installed version. | `gitautoflow version` |
| `--help` | Get help on any command. | `gitautoflow features --help` |

---

### Workflow Example: From Issue to PR

A simple, 3-step workflow to ship a feature.

1.  **Start a Feature from an Issue**
    ```bash
    # Creates a new branch 'feature/15-add-user-authentication'
    gitautoflow features start 15
    ```

2.  **Code & Commit Your Changes**
    ```bash
    # Your usual git workflow
    git add .
    git commit -m "feat: implement user authentication endpoint"
    ```

3.  **Create a Pull Request**
    The tool uses AI to generate a title and description from your commits.
    ```bash
    gitautoflow prs create
    ```

---

### 🛠️ Advanced Usage

<details>
<summary><strong>Install a Specific Version</strong></summary>

You can install a specific version of `git-auto-flow` by passing the version number to the install script.

```bash
# Example: To install a specific version (e.g., 1.5.0), use the -v flag.
curl -sL https://raw.githubusercontent.com/genix-x/git-auto-flow/main/install.sh | bash -s -- -v 1.5.0
```
</details>

<details>
<summary><strong>Developer Installation</strong></summary>

If you want to contribute to the project, you can install it in editable mode.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/OusamaBenyounes/git-auto-flow.git
    cd git-auto-flow
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install in editable mode:**
    ```bash
    pip install -e .
    ```
4.  **Verify your local installation:**
    ```bash
    gitautoflow version
    ```
</details>

<details>
<summary><strong>Advanced Configuration</strong></summary>

Configuration is handled via environment variables or a `.env` file in your project root.

-   `AI_PROVIDER`: Set your preferred AI provider (`gemini` or `groq`).
-   `GEMINI_API_KEY`: Your Google Gemini API key.
-   `GROQ_API_KEY`: Your Groq API key.
-   `GITHUB_TOKEN`: Your GitHub Personal Access Token for repository operations.

Example `.env` file:
```
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=ghp_your_github_token_here
```
</details>

<details>
<summary><strong>Troubleshooting</strong></summary>

-   **Command not found:** If your shell can't find `gitautoflow`, make sure `~/.local/bin` is in your `PATH`. Add `export PATH="$HOME/.local/bin:$PATH"` to your `.bashrc`, `.zshrc`, or equivalent shell profile file.
-   **Authentication issues:** Ensure your `GITHUB_TOKEN` has the correct permissions (e.g., `repo`, `workflow`).
-   **Check for help:** Use the `--help` flag for detailed command options: `gitautoflow --help` or `gitautoflow features --help`.
</details>