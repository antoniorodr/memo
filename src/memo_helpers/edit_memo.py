import subprocess
import click
import tempfile
import mistune
import os
import re
import base64
import datetime
from memo_helpers.id_search_memo import id_search_memo
from memo_helpers.md_converter import md_converter


def _decode_image_to_tempfile(img_html):
    """Extract base64 data from an <img> HTML block and write to a temp file."""
    match = re.search(r'src="data:image/(\w+);base64,([^"]+)"', img_html)
    if not match:
        return None
    ext = match.group(1)
    data = base64.b64decode(match.group(2))
    fd, path = tempfile.mkstemp(suffix=f".{ext}")
    os.write(fd, data)
    os.close(fd)
    return path


def _reattach_images(note_id, surviving_images):
    """Delete orphaned attachments and re-add surviving images."""
    subprocess.run(
        [
            "osascript",
            "-e",
            f"""
        tell application "Notes"
            set n to first note whose id is "{note_id}"
            repeat while (count of attachments of n) > 0
                delete first attachment of n
            end repeat
        end tell
    """,
        ],
        capture_output=True,
        text=True,
    )

    expected = 0
    for key in sorted(surviving_images.keys()):
        filepath = _decode_image_to_tempfile(surviving_images[key])
        if not filepath:
            continue
        expected += 1
        subprocess.run(
            [
                "osascript",
                "-e",
                f"""
            tell application "Notes"
                set n to first note whose id is "{note_id}"
                make new attachment at end of attachments of n with data POSIX file "{filepath}"
                if (count of attachments of n) > {expected} then
                    delete last attachment of n
                end if
            end tell
        """,
            ],
            capture_output=True,
            text=True,
        )
        os.unlink(filepath)


def edit_note(note_id):
    result = id_search_memo(note_id)
    original_md, original_html, image_map = md_converter(result)

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
        temp_file.write(original_md.encode("utf-8"))
        temp_file_path = temp_file.name

    if image_map:
        click.secho(
            f"\nℹ️  This note contains {len(image_map)} image(s), shown as [MEMO_IMG_N] placeholders.",
            fg="cyan",
        )
        click.secho(
            "  Keep placeholders to preserve images, remove them to delete images.",
            fg="cyan",
        )

    editor = os.getenv("EDITOR", "vim")
    subprocess.run([editor, temp_file_path])

    with open(temp_file_path, "r", encoding="utf-8") as file:
        edited_md = file.read().strip()

    if edited_md == original_md:
        click.secho("\nNo changes made.", fg="yellow")
        return

    # Determine which images the user kept (placeholder still present)
    surviving_images = {}
    if image_map:
        for key, img_html in image_map.items():
            if key in edited_md:
                surviving_images[key] = img_html
        # Remove placeholders before converting to HTML
        for key in image_map:
            edited_md = edited_md.replace(key, "")

    edited_html = mistune.markdown(edited_md)

    update_script = f"""
        tell application "Notes"
            set selectedNote to first note whose id is "{note_id}"
            set body of selectedNote to "{edited_html}"
        end tell
        """
    process = subprocess.run(
        ["osascript", "-e", update_script], capture_output=True, text=True
    )
    if process.returncode != 0:
        click.secho("\nError: Could not update note.\n", fg="red")
        click.secho(process.stderr, fg="red")
        return

    # Re-add images as attachments (set body strips inline base64 images)
    if surviving_images:
        _reattach_images(note_id, surviving_images)
        click.secho(
            f"\nNote updated. {len(surviving_images)} image(s) preserved.",
            fg="green",
        )
    else:
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
