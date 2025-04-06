<div align="center" id="top">
  <img height=200px src="./.github/Memo.png" alt="memo" />

&#xa0;

  <!-- <a href="https://memo.netlify.app">Demo</a> -->
</div>

<h1 align="center">memo</h1>

<p align="center">
  <img alt="Github top language" src="https://img.shields.io/github/languages/top/antoniorodr/memo?color=56BEB8">

  <img alt="Github language count" src="https://img.shields.io/github/languages/count/antoniorodr/memo?color=56BEB8">

  <img alt="Repository size" src="https://img.shields.io/github/repo-size/antoniorodr/memo?color=56BEB8">

  <img alt="License" src="https://img.shields.io/github/license/antoniorodr/memo?color=56BEB8">

  <img alt="Github issues" src="https://img.shields.io/github/issues/antoniorodr/memo?color=56BEB8" />

  <img alt="Github forks" src="https://img.shields.io/github/forks/antoniorodr/memo?color=56BEB8" />

  <img alt="Github stars" src="https://img.shields.io/github/stars/antoniorodr/memo?color=56BEB8" />

</p>

 <h4 align="center">
 🚧  memo 🚀 Under development...  🚧
</h4>

<hr>

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0;
  <a href="#computer-demo">Demo</a> &#xa0; | &#xa0;
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-installation">Installation</a> &#xa0; | &#xa0;
  <a href="#bookmark_tabs-documentation">Documentation</a> &#xa0; | &#xa0;
  <a href="#pushpin-roadmap">Roadmap</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="https://github.com/antoniorodr" target="_blank">Author</a>
</p>

<br>

## :dart: About

CLI app to manage your Apple Notes and Apple reminders (not implemented yet).

## :computer: Demo

<a href="https://asciinema.org/a/pNryTkFEJPmojjl5iueitd75S" target="_blank">
  <img src="https://asciinema.org/a/pNryTkFEJPmojjl5iueitd75S.svg" alt="asciicast">
</a>

## :sparkles: Features

:heavy_check_mark: View your notes directly from the terminal\
:heavy_check_mark: Edit your notes right from the terminal\
:heavy_check_mark: Add new notes effortlessly through the terminal\
:heavy_check_mark: Move notes to another folder effortlessly through the terminal

## :rocket: Technologies

The following tools were used in this project:

- [Click](https://click.palletsprojects.com/en/stable/)
- [Mistune](https://mistune.lepture.com/en/latest/)
- [html2text](https://pypi.org/project/html2text/)

## :checkered_flag: Installation

#### Manual Installation

```bash
git clone https://github.com/antoniorodr/memo

cd memo

pip install .
```

#### Homebrew Installation

```bash
brew tap antoniorodr/memo
brew install antoniorodr/memo/memo
```

## :bookmark_tabs: Documentation

Use the command `memo notes --help` to see all the options available.

```bash
memo notes --help
Usage: memo notes [OPTIONS]

Options:
  -f, --folder TEXT  Specify a folder to filter the notes (leave empty to get
                     all).
  -a, --add          Add a note to the specified folder. Specify a folder
                     using the --folder flag.
  -e, --edit         Edit a note in the specified folder. Specify a folder
                     using the --folder flag.
  -d, --delete       Delete a note in the specified folder. Specify a folder
                     using the --folder flag.
  -m, --move         Move a note to a different folder.
  -fl, --flist       List all the folders and subfolders.
  --help             Show this message and exit.
```

Memo uses `$EDITOR` to edit and add notes. You can set it up by running the following command:

```bash
export EDITOR="vim"
```

Where `vim` can be replaced with your preferred editor.

Or check the one you have set up in your terminal by running:

```bash
echo $EDITOR
```

## :pushpin: Roadmap

- Add a search flag powered by fuzzy search
- Possibility to remove a folder
- Add support for Apple reminders
- Write tests

## :memo: License

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.

## :eyes: Do you like my work?

<a href="https://www.buymeacoffee.com/antoniorodr" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-white.png" alt="Buy Me A Coffee" height="48"></a>

Made with :heart: by <a href="https://github.com/antoniorodr" target="_blank">Antonio Rodriguez</a>

&#xa0;

<a href="#top">Back to top</a>
