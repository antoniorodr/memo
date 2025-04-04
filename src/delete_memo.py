import subprocess
import click


def delete_note(note_id):
    script = f"""
        tell application "Notes"
            set selectedNote to first note whose id is "{note_id}"
            delete selectedNote
        end tell
    """

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode == 0:
        click.echo("\nNote deleted successfully.")
    else:
        click.echo(f"Error: {result.stderr}")
