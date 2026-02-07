import subprocess
import click

FOLDER_SEPARATOR = "|||"


def _build_tree(folders_with_parents):
    """Build a folder tree from a flat list of (name, parent) tuples."""
    children = {}
    for name, parent in folders_with_parents:
        children.setdefault(parent, []).append(name)
    return children


def _render_tree(children, parent="", indent=0):
    """Render the folder tree as indented text."""
    lines = []
    for name in children.get(parent, []):
        lines.append(" " * indent + name)
        if name in children:
            lines.extend(_render_tree(children, name, indent + 2))
    return lines


def notes_folders():
    script = f"""
    tell application "Notes"
    set output to ""
    repeat with f in every folder
        set fName to name of f
        try
            set c to container of f
            set cClass to class of c as text
            if cClass is "folder" then
                set parentName to name of c
            else
                set parentName to ""
            end if
        on error
            set parentName to ""
        end try
        set output to output & fName & "{FOLDER_SEPARATOR}" & parentName & linefeed
    end repeat
    return output
    end tell
    """

    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, check=True
        )
        raw = result.stdout.strip()
        if not raw:
            return ""

        folders_with_parents = []
        for line in raw.split("\n"):
            if FOLDER_SEPARATOR in line:
                name, parent = line.split(FOLDER_SEPARATOR, 1)
                folders_with_parents.append((name.strip(), parent.strip()))

        children = _build_tree(folders_with_parents)
        lines = _render_tree(children)
        return "\n".join(lines)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running AppleScript: {e}")
        return ""
