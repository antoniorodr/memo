import subprocess
import os
import click
import html2text
import chardet


def export_memo(path: str):
    script = f"""
    set exportFolder to "{path}"
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
        click.secho(f"\nNotes exported to {path}", fg="green")
        if click.confirm(
            "\nDo you want to convert the notes to Markdown? Attachements and pictures will not be converted."
        ):
            html_to_md(path)
    else:
        click.secho("\nError exporting notes", fg="red")


def html_to_md(path: str):
    files = os.listdir(path)
    files_list = [f for f in files if os.path.isfile(os.path.join(path, f))]

    for file in files_list:
        file_path = os.path.join(path, file)
        file_name = os.path.splitext(file)[0]

        with open(file_path, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result["encoding"]

        try:
            if encoding:
                html_content = raw_data.decode(encoding)
            else:
                html_content = raw_data.decode("utf-8", errors="replace")
        except Exception as e:
            click.secho(
                f"Could not decode {file} with detected encoding '{encoding}': {e}",
                fg="red",
            )
            return

        text_maker = html2text.HTML2Text()
        text_maker.images_to_alt = True
        text_maker.body_width = 0
        original_md = text_maker.handle(html_content).strip()
        output_path = os.path.join(path, f"{file_name}.md")

        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write(original_md)

    click.secho("\nAll notes succesfully converted to Markdown", fg="green")
