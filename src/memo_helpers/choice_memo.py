import click


def pick_note(local_note_map, notes_list_filter, action):
    """Prompt the user to pick a note by its displayed local index.

    Args:
        local_note_map: dict mapping the 1-based local index shown to the user
            to a tuple ``(note_id, title)``.
        notes_list_filter: list of ``(local_index, title)`` tuples in display order.
        action: human-readable verb (e.g. ``"edit"``, ``"move"``, ``"delete"``).

    Returns:
        The selected note id string.

    Raises:
        IndexError: if the user enters an index outside the displayed range.
    """
    click.secho(
        "\nRemember: Due to AppleScript limitations, the images will be preserved at the end of the note.",
        fg="yellow",
    )
    choice = click.prompt(
        f"\nEnter the number of the note you want to {action}", type=int
    )
    if not 1 <= choice <= len(notes_list_filter):
        raise IndexError("The note you selected is not in the list.")
    note_data = local_note_map.get(choice)
    if note_data is None:
        click.echo("Invalid selection.")
        return None
    return note_data[0]


def pick_reminder(reminder_map, reminders_list, action):
    """Prompt the user to pick a reminder by its displayed local index.

    Args:
        reminder_map: dict mapping the 1-based local index shown to the user
            to a tuple ``(reminder_id, title, due_datetime)``.
        reminders_list: list of reminder display strings (used to size validation).
        action: human-readable verb (e.g. ``"complete"``, ``"delete"``).

    Returns:
        The selected reminder id string.

    Raises:
        IndexError: if the user enters an index outside the displayed range.
    """
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
