import subprocess
import click
import tempfile
import mistune
import os


def add_note(folder_name):
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
        temp_file.write(b"# New Note\n\nWrite your note here...")
        temp_file_path = temp_file.name

    editor = os.getenv("EDITOR", "vim")
    subprocess.run([editor, temp_file_path])

    with open(temp_file_path, "r", encoding="utf-8") as file:
        note_md = file.read().strip()

    if not note_md or note_md == "# New Note\n\nWrite your note here...":
        click.echo("\nNote creation cancelled.")
        os.remove(temp_file_path)
        return

    note_html = mistune.markdown(note_md)

    script = f"""
        tell application "Notes"
            set targetFolder to first folder whose name is "{folder_name}"
            tell targetFolder
                make new note with properties {{name:"New Note", body:"{note_html}"}}
            end tell
        end tell
        """

    process = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )

    os.remove(temp_file_path)

    if process.returncode == 0:
        click.echo(f"\nNote created in '{folder_name}' folder.")
    else:
        click.echo("\nError: Could not create note. Check if the folder exists.")
