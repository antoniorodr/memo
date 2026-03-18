import subprocess
import click
import tempfile
import mistune
import os
import sys
from datetime import datetime


def _escape_applescript_string(s):
    """Escape a string for safe embedding in an AppleScript double-quoted string."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def add_note(folder_name, title=None, body=None):
    """Create a note in the given Notes folder.

    When *title* and/or *body* are provided the editor is skipped entirely,
    making the function safe to call from non-interactive environments such as
    shell pipelines or AI agents.

    If neither argument is supplied and stdin is not a TTY (i.e. content is
    being piped in), the piped text is treated as Markdown and used directly.

    Falls back to opening ``$EDITOR`` when running interactively with no
    arguments.
    """
    if title is not None or body is not None:
        # Non-interactive: build note from provided arguments.
        note_title = title if title is not None else "Untitled"
        note_body = body if body is not None else ""
        note_md = f"# {note_title}\n\n{note_body}" if note_body else f"# {note_title}"
    elif not sys.stdin.isatty():
        # Stdin is a pipe: treat the piped text as Markdown.
        note_md = sys.stdin.read().strip()
        if not note_md:
            click.echo("\nNote creation cancelled.")
            return
    else:
        # Interactive fallback: open the user's preferred editor.
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
            temp_file.write(b"# Your note title\n\nWrite your note here...")
            temp_file_path = temp_file.name

        editor = os.getenv("EDITOR", "vim")
        subprocess.run([editor, temp_file_path])

        with open(temp_file_path, "r", encoding="utf-8") as file:
            note_md = file.read().strip()

        os.remove(temp_file_path)

        if not note_md or note_md == "# Your note title\n\nWrite your note here...":
            click.echo("\nNote creation cancelled.")
            return

    note_html = mistune.markdown(note_md)
    escaped_html = _escape_applescript_string(note_html)

    script = f"""
        tell application "Notes"
            set targetFolder to first folder whose name is "{folder_name}"
            tell targetFolder
                make new note with properties {{body:"{escaped_html}"}}
            end tell
        end tell
        """

    process = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )

    if process.returncode == 0:
        click.echo(f"\nNote created in '{folder_name}' folder.")
    else:
        click.echo("\nError: Could not create note. Check if the folder exists.")


def add_reminder():
    title = click.prompt("\nEnter the title of the reminder")
    date = click.prompt("Enter the due date (YYYY-MM-DD)")
    time = click.prompt("Enter the due time (HH:MM)")
    datetime_str = f"{date} {time}"
    due_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

    year = due_dt.year
    month = due_dt.month
    day = due_dt.day
    hour = due_dt.hour
    minute = due_dt.minute

    script = f'''
    tell application "Reminders"
        set theDate to current date
        set year of theDate to {year}
        set month of theDate to {month}
        set day of theDate to {day}
        set time of theDate to ({hour} * hours + {minute} * minutes)
        make new reminder with properties {{name:"{title}", due date:theDate}}
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode == 0:
        click.secho(f"\nReminder '{title}' added successfully.", fg="green")
    else:
        click.secho(f"\nError: Could not add reminder, {result.stderr}", fg="red")
