import subprocess
import click
import html2text


def move_note(note_id: str, target_folder: str):
    script_body = f"""
        tell application "Notes"
            set selectedNote to first note whose id is "{note_id}"
            return body of selectedNote
        end tell
        """
    result_body = subprocess.run(
        ["osascript", "-e", script_body], capture_output=True, text=True
    )
    original_html = result_body.stdout.strip()

    text_maker = html2text.HTML2Text()
    text_maker.body_width = 0

    if "<img" in original_html or "<enclosure" in original_html:
        click.secho(
            "\n⚠️  Warning: This note contains images or attachments that could be lost!",
            fg="yellow",
        )
        if not click.confirm("\nDo you still want to continue moving the note?"):
            return

    script = f'''
    tell application "Notes"
        set noteToMove to missing value
        set noteName to ""
        set noteBody to ""
        set accToUse to missing value
        repeat with acc in accounts
            repeat with f in folders of acc
                try
                    set n to first note of f whose id is "{note_id}"
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
                set destinationFolder to folder "{target_folder}" of accToUse
            on error
                set destinationFolder to make new folder with properties {{name:"{target_folder}"}} at accToUse
            end try
            make new note at destinationFolder with properties {{name:noteName, body:noteBody}}
            delete noteToMove
        end if
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode == 0:
        click.secho(f'\n✅ The note was moved to "{target_folder}" folder.', fg="green")
    else:
        click.secho(f"\n❌ Error while moving: {result.stderr}", fg="red")
