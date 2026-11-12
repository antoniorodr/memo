import subprocess
from datetime import datetime

import click

from memo.services.notes_services.processing.notes_processing import NotesProcessing


class RemindersOperations:
    """Class to handle operations related to reminders."""

    @staticmethod
    def add_reminder():
        title = click.prompt("\nEnter the title of the reminder")
        date = click.prompt("Enter the due date (YYYY-MM-DD)")
        time = click.prompt("Enter the due time (HH:MM)")
        datetime_str = f"{date} {time}"
        due_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

        year = due_dt.year
        month = due_dt.month
        day = due_dt.day
        hour = due_dt.hour
        minute = due_dt.minute

        escaped_title = NotesProcessing.applescript_escape(title)

        script = f'''
        tell application "Reminders"
            set theDate to current date
            set year of theDate to {year}
            set month of theDate to {month}
            set day of theDate to {day}
            set time of theDate to ({hour} * hours + {minute} * minutes)
            make new reminder with properties {{name:"{escaped_title}", due date:theDate}}
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode == 0:
            click.secho(f"\nReminder '{title}' added successfully.", fg="green")
        else:
            click.secho(f"\nError: Could not add reminder, {result.stderr}", fg="red")
