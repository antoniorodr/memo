import click


def pick_note(note_map, notes_list, action):
    choice = click.prompt(
        f"\nEnter the number of the note you want to {action}", type=int
    )
    if 1 <= choice <= len(notes_list):
        note_data = note_map.get(choice)
        if note_data is None:
            click.echo("Invalid selection.")
            return
        return note_data[0]
    else:
        click.echo("Invalid selection.")
