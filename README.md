<a id="memo"></a>

![memo](./.github/Memo.png)

> [!caution]
> **Status:** Under development

## ℹ️ About

**Memo** is a Python CLI for managing Apple Notes and Apple Reminders from the terminal. It is built for a keyboard-driven workflow, so you can browse, read, edit, move, export, and complete items without leaving your shell.

Memo is also used by [OpenClaw](https://github.com/openclaw/openclaw/blob/main/skills/apple-notes/SKILL.md).

Full documentation is available at [antoniorodr.github.io/memo](https://antoniorodr.github.io/memo).

## 🎬 Demo

![Memo demo](./.github/memo.gif)

## ✨ Features

- View notes and reminders directly from the terminal
- Read note content as clean Markdown
- Add and edit notes without leaving your editor
- Move notes between folders and browse subfolders
- Search notes with fuzzy matching
- Mark reminders as completed from the CLI
- Export notes to HTML and convert them to Markdown

## 🛠️ Technologies

The project is built with:

- [Python](https://www.python.org/)
- [Click](https://click.palletsprojects.com/en/stable/)
- [Mistune](https://mistune.lepture.com/en/latest/)
- [html2text](https://pypi.org/project/html2text/)
- [chardet](https://pypi.org/project/chardet/)

## 📋 Requirements

Before starting, make sure the required tools and dependencies are installed on your machine:

```bash
python3.13 --version
echo $EDITOR
```

Memo depends on Apple Notes, Apple Reminders, and AppleScript, so it is intended for macOS. For manual and `uv` installs, Python 3.13 or newer is required.

If you want to add or edit notes from the CLI, set `$EDITOR` to your preferred terminal editor.

## 📦 Installation

### Manual installation

```bash
git clone https://github.com/antoniorodr/memo
cd memo
pip install .
```

### Homebrew installation

```bash
brew tap antoniorodr/memo
brew install antoniorodr/memo/memo
```

### Installation with [uv](https://docs.astral.sh/uv/)

```bash
uv tool install git+https://github.com/antoniorodr/memo
```

## 🚀 Getting Started

Once installed, set your editor and inspect the available commands:

```bash
export EDITOR="vim"
memo --help
memo notes --help
memo rem --help
```

Use `memo notes` to work with Apple Notes and `memo rem` to manage Apple Reminders from the terminal.

> [!NOTE]
> When editing notes with images, Memo preserves them by inserting `[MEMO_IMG_N]` placeholders into the text shown in your editor. Keep a placeholder to preserve the corresponding image, or remove it to delete that image.

> [!IMPORTANT]
> Because of AppleScript limitations, preserved images are appended to the end of the note after editing, even if their placeholders appear elsewhere in the text.

For full usage details and examples, see the [documentation site](https://antoniorodr.github.io/memo).

## ❤️ Do you like my work?

If you find the project useful, you can support the author here:

[![GitHub Sponsor](https://img.shields.io/badge/Sponsor_on_GitHub-30363D?logo=github&style=for-the-badge)](https://github.com/sponsors/antoniorodr)

[Back to top](#memo)
