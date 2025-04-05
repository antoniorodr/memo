import subprocess
import click


def get_note():
    script = """
    tell application "Notes"
        set output to ""
        repeat with eachFolder in folders
            set folderName to name of eachFolder
            if folderName is not "Nylig slettet" and folderName is not "Recently Deleted" then
                repeat with eachNote in notes of eachFolder
                    set noteName to name of eachNote
                    set noteID to id of eachNote
                    set output to output & noteID & "|" & folderName & " - " & noteName & "\n"
                end repeat
            end if
        end repeat
        return output
    end tell
    """
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    notes_list = [line.split("|") for line in result.stdout.strip().split("\n") if line]
    note_map = {
        i + 1: (note_id, note_title)
        for i, (note_id, note_title) in enumerate(notes_list)
    }

    if not notes_list:
        click.echo("No notes found.")
    seen_id = set()
    notes_list = [
        note_title
        for _, (id, note_title) in note_map.items()
        if id not in seen_id and not seen_id.add(id)
    ]
    return [note_map, notes_list]
