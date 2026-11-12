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

    @staticmethod
    def pick_reminder(reminder_map, reminders_list, action):
        choice = click.prompt(
            f"\nEnter the number of the reminder you want to {action}", type=int
        )
        if 1 <= choice <= len(reminders_list):
            reminder_data = reminder_map.get(choice)
            if reminder_data is None:
                click.echo("Invalid selection.")
                return
            return reminder_data[0]
        else:
            raise IndexError("The reminder you selected is not in the list.")

    @staticmethod
    def complete_reminder(reminder_id):

        escaped_reminder_id = NotesProcessing.applescript_escape(reminder_id)
        script = f'''
            tell application "Reminders"
                set selectedRem to first reminder whose id is "{escaped_reminder_id}"
                set completed of selectedRem to true
            end tell
            '''

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode == 0:
            click.secho("\nReminder marked successfully as completed.", fg="green")
        else:
            click.secho(f"Error: {result.stderr}", fg="red")

    @staticmethod
    def delete_reminder(reminder_id):

        escaped_reminder_id = NotesProcessing.applescript_escape(reminder_id)

        script = f'''
            tell application "Reminders"
            set selectedRem to first reminder whose id is "{escaped_reminder_id}"
            delete selectedRem
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode == 0:
            click.secho("\nReminder deleted successfully.", fg="green")
        else:
            click.secho(f"Error: {result.stderr}", fg="red")
