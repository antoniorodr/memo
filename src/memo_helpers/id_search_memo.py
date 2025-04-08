import subprocess


def id_search_memo(note_id):
    script = f"""
        tell application "Notes"
            set selectedNote to first note whose id is "{note_id}"
            return body of selectedNote
        end tell
        """
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result
