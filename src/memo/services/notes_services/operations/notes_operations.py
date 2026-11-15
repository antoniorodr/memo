import os
import subprocess
import tempfile

import click
import mistune

from memo.services.notes_services.cache.notes_cache_services import NotesCacheServices
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

    @staticmethod
    def fuzzy_notes():
        note_map, unique_notes = NotesOperations.get_note()
        title_to_id = {title: note_id for (_, (note_id, title)) in note_map.items()}

        with tempfile.TemporaryDirectory() as tmpdirname:
            for note_title in unique_notes:
                note_id = title_to_id[note_title]
                result = NotesOperations.id_search_memo(note_id)
                original_md = NotesProcessing.md_converter(result)[0]

                safe_filename = note_title.replace("/", "-").replace("\\", "-")
                file_path = os.path.join(tmpdirname, f"{safe_filename}.md")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(original_md)

            fzf_command = r"""
            fzf --style=full \
                --border --padding=1,2 \
                --border-label=' Your Notes ' --input-label=' Input ' --header-label=' File Type ' \
                --preview='bat --style=plain --color=always {}' \
                --preview-window=right:60%:wrap:cycle \
                --bind='ctrl-d:preview-down,ctrl-u:preview-up' \
                --bind='result:transform-list-label:
                    if [[ -z $FZF_QUERY ]]; then
                    echo " $FZF_MATCH_COUNT items "
                    else
                    echo " $FZF_MATCH_COUNT matches for [$FZF_QUERY] "
                    fi' \
                --bind='focus:transform-preview-label:[[ -n {} ]] && printf " Previewing [%s] " {}' \
                --bind='focus:+transform-header:file --brief {} || echo "No file selected"' \
                --bind='ctrl-r:change-list-label( Reloading the list )+reload(sleep 2; git ls-files)' \
                --color='border:#aaaaaa,label:#cccccc' \
                --color='preview-border:#9999cc,preview-label:#ccccff' \
                --color='list-border:#669966,list-label:#99cc99' \
                --color='input-border:#996666,input-label:#ffcccc' \
                --color='header-border:#6699cc,header-label:#99ccff'
            """
            subprocess.run(fzf_command, shell=True, cwd=tmpdirname)

    @staticmethod
    def get_note():
        cached = NotesCacheServices.load_cache()
        if cached:
            return list(cached)

        script = """
        set deletedTranslations to {"Recently Deleted", "Nylig slettet", "Senast raderade", "Senest slettet", "Zuletzt gelöscht", "Supprimés récemment", "Eliminados recientemente", "Eliminati di recente", "Recent verwijderd", "Ostatnio usunięte", "Недавно удалённые", "Apagados recentemente", "Apagadas recentemente", "最近删除", "最近刪除", "最近削除した項目", "최근 삭제된 항목", "Son Silinenler", "Äskettäin poistetut", "Nedávno smazané", "Πρόσφατα διαγραμμένα", "Nemrég töröltek", "Șterse recent", "Nedávno vymazané", "เพิ่งลบ", "Đã xóa gần đây", "Нещодавно видалені"}

        tell application "Notes"
            set notesList to {}
            repeat with eachFolder in folders
                set folderName to name of eachFolder
                if folderName is not in deletedTranslations then
                    set folderNotes to notes of eachFolder
                    if (count of folderNotes) > 0 then
                        set noteIDs to id of every note of eachFolder
                        set noteNames to name of every note of eachFolder
                        repeat with i from 1 to count of noteIDs
                            set end of notesList to (item i of noteIDs) & "|" & folderName & " - " & (item i of noteNames)
                        end repeat
                    end if
                end if
            end repeat
            set AppleScript's text item delimiters to "\n"
            set output to notesList as string
            set AppleScript's text item delimiters to ""
            return output
        end tell
        """

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        notes_list = [
            line.split("|", 1) for line in result.stdout.strip().split("\n") if line
        ]

        note_map = {i + 1: (parts[0], parts[1]) for i, parts in enumerate(notes_list)}

        if not notes_list:
            click.echo("No notes found.")
        seen_id = set()
        notes_list = [
            note_title
            for _, (id, note_title) in note_map.items()
            if id not in seen_id and not seen_id.add(id)
        ]

        NotesCacheServices.save_cache(note_map, notes_list)
        return [note_map, notes_list]

    @staticmethod
    def id_search_memo(note_id):

        escaped_note_id = NotesProcessing.applescript_escape(note_id)
        script = f"""
            tell application "Notes"
                set selectedNote to first note whose id is "{escaped_note_id}"
                return body of selectedNote
            end tell
            """

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        return result

    @staticmethod
    def export_memo(path: str, notes_folder: str | None = None):

        if notes_folder:
            escaped_notes_folder = NotesProcessing.applescript_escape(notes_folder)

            folder_filter = f"""
            set targetFolder to missing value
            repeat with f in folders of default account
                if name of f is "{escaped_notes_folder}" then
                    set targetFolder to f
                    exit repeat
                end if
            end repeat
            if targetFolder is missing value then
                error "Folder '{escaped_notes_folder}' not found"
            end if
            set notesToExport to notes of targetFolder
            """
        else:
            folder_filter = "set notesToExport to notes of default account\n"

        escaped_path = NotesProcessing.applescript_escape(path)

        script = f"""
        set exportFolder to "{escaped_path}"
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
            {folder_filter}
            repeat with theNote in notesToExport
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

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        if result.returncode == 0:
            click.secho(f"\nNotes exported to {path}", fg="green")
            if click.confirm(
                "\nDo you want to convert the notes to Markdown? Attachements and pictures will not be converted."
            ):
                NotesProcessing.html_to_md(path)
        else:
            click.secho("\nError exporting notes", fg="red")

    @staticmethod
    def edit_note(note_id):
        result = NotesOperations.id_search_memo(note_id)
        original_md, original_html, image_map = NotesProcessing.md_converter(result)

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
            temp_file.write(original_md.encode("utf-8"))
            temp_file_path = temp_file.name

        if image_map:
            click.secho(
                f"\nℹ️ This note contains {len(image_map)} image(s), shown as [MEMO_IMG_N] placeholders.",
                fg="cyan",
            )
            click.secho(
                "Keep placeholders to preserve images, remove them to delete images.",
                fg="cyan",
            )

        editor = os.getenv("EDITOR", "vim")
        subprocess.run([editor, temp_file_path])

        with open(temp_file_path, "r", encoding="utf-8") as file:
            edited_md = file.read().strip()

        if edited_md == original_md:
            click.secho("\nNo changes made.", fg="yellow")
            return

        # Determine which images the user kept (placeholder still present)
        surviving_images = {}
        if image_map:
            for key, img_html in image_map.items():
                if key in edited_md:
                    surviving_images[key] = img_html
            # Remove placeholders before converting to HTML
            for key in image_map:
                edited_md = edited_md.replace(key, "")

        edited_html = mistune.markdown(edited_md)

        escaped_note_id = NotesProcessing.applescript_escape(note_id)
        escaped_edited_html = NotesProcessing.applescript_escape(edited_html)

        update_script = f"""
            tell application "Notes"
                set selectedNote to first note whose id is "{escaped_note_id}"
                set body of selectedNote to "{escaped_edited_html}"
            end tell
            """

        process = subprocess.run(
            ["osascript", "-e", update_script], capture_output=True, text=True
        )
        if process.returncode != 0:
            click.secho("\nError: Could not update note.\n", fg="red")
            click.secho(process.stderr, fg="red")
            return

        # Re-add images as attachments (set body strips inline base64 images)
        if surviving_images:
            NotesProcessing._reattach_images(note_id, surviving_images)
            click.secho(
                f"\nNote updated. {len(surviving_images)} image(s) preserved.",
                fg="green",
            )
        else:
            click.secho("\nNote updated.", fg="green")
