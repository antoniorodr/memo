import os
import subprocess
import tempfile

import click
import mistune

from memo.services.notes_services.processing.notes_processing import NotesProcessing


class NotesOperations:
    """Class to handle operations related to notes."""

    @staticmethod
    def add_note(folder_name):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
            temp_file.write(b"# Your note title\n\nWrite your note here...")
            temp_file_path = temp_file.name

        editor = os.getenv("EDITOR", "vim")
        subprocess.run([editor, temp_file_path])

        with open(temp_file_path, "r", encoding="utf-8") as file:
            note_md = file.read().strip()

        if not note_md or note_md == "# Your note title\n\nWrite your note here...":
            click.echo("\nNote creation cancelled.")
            os.remove(temp_file_path)
            return

        note_html = mistune.markdown(note_md)

        escaped_folder_name = NotesProcessing.applescript_escape(folder_name)
        escaped_note_html = NotesProcessing.applescript_escape(note_html)

        script = f"""
            tell application "Notes"
                set targetFolder to first folder whose name is "{escaped_folder_name}"
                tell targetFolder
                    make new note with properties {{body:"{escaped_note_html}"}}
                end tell
            end tell
            """

        process = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        os.remove(temp_file_path)

        if process.returncode == 0:
            click.echo(f"\nNote created in '{folder_name}' folder.")
        else:
            click.echo("\nError: Could not create note. Check if the folder exists.")

    @staticmethod
    def pick_note(note_map, notes_list, action):
        click.secho(
            "\nRemember: Due to AppleScript limitations, the images will be preserved at the end of the note.",
            fg="yellow",
        )
        choice = click.prompt(
            f"\nEnter the number of the note you want to {action}", type=int
        )

        while choice < 1 or choice > len(notes_list):
            click.secho(
                "\nInvalid selection. The note you selected is not in the list.",
                fg="red",
            )
            choice = click.prompt(
                f"\nEnter the number of the note you want to {action}", type=int
            )

        if 1 <= choice <= len(notes_list):
            note_data = note_map.get(choice)
            if note_data is None:
                click.secho(
                    "\nInvalid selection.",
                    fg="yellow",
                )
                return
            return note_data[0]

    @staticmethod
    def delete_note(note_id):

        escaped_note_id = NotesProcessing.applescript_escape(note_id)

        script = f'''
        tell application "Notes"
            set theNote to first note whose id is "{escaped_note_id}"
            delete theNote
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode == 0:
            click.secho("\nNote deleted successfully.", fg="green")
        else:
            click.secho(f"Error: {result.stderr}", fg="red")

    @staticmethod
    def delete_note_folder(folder_name):

        escaped_folder_name = NotesProcessing.applescript_escape(folder_name)

        script = f'''
        tell application "Notes"
            set selectedFolder to first folder whose name is "{escaped_folder_name}"
            delete selectedFolder
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode == 0:
            click.secho("\nFolder deleted successfully.", fg="green")
        else:
            click.secho(f"Error: {result.stderr}", fg="red")

    @staticmethod
    def move_note(note_id: str, target_folder: str):

        escaped_note_id = NotesProcessing.applescript_escape(note_id)
        escaped_target_folder = NotesProcessing.applescript_escape(target_folder)
        script = f'''
        tell application "Notes"
            set noteToMove to missing value
            set noteName to ""
            set noteBody to ""
            set accToUse to missing value
            repeat with acc in accounts
                repeat with f in folders of acc
                    try
                        set n to first note of f whose id is "{escaped_note_id}"
                        set noteToMove to n
                        set noteName to name of n
                        set noteBody to body of n
                        set accToUse to acc
                        exit repeat
                    end try
                end repeat
                if noteToMove is not missing value then exit repeat
            end repeat
            if noteToMove is not missing value then
                set destinationFolder to missing value
                try
                    set destinationFolder to folder "{escaped_target_folder}" of accToUse
                on error
                    set destinationFolder to make new folder with properties
                    {{name:"{escaped_target_folder}"}} at accToUse
                end try
                make new note at destinationFolder with properties {{name:noteName, body:noteBody}}
                delete noteToMove
            end if
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        if result.returncode == 0:
            click.secho(
                f'\n✅ The note was moved to "{target_folder}" folder.', fg="green"
            )
        else:
            click.secho(f"\n❌ Error while moving: {result.stderr}", fg="red")
