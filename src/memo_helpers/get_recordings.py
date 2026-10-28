import subprocess
import click


def _parse_recordings_output(stdout):
    """Parse AppleScript output into (recording_map, recordings_list)."""
    lines = [line for line in stdout.strip().split("\n") if line]

    if not lines:
        return {}, []

    notes_list = [line.split("|", 1) for line in lines]
    recording_map = {
        i + 1: (parts[0], parts[1]) for i, parts in enumerate(notes_list)
    }

    seen_id = set()
    recordings_list = [
        note_title
        for _, (note_id, note_title) in recording_map.items()
        if note_id not in seen_id and not seen_id.add(note_id)
    ]

    return recording_map, recordings_list


def get_recordings():
    """Fetch call recordings from Apple Notes.

    Uses a dual strategy:
    1. Try the "Call Recordings" smart folder directly (system-level folder)
    2. Fall back to scanning all notes for "Call with ..." name pattern

    Returns a tuple of (recording_map, recordings_list) matching the
    format used by get_note():
      - recording_map: {index: (note_id, display_title)}
      - recordings_list: [display_title, ...]
    """

    # Strategy 1: Try the "Call Recordings" smart folder directly.
    # This is a system-level folder that doesn't appear in the normal
    # `folders` enumeration but can be accessed by name.
    smart_folder_script = """
    tell application "Notes"
        try
            set recFolder to folder "Call Recordings"
            set notesList to {}
            set folderNotes to notes of recFolder
            if (count of folderNotes) > 0 then
                set noteIDs to id of every note of recFolder
                set noteNames to name of every note of recFolder
                set noteDates to creation date of every note of recFolder
                repeat with i from 1 to count of noteIDs
                    set dateStr to (item i of noteDates) as string
                    set end of notesList to (item i of noteIDs) & "|" & (item i of noteNames) & " (" & dateStr & ")"
                end repeat
            end if
            set AppleScript's text item delimiters to "\\n"
            set output to notesList as string
            set AppleScript's text item delimiters to ""
            return output
        on error
            return ""
        end try
    end tell
    """

    result = subprocess.run(
        ["osascript", "-e", smart_folder_script], capture_output=True, text=True
    )

    if result.returncode == 0 and result.stdout.strip():
        return _parse_recordings_output(result.stdout)

    # Strategy 2: Fall back to scanning all notes for "Call with" pattern.
    # This catches recordings even if the smart folder isn't available.
    fallback_script = """
    tell application "Notes"
        set notesList to {}
        repeat with f in folders
            repeat with n in notes of f
                set noteName to name of n
                if noteName starts with "Call with" then
                    set noteID to id of n
                    set noteDate to creation date of n as string
                    set end of notesList to noteID & "|" & noteName & " (" & noteDate & ")"
                end if
            end repeat
        end repeat
        set AppleScript's text item delimiters to "\\n"
        set output to notesList as string
        set AppleScript's text item delimiters to ""
        return output
    end tell
    """

    result = subprocess.run(
        ["osascript", "-e", fallback_script], capture_output=True, text=True
    )

    if result.returncode != 0:
        click.secho(
            "\nError: Could not access call recordings.", fg="red"
        )
        return {}, []

    return _parse_recordings_output(result.stdout)
