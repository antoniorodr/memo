import click
import subprocess


def delete_note(note_id):
    script = f'''
    tell application "Notes"
        set theNote to first note whose id is "{note_id}"
        delete theNote
    end tell
    '''

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode == 0:
        click.secho("\nNote deleted successfully.", fg="green")
    else:
        click.secho(f"Error: {result.stderr}", fg="red")


def complete_reminder(reminder_id):
    script = f'''
        tell application "Reminders"
            set selectedRem to first reminder whose id is "{reminder_id}"
            set completed of selectedRem to true
        end tell
        '''

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode == 0:
        click.secho("\nReminder marked successfully as completed.", fg="green")
    else:
        click.secho(f"Error: {result.stderr}", fg="red")


def delete_reminder(reminder_id):
    script = f'''
        tell application "Reminders"
        set selectedRem to first reminder whose id is "{reminder_id}"
        delete selectedRem
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode == 0:
        click.secho("\nReminder deleted successfully.", fg="green")
    else:
        click.secho(f"Error: {result.stderr}", fg="red")
