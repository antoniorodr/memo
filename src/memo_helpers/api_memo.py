"""Machine-friendly API for notes (non-interactive)."""

import json
import os
import re
import sys
import tempfile
import subprocess
import mistune

from memo_helpers.get_memo import get_note
from memo_helpers.id_search_memo import id_search_memo
from memo_helpers.md_converter import md_converter


def _read_stdin_content():
    """Read content from stdin. Returns None if stdin is a TTY (no input)."""
    if sys.stdin.isatty():
        return None
    return sys.stdin.read()


def _update_note_body(note_id, html_content):
    """Update note body via temp file to avoid AppleScript escaping issues."""
    fd, path = tempfile.mkstemp(suffix=".html")
    try:
        os.write(fd, html_content.encode("utf-8"))
        os.close(fd)
        escaped_path = path.replace("\\", "\\\\").replace('"', '\\"')
        script = f'''
        set htmlPath to "{escaped_path}"
        set htmlContent to do shell script "cat " & quoted form of htmlPath
        tell application "Notes"
            set n to first note whose id is "{note_id}"
            set body of n to htmlContent
        end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0, result.stderr
    finally:
        if os.path.exists(path):
            os.unlink(path)


def list_notes(folder="", format="tsv"):
    """Fetch notes without cache and return formatted output."""
    note_map, notes_list = get_note(use_cache=False)
    notes_list_filter = [
        note for note in enumerate(notes_list, start=1) if folder in note[1]
    ]
    lines = []
    seen_id = set()
    for idx, note_title in notes_list_filter:
        note_data = note_map.get(idx)
        if note_data is None:
            continue
        note_id, full_title = note_data
        if note_id in seen_id:
            continue
        seen_id.add(note_id)
        if " - " in full_title:
            folder_name, title = full_title.split(" - ", 1)
        else:
            folder_name, title = "", full_title
        if format == "tsv":
            lines.append(f"{note_id}\t{folder_name}\t{title}")
        elif format == "lines":
            lines.append(f"{note_id}|{folder_name}|{title}")
        elif format == "json":
            lines.append(
                json.dumps({"id": note_id, "folder": folder_name, "title": title})
            )
    return "\n".join(lines)


def show_note(note_id):
    """Fetch note body and return as Markdown."""
    result = id_search_memo(note_id)
    if result.returncode != 0:
        return None, result.stderr
    markdown_content = md_converter(result)[0]
    return markdown_content, None


def edit_note_stdin(note_id, content):
    """Replace note body with content (Markdown). Strips image placeholders."""
    for placeholder in re.findall(r"\[MEMO_IMG_\d+\]", content):
        content = content.replace(placeholder, "")
    html_content = mistune.markdown(content)
    return _update_note_body(note_id, html_content)


def add_note_stdin(folder_name, content):
    """Create note from Markdown content."""
    html_content = mistune.markdown(content)
    fd, path = tempfile.mkstemp(suffix=".html")
    try:
        os.write(fd, html_content.encode("utf-8"))
        os.close(fd)
        escaped_path = path.replace("\\", "\\\\").replace('"', '\\"')
        script = f'''
        set htmlPath to "{escaped_path}"
        set htmlContent to do shell script "cat " & quoted form of htmlPath
        tell application "Notes"
            set targetFolder to first folder whose name is "{folder_name}"
            tell targetFolder
                make new note with properties {{body:htmlContent}}
            end tell
        end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0, result.stderr
    finally:
        if os.path.exists(path):
            os.unlink(path)
