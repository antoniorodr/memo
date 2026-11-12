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
