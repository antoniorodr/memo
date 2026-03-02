:heavy_check_mark: **Image support:** When editing notes with images, inline images are preserved through the edit cycle. Images appear as `[MEMO_IMG_N]` placeholders in your editor — keep them to preserve images, or remove them to delete images.

:warning: Due to AppleScript limitations, the images will be preserved at the end of the note, regardless of where the placeholder is located in the text. This means that if you have images in your note, they will be moved to the end of the note after editing.

Use the command `memo notes --help` to see all the options available for notes.

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
  -s, --search       Fuzzy search your notes.
  -r, --remove       Remove the folder you specified.
  -ex, --export      Export your notes to the Desktop.
  -v, --view INTEGER Display the content of note N from the list.
  --help             Show this message and exit.
```

Use the command `memo rem --help` to see all the options available for reminders.

```bash
memo rem --help
Usage: memo rem [OPTIONS]

Options:
  -c, --complete  Mark a reminder as completed.
  -a, --add       Add a new reminder.
  -d, --delete    Delete a reminder.
  --help          Show this message and exit.
```

You can use `memo --help` to see the available commands.

```bash
memo --help
Usage: memo [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  notes
  rem
```

Memo uses `$EDITOR` to edit and add notes. You can set it up by running the following command:

```bash
export EDITOR="vim"
```

Where `vim` can be replaced with your preferred editor. Add it to your .zshrc/.bashrc to make it permanent.

Or check the one you have set up in your terminal by running:

```bash
echo $EDITO
```
