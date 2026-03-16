# Notes API (for agents)

The `memo notes api` subcommand provides non-interactive, machine-friendly operations for scripts and AI agents. All commands:

- Bypass the notes cache (fresh data every time)
- Output plain text in well-parsable formats
- Use no prompts, colored messages, or interactive dialogs
- Support stable note IDs from Apple Notes

Run `memo notes api --help` for the full command list.

## Commands

| Command | Description |
|---------|-------------|
| `list` | List notes with id, folder, title (TSV, lines, or JSON) |
| `show` | Output note body as Markdown |
| `edit` | Replace note body from stdin |
| `add` | Create note from stdin |
| `delete` | Delete a note by ID |
| `move` | Move note to another folder |
| `folders` | List folders and subfolders |
| `search` | Search notes by substring match |
| `remove` | Delete a folder (requires `--force`) |
| `export` | Export all notes to a directory |

## Output formats

For `list`, `folders`, and `search`:

- `tsv` (default): Tab-separated values
- `lines`: Pipe-separated (`id|folder|title`)
- `json`: NDJSON, one object per line

## Examples

```bash
# List notes in folder
memo notes api list -f "Work"

# List with JSON output
memo notes api list --format json

# Show note content
memo notes api show x-coredata://.../ICNote/p123

# Edit note from file
memo notes api edit x-coredata://.../ICNote/p123 < note.md

# Create note
echo "# Title" | memo notes api add -f "Work"

# Search notes
memo notes api search "meeting" --body
```

## Stdin behavior

`edit` and `add` read content from stdin when it is not a TTY (e.g. pipe or redirect). When run interactively with no input, they exit with an error.
