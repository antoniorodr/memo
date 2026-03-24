import subprocess
import os
import click
from memo_helpers.id_search_memo import id_search_memo
from memo_helpers.md_converter import md_converter


def get_recording_transcript(note_id):
    """Retrieve the transcript of a call recording as markdown.

    Apple auto-generates transcripts for call recordings and stores them
    as the note body.  We reuse id_search_memo + md_converter to convert
    the HTML body to clean markdown.

    Returns (markdown_text, original_html, image_map) or None on error.
    """
    result = id_search_memo(note_id)
    if result.returncode != 0:
        return None
    return md_converter(result)


def get_recording_attachments(note_id):
    """List attachments in a call recording note.

    Returns a list of dicts with 'index', 'name', and 'content_id' keys,
    or an empty list on error.
    """
    script = f"""
    tell application "Notes"
        set n to first note whose id is "{note_id}"
        set attCount to count of attachments of n
        set attList to ""
        repeat with i from 1 to attCount
            set att to attachment i of n
            set attName to name of att
            set attCID to content identifier of att
            set attList to attList & i & "|" & attName & "|" & attCID & linefeed
        end repeat
        return attList
    end tell
    """

    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )

    if result.returncode != 0:
        return []

    attachments = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 2)
        if len(parts) >= 2:
            attachments.append(
                {
                    "index": int(parts[0]),
                    "name": parts[1],
                    "content_id": parts[2] if len(parts) > 2 else "",
                }
            )

    return attachments


def extract_recording_audio(note_id, output_path, attachment_index=1):
    """Extract the audio attachment from a call recording note to disk.

    By default extracts the first attachment (index=1) which is typically
    the audio file.  Uses AppleScript's ``save`` command to write the
    attachment directly to the output path.

    Returns the final output file path on success, or None on error.
    """
    # First get the attachment name to build the destination path.
    name_script = f"""
    tell application "Notes"
        set n to first note whose id is "{note_id}"
        set att to attachment {attachment_index} of n
        return name of att
    end tell
    """

    name_result = subprocess.run(
        ["osascript", "-e", name_script], capture_output=True, text=True
    )

    if name_result.returncode != 0:
        click.secho("\nError: Could not access recording attachment.", fg="red")
        click.secho(name_result.stderr.strip(), fg="red")
        return None

    att_name = name_result.stdout.strip()

    # Determine final output path.
    if os.path.isdir(output_path):
        dest_path = os.path.join(output_path, att_name)
    else:
        dest_path = output_path

    dest_dir = os.path.dirname(os.path.abspath(dest_path))
    os.makedirs(dest_dir, exist_ok=True)

    # Use AppleScript's save command to write the attachment to disk.
    # This bypasses the sandbox restrictions that prevent direct file
    # access to Notes' internal Media directory.
    save_script = f"""
    tell application "Notes"
        set n to first note whose id is "{note_id}"
        set att to attachment {attachment_index} of n
        save att in POSIX file "{dest_path}"
    end tell
    """

    save_result = subprocess.run(
        ["osascript", "-e", save_script], capture_output=True, text=True
    )

    if save_result.returncode != 0:
        click.secho("\nError: Could not extract recording.", fg="red")
        click.secho(save_result.stderr.strip(), fg="red")
        return None

    if not os.path.exists(dest_path):
        click.secho(
            f"\nError: File was not written to {dest_path}", fg="red"
        )
        return None

    return dest_path


def get_recording_metadata(note_id):
    """Fetch metadata for a call recording note.

    Returns a dict with name, creation_date, modification_date, and
    attachment_count, or None on error.
    """
    script = f"""
    tell application "Notes"
        set n to first note whose id is "{note_id}"
        set noteName to name of n
        set noteCreated to creation date of n as string
        set noteModified to modification date of n as string
        set attCount to count of attachments of n
        return noteName & "|" & noteCreated & "|" & noteModified & "|" & attCount
    end tell
    """

    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )

    if result.returncode != 0:
        return None

    parts = result.stdout.strip().split("|")
    if len(parts) < 4:
        return None

    return {
        "name": parts[0],
        "creation_date": parts[1],
        "modification_date": parts[2],
        "attachment_count": int(parts[3]),
    }
