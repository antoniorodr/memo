import click


def selection_notes_validation(folder, edit, delete, move, add, flist):
    used_flags = {
        "folder": bool(folder),
        "edit": edit,
        "delete": delete,
        "move": move,
        "add": add,
        "flist": flist,
    }

    if add and sum(used_flags.values()) > 1:
        raise click.UsageError(
            "--add must be used alone. It cannot be combined with other flags or --folder."
        )

    if flist and sum(used_flags.values()) > 1:
        raise click.UsageError(
            "--flist must be used alone. It cannot be combined with other flags or --folder."
        )

    modifier_flags = ["edit", "delete", "move"]
    used_modifiers = [f for f in modifier_flags if used_flags[f]]
    if len(used_modifiers) > 1:
        raise click.UsageError(
            "Only one of --edit, --delete, or --move can be used at a time."
        )
