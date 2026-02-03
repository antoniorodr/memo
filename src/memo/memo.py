import click
import datetime
from memo_helpers.get_memo import get_note, get_reminder
from memo_helpers.edit_memo import edit_note, edit_reminder
from memo_helpers.add_memo import add_note, add_reminder
from memo_helpers.delete_memo import (
    delete_note,
    complete_reminder,
    delete_reminder,
    delete_note_folder,
)
from memo_helpers.move_memo import move_note
from memo_helpers.choice_memo import pick_note, pick_reminder
from memo_helpers.list_folder import notes_folders
from memo_helpers.validation_memo import selection_notes_validation
from memo_helpers.search_memo import fuzzy_notes
from memo_helpers.export_memo import export_memo

# TODO: Check if notes can be imported and exported.
# TODO: Check if its possible to fetch .localized names from the folders.
# TODO: Check alternative to md_converter to support images and attachments.


@click.group(invoke_without_command=False)
@click.version_option()
def cli():
    pass


@cli.command()
@click.option(
    "--folder",
    "-f",
    default="",
    help="Specify a folder to filter the notes (leave empty to get all).",
)
@click.option(
    "--add",
    "-a",
    is_flag=True,
    help="Add a note to the specified folder. Specify a folder using the --folder flag.",
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
@click.option("--search", "-s", is_flag=True, help="Fuzzy search your notes.")
@click.option(
    "--remove",
    "-r",
    is_flag=True,
    help="Remove the folder you specified.",
)
@click.option(
    "--export",
    "-ex",
    is_flag=True,
    help="Export your notes to the Desktop.",
)
def notes(folder, edit, add, delete, move, flist, search, remove, export):
    selection_notes_validation(
        folder, edit, delete, move, add, flist, search, remove, export
    )

    # Early returns for operations that don't need to fetch all notes
    # This dramatically improves performance for users with many notes

    if flist:
        folders = notes_folders()
        click.echo("\nFolders and subfolders in Notes:")
        click.echo(f"\n{folders}")
        return

    if add:
        add_note(folder)
        return

    if search:
        click.secho("\nFetching notes...\n", fg="yellow")
        fuzzy_notes()
        return

    if remove:
        folders = notes_folders()
        click.echo(f"\n{folders}")
        click.secho(
            "\n⚠️ Make sure the folder is empty, because the notes it includes will be deleted too.",
            fg="red",
        )
        folder_to_delete = click.prompt(
            "\nEnter the name of the folder to delete",
            type=str,
        )
        delete_note_folder(folder_to_delete)
        return

    if export:
        if click.confirm("\nAre you sure you want to export your notes to HTML?"):
            export_memo()
        return

    # Only fetch notes when actually needed (list, edit, delete, move)
    click.secho("\nFetching notes...", fg="yellow")
    notes_info = get_note()
    note_map = notes_info[0]
    notes_list = notes_info[1]
    notes_list_filter = [
        note for note in enumerate(notes_list, start=1) if folder in note[1]
    ]
    folders = notes_folders()

    if edit:
        note_id = pick_note(note_map, notes_list_filter, "edit")
        edit_note(note_id)
        return

    if move:
        note_id = pick_note(note_map, notes_list_filter, "move")
        if note_id is None:
            click.echo("Invalid selection.")
            return
        target_folder = click.prompt(
            "\nEnter the folder you want to move the note to", type=str
        )
        move_note(note_id, target_folder)
        return

    if delete:
        note_id = pick_note(note_map, notes_list_filter, "delete")
        delete_note(note_id)
        return

    # Default: list notes
    if folder not in folders:
        click.echo("\nThe folder does not exists.")
        click.echo("\nUse 'memo notes -fl' to see your folders")
    elif not notes_list_filter:
        click.echo("\nNo notes found.")
    else:
        title = f"Your Notes in folder {folder}:" if folder else "All your notes:"
        click.echo(f"\n{title}\n")
        for note in notes_list_filter:
            click.echo(f"{note[0]}. {note[1]}")


@cli.command()
@click.option(
    "--complete",
    "-c",
    is_flag=True,
    help="Mark a reminder as completed.",
)
@click.option(
    "--add",
    "-a",
    is_flag=True,
    help="Add a new reminder.",
)
@click.option(
    "--delete",
    "-d",
    is_flag=True,
    help="Delete a reminder.",
)
@click.option(
    "--edit",
    "-e",
    is_flag=True,
    help="Edit a reminder.",
)
def rem(complete, add, delete, edit):
    if add:
        add_reminder()
    else:
        today = datetime.datetime.today()
        modified_today = today - datetime.timedelta(days=1)
        reminders_info = get_reminder()
        reminders_map = reminders_info[0]
        reminders_list = reminders_info[1]
        reminders_list_filter = [
            reminder for reminder in enumerate(reminders_list, start=1)
        ]
        click.echo("\nYour Reminders:\n")
        for reminder in reminders_list_filter:
            reminder_dato = datetime.datetime.strptime(
                reminder[1].split(" | ")[1], "%Y-%m-%d %H:%M:%S"
            )
            dato_diff = reminder_dato - modified_today
            if dato_diff.days <= 1:
                due = (
                    f"Due on {dato_diff.days} day"
                    if dato_diff.days > 0
                    else "Due today"
                )
                click.secho(
                    f"{reminder[0]}. {reminder[1]} | {due}",
                    fg="red",
                )
            elif dato_diff.days <= 3:
                click.secho(
                    f"{reminder[0]}. {reminder[1]} | Due on {dato_diff.days} days",
                    fg="yellow",
                )
            else:
                click.echo(
                    f"{reminder[0]}. {reminder[1]} | Due on {dato_diff.days} days"
                )
        if complete:
            reminder_id = pick_reminder(
                reminders_map, reminders_list_filter, "complete"
            )
            complete_reminder(reminder_id)
        if delete:
            reminder_id = pick_reminder(reminders_map, reminders_list_filter, "delete")
            delete_reminder(reminder_id)
        if edit:
            reminder_id = pick_reminder(reminders_map, reminders_list_filter, "edit")
            part_to_edit = (
                click.prompt("\nEnter the part to edit ('title' or 'due date')")
                .strip()
                .lower()
            )
            edit_reminder(reminder_id, part_to_edit)
