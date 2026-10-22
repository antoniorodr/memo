import click


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


def pick_reminder(reminder_map, reminders_list, action):
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
