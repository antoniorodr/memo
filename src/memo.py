import click
from get_memo import get_note
from edit_memo import edit_note
from add_memo import add_note
from delete_memo import delete_note
from move_memo import move_note
from choice_memo import pick_note
from list_folder import notes_folders
from validation_memo import selection_notes_validation

# TODO: Implement fzf with --search flag
# TODO: Check if reminders works better retrieving only the first event.


@click.group(invoke_without_command=False)
def cli():
    pass


@cli.command()
@click.option(
    "--folder",
    "-f",
    default="",
    help="Notes folder (leave empty to get all).",
)
@click.option(
    "--add",
    "-a",
    is_flag=True,
    help="Add a note to the specified folder.",
)
@click.option(
    "--edit",
    "-e",
    is_flag=True,
    help="Edit a note in the specified folder. Specify a folder using the --folder flag.",
)
@click.option(
    "--delete",
    "-d",
    is_flag=True,
    help="Delete a note in the specified folder. Specify a folder using the --folder flag.",
)
@click.option(
    "--move",
    "-m",
    is_flag=True,
    help="Move a note to a different folder.",
)
@click.option(
    "--flist",
    "-fl",
    is_flag=True,
    help="List all the folders and subfolders.",
)
def notes(folder, edit, add, delete, move, flist):
    selection_notes_validation(folder, edit, delete, move, add, flist)
    notes_info = get_note()
    note_map = notes_info[0]
    notes_list = notes_info[1]
    notes_list_filter = [
        note for note in enumerate(notes_list, start=1) if folder in note[1]
    ]

    if not flist:
        if not notes_list_filter:
            click.echo("\nNo notes found.")
        else:
            title = f"Notes in folder {folder}:" if folder else "All notes:"
            click.echo(f"\n{title}\n")
            for note in notes_list_filter:
                click.echo(f"{note[0]}. {note[1]}")

    if edit:
        note_id = pick_note(note_map, notes_list_filter, "edit")
        edit_note(note_id)
    if add:
        add_note(folder)
    if move:
        note_id = pick_note(note_map, notes_list_filter, "move")
        if note_id is None:
            click.echo("Invalid selection.")
            return
        target_folder = click.prompt(
            "\nEnter the folder you want to move the note to", type=str
        )
        move_note(note_id, target_folder)
    if delete:
        choice = click.prompt(
            "\nEnter the number of the note you want to delete", type=int
        )
        if 1 <= choice <= len(notes_list):
            note_data = note_map.get(choice)
            if note_data is None:
                click.echo("Invalid selection.")
                return
            note_id = note_data[0]
            delete_note(note_id)
    if flist:
        notes_folders()
