import subprocess
import click
import tempfile
import mistune
import os
import datetime
from memo_helpers.id_search_memo import id_search_memo
from memo_helpers.md_converter import md_converter


def edit_note(note_id):
    result = id_search_memo(note_id)
    original_md, original_html = md_converter(result)

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
        temp_file.write(original_md.encode("utf-8"))
        temp_file_path = temp_file.name

    if "<img" in original_html or "<enclosure" in original_html:
        click.secho(
            "\n⚠️  Warning: This note contains images or attachments that could be lost!",
            fg="yellow",
        )
        if not click.confirm("\nDo you still want to continue editing the note?"):
            return

    editor = os.getenv("EDITOR", "vim")
    subprocess.run([editor, temp_file_path])

    with open(temp_file_path, "r", encoding="utf-8") as file:
        edited_md = file.read().strip()

    if edited_md == original_md:
        click.secho("\nNo changes made.", fg="yellow")
        return

    edited_html = mistune.markdown(edited_md)

    update_script = f"""
        tell application "Notes"
            set selectedNote to first note whose id is "{note_id}"
            set body of selectedNote to "{edited_html}"
        end tell
        """
    subprocess.run(["osascript", "-e", update_script])
    click.secho("\nNote updated.", fg="green")


def edit_reminder(reminder_id, part_to_edit):
    if part_to_edit == "title":
        new_title = click.prompt("\nEnter the new title")
        script = f"""
            tell application "Reminders"
                set selectedReminder to first reminder whose id is "{reminder_id}"
                set name of selectedReminder to "{new_title}"
            end tell
            """
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        if result.returncode == 0:
            click.secho("\nReminder title updated.", fg="green")
        else:
            click.secho("\nError: Could not update reminder title.", fg="red")
    if part_to_edit == "due date":
        new_date = click.prompt("\nEnter the new date (YYYY-MM-DD)")
        new_time = click.prompt("\nEnter the new time (HH:MM)")
        datetime_str = f"{new_date} {new_time}"
        due_dt = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        year = due_dt.year
        month = due_dt.month
        day = due_dt.day
        hour = due_dt.hour
        minute = due_dt.minute

        script = f"""
        tell application "Reminders"
            set selectedReminder to first reminder whose id is "{reminder_id}"
            set dueDate to current date
            set year of dueDate to {year}
            set month of dueDate to {month}
            set day of dueDate to {day}
            set time of dueDate to ({hour} * hours + {minute} * minutes)
            set due date of selectedReminder to dueDate
        end tell
        """

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        if result.returncode == 0:
            click.secho("\nReminder date updated.", fg="green")
        else:
            click.secho("\nError: Could not update reminder date.", fg="red")
