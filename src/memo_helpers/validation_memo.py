import click


def selection_notes_validation(
    folder, edit, delete, move, add, flist, search, remove, export
):
    used_flags = {
        "folder": bool(folder),
        "edit": edit,
        "delete": delete,
        "move": move,
        "add": add,
        "flist": flist,
        "search": search,
        "remove": remove,
        "export": export,
    }

    if add and not folder:
        raise click.UsageError(
            "--add/ must be used indicating a folder to create the note to."
        )

    if flist and sum(used_flags.values()) > 1:
        raise click.UsageError(
            "--flist must be used alone. It cannot be combined with other flags or --folder."
        )

    modifier_flags = ["edit", "delete", "move", "remove", "search"]
    used_modifiers = [f for f in modifier_flags if used_flags[f]]
    if len(used_modifiers) > 1:
        raise click.UsageError(
            "Only one of --edit, --delete, --move, --remove or search can be used at a time."
        )
