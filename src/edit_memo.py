import subprocess
import click
import tempfile
import html2text
import mistune
import os


def edit_note(note_id):
    script = f"""
        tell application "Notes"
            set selectedNote to first note whose id is "{note_id}"
            return body of selectedNote
        end tell
        """
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    original_html = result.stdout.strip()

    text_maker = html2text.HTML2Text()
    text_maker.body_width = 0
    original_md = text_maker.handle(original_html).strip()

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
        temp_file.write(original_md.encode("utf-8"))
        temp_file_path = temp_file.name

    if "<img" in original_html or "<enclosure" in original_html:
        click.secho(
            "⚠️  Warning: This note contains images or attachments that could be lost!",
            fg="yellow",
        )
    if not click.confirm("Do you still want to continue editing the note?"):
        return

    editor = os.getenv("EDITOR", "vim")
    subprocess.run([editor, temp_file_path])

    with open(temp_file_path, "r", encoding="utf-8") as file:
        edited_md = file.read().strip()

    if edited_md == original_md:
        click.echo("\nNo changes made.")
        return

    edited_html = mistune.markdown(edited_md)

    update_script = f"""
        tell application "Notes"
            set selectedNote to first note whose id is "{note_id}"
            set body of selectedNote to "{edited_html}"
        end tell
        """
    subprocess.run(["osascript", "-e", update_script])
    click.echo("\nNote updated.")
