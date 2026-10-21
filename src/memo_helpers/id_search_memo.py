import subprocess

from memo_helpers.validation_memo import applescript_escape


def id_search_memo(note_id):

    escaped_note_id = applescript_escape(note_id)
    script = f"""
        tell application "Notes"
            set selectedNote to first note whose id is "{escaped_note_id}"
            return body of selectedNote
        end tell
        """

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result
