import subprocess
import click


def notes_folders():
    script = """
    tell application "Notes"
    set topLevelFolders to every folder
    set folderHierarchy to my listFolders(topLevelFolders, 0)
    return folderHierarchy
    end tell
    on listFolders(folders, indentLevel)
    set hierarchyText to ""
    set rootFolders to folders
    repeat with f in rootFolders
        set folderName to name of f
        set indent to my repeatChar(" ", indentLevel)
        set hierarchyText to hierarchyText & indent & folderName & return
        set subFolders to folder of f
        set xcount to count subFolders
        if xcount > 0 then
            set hierarchyText to hierarchyText & my listFolders(subFolders, indentLevel + 2)
        end if
    end repeat
    return hierarchyText
    end listFolders
    on repeatChar(theChar, xcount)
    set theString to ""
    repeat xcount times
        set theString to theString & theChar
    end repeat
    return theString
    end repeatChar
    """

    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running AppleScript: {e}")
