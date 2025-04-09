import subprocess
import click
import datetime


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


def get_reminder():
    click.secho("\nFetching reminders...", fg="yellow")
    script = """
    set output to ""
    tell application "Reminders"
        repeat with eachRem in reminders
            if not completed of eachRem then
                set nameRem to name of eachRem
                set idRem to id of eachRem
                set dueDateRem to due date of eachRem
                if dueDateRem is not missing value then
                    set timeStamp to (dueDateRem - (current date)) + (do shell script "date +%s") as real
                else
                    set timeStamp to "None"
                end if
                set output to output & idRem & "|" & nameRem & " -> " & timeStamp & "\\n"
            end if
        end repeat
    end tell
    return output
    """
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    reminders_list = [
        line.split("|") for line in result.stdout.strip().split("\n") if line
    ]
    reminders_map = {}
    for i, (reminder_id, reminder_title) in enumerate(reminders_list):
        parts = reminder_title.split("->")
        title = parts[0].strip()
        due_ts_raw = parts[1].strip()

        if due_ts_raw != "None":
            due_ts_clean = due_ts_raw.replace(",", ".")
            try:
                due_datetime = datetime.datetime.fromtimestamp(float(due_ts_clean))
            except ValueError:
                due_datetime = None
        else:
            due_datetime = None

        reminders_map[i + 1] = (reminder_id, title, due_datetime)

    reminders_list = [f"{v[1]} | {v[2]}" for v in reminders_map.values()]
    return [reminders_map, reminders_list]
