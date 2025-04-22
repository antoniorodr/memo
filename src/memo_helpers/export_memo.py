import subprocess
import click
import os
from markitdown import MarkItDown

EXPORT_PATH = os.path.expanduser("~/Downloads/Notes/")


def export_memo():
    script = f"""
    set exportFolder to "{EXPORT_PATH}"
    do shell script "mkdir -p " & quoted form of exportFolder

    on replaceText(find, replace, subject)
        set prevTIDs to text item delimiters of AppleScript
        set text item delimiters to find
        set subject to text items of subject
        set text item delimiters to replace
        set subject to "" & subject
        set text item delimiters to prevTIDs
        return subject
    end replaceText

    on cleanFileName(t)
        set t to my replaceText(":", "-", t)
        set t to my replaceText("/", "-", t)
        if length of t > 250 then
            set t to text 1 thru 250 of t
        end if
        return t
    end cleanFileName

    tell application "Notes"
        repeat with theNote in notes of default account
            set noteLocked to password protected of theNote as boolean
            if not noteLocked then
                set noteName to name of theNote as string
                set noteBody to body of theNote as string
                set cleanName to my cleanFileName(noteName)
                set exportPath to exportFolder & cleanName
                set tempHTMLPath to exportPath & ".html"
                set htmlContent to "<html><head><meta charset=\\"UTF-8\\"></head><body>" & noteBody & "</body></html>"
                set f to open for access (POSIX file tempHTMLPath) with write permission
                set eof of f to 0
                write htmlContent to f
                close access f
            end if
        end repeat
    end tell
    """

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode == 0:
        click.secho(
            f"\nNotes exported successfully in '{EXPORT_PATH}' folder", fg="green"
        )
        if click.confirm(
            "\nDo you want to convert the notes to Markdown?. The pictures can be lost."
        ):
            pdf_converter()
    else:
        click.secho(f"\nError exporting notes:\n{result.stderr}", fg="red")


def pdf_converter():
    files = os.listdir(EXPORT_PATH)
    files_list = [f for f in files if os.path.isfile(os.path.join(EXPORT_PATH, f))]

    for file in files_list:
        md = MarkItDown(enable_plugins=False)
        result = md.convert(os.path.join(EXPORT_PATH, file))

        output_file = os.path.splitext(file)[0] + ".md"
        output_path = os.path.join(EXPORT_PATH, output_file)

        with open(output_path, "w") as f:
            f.write(result.text_content)

        click.secho(f"\nFile saved in '{output_path}'", fg="green")
