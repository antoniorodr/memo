import click
from get_memos import get_note
from edit_memos import edit_note
from add_memos import add_note
from delete_memos import delete_note

# TODO: Implement fzf with --search flag
# TODO: Check if reminders works better retrieving only the first event.
# TODO: Find out how to move a note to a different folder.


@click.group(invoke_without_command=False)
def cli():
    pass


@cli.command()
@click.option(
    "--folder",
    default="",
    help="Notes folder (leave empty to get all).",
)
@click.option(
    "--add",
    is_flag=True,
    help="Add a note to the specified folder.",
)
@click.option(
    "--edit",
    is_flag=True,
    help="Edit a note in the specified folder. Specify a folder using the --folder flag.",
)
@click.option(
    "--delete",
    is_flag=True,
    help="Delete a note in the specified folder. Specify a folder using the --folder flag.",
)
def notes(folder, edit, add, delete):
    note_map = get_note()
    seen_id = set()
    notes_list = [
        note_title
        for _, (id, note_title) in note_map.items()
        if id not in seen_id and not seen_id.add(id)
    ]
    notes_list_filter = [
        note for note in enumerate(notes_list, start=1) if folder in note[1]
    ]
    title = f"Notes in folder {folder}:" if folder else "All notes:"

    if not notes_list_filter:
        click.echo("\nNo notes found.")
    else:
        click.echo(f"\n{title}\n")
        for note in notes_list_filter:
            click.echo(f"{note[0]}. {note[1]}")

    if edit:
        choice = click.prompt(
            "\nEnter the number of the note you want to edit", type=int
        )
        if 1 <= choice <= len(notes_list):
            note_data = note_map.get(choice)
            if note_data is None:
                click.echo("Invalid selection.")
                return
            note_id = note_data[0]
            edit_note(note_id)
        else:
            click.echo("Invalid selection.")
    if add:
        add_note(folder)
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
