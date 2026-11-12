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

    @staticmethod
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
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
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
                    due_datetime = datetime.fromtimestamp(float(due_ts_clean))
                except ValueError:
                    due_datetime = None
            else:
                due_datetime = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            reminders_map[i + 1] = (reminder_id, title, due_datetime)

        reminders_list = [f"{v[1]} | {v[2]}" for v in reminders_map.values()]
        return [reminders_map, reminders_list]

    @staticmethod
    def edit_reminder(reminder_id, part_to_edit):

        escaped_reminder_id = NotesProcessing.applescript_escape(reminder_id)

        if part_to_edit == "title":
            new_title = click.prompt("\nEnter the new title")

            escaped_new_title = NotesProcessing.applescript_escape(new_title)

            script = f"""
                tell application "Reminders"
                    set selectedReminder to first reminder whose id is "{escaped_reminder_id}"
                    set name of selectedReminder to "{escaped_new_title}"
                end tell
                """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True
            )
            if result.returncode == 0:
                click.secho("\nReminder title updated.", fg="green")
            else:
                click.secho("\nError: Could not update reminder title.", fg="red")
        if part_to_edit == "due date":
            new_date = click.prompt("\nEnter the new date (YYYY-MM-DD)")
            new_time = click.prompt("\nEnter the new time (HH:MM)")
            datetime_str = f"{new_date} {new_time}"
            due_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            year = due_dt.year
            month = due_dt.month
            day = due_dt.day
            hour = due_dt.hour
            minute = due_dt.minute

            script = f"""
            tell application "Reminders"
                set selectedReminder to first reminder whose id is "{escaped_reminder_id}"
                set dueDate to current date
                set year of dueDate to {year}
                set month of dueDate to {month}
                set day of dueDate to {day}
                set time of dueDate to ({hour} * hours + {minute} * minutes)
                set due date of selectedReminder to dueDate
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True
            )
            if result.returncode == 0:
                click.secho("\nReminder date updated.", fg="green")
            else:
                click.secho("\nError: Could not update reminder date.", fg="red")
