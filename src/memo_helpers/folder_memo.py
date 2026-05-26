PATH_SEPARATOR = "/"


def normalize_folder_path(folder_path: str | None) -> str:
    if not folder_path:
        return ""
    return PATH_SEPARATOR.join(
        part.strip() for part in folder_path.split(PATH_SEPARATOR) if part.strip()
    )


def folder_paths_from_tree(folders_tree: str) -> list[str]:
    paths_by_level: dict[int, str] = {}
    folder_paths = []

    for line in folders_tree.splitlines():
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        level = indent // 2
        name = line.strip()
        parent_path = paths_by_level.get(level - 1, "")
        folder_path = normalize_folder_path(
            f"{parent_path}{PATH_SEPARATOR}{name}" if parent_path else name
        )

        paths_by_level[level] = folder_path
        for deeper_level in [key for key in paths_by_level if key > level]:
            del paths_by_level[deeper_level]

        folder_paths.append(folder_path)

    return folder_paths


def resolve_folder_path(folder_path: str, known_folder_paths: list[str]) -> str:
    requested_path = normalize_folder_path(folder_path)
    normalized_paths = [normalize_folder_path(path) for path in known_folder_paths]

    if requested_path in normalized_paths:
        return requested_path

    matching_basenames = [
        path
        for path in normalized_paths
        if path.split(PATH_SEPARATOR)[-1] == requested_path
    ]
    if len(matching_basenames) == 1:
        return matching_basenames[0]

    return ""


def note_belongs_to_folder(note_title: str, folder_path: str) -> bool:
    normalized_folder = normalize_folder_path(folder_path)
    if not normalized_folder:
        return True

    folder_prefix = f"{normalized_folder} - "
    if note_title.startswith(folder_prefix):
        return True

    # Older cache entries stored only the leaf folder name. Only allow this
    # fallback for unambiguous single-segment folder filters.
    if PATH_SEPARATOR in normalized_folder:
        return False

    folder_name = normalized_folder.split(PATH_SEPARATOR)[-1]
    return note_title.startswith(f"{folder_name} - ")


def applescript_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def applescript_list(values: list[str]) -> str:
    return "{" + ", ".join(applescript_string(value) for value in values) + "}"


def folder_lookup_script(folder_path: str, variable_name: str = "targetFolder") -> str:
    normalized_path = normalize_folder_path(folder_path)
    parts = normalized_path.split(PATH_SEPARATOR)
    if not parts or parts == [""]:
        raise ValueError("folder_path must not be empty")

    return f"""
        set folderPathParts to {applescript_list(parts)}
        set {variable_name} to missing value
        repeat with acc in accounts
            try
                set candidateFolder to folder (item 1 of folderPathParts) of acc
                if (count of folderPathParts) > 1 then
                    repeat with folderIndex from 2 to count of folderPathParts
                        set candidateFolder to folder (item folderIndex of folderPathParts) of candidateFolder
                    end repeat
                end if
                set {variable_name} to candidateFolder
                exit repeat
            end try
        end repeat
        if {variable_name} is missing value and (count of folderPathParts) is 1 then
            try
                set {variable_name} to first folder whose name is (item 1 of folderPathParts)
            end try
        end if
        if {variable_name} is missing value then
            error {applescript_string(f"Folder {normalized_path} not found")}
        end if
    """


def folder_path_handler_script() -> str:
    return """
    on folderPath(folderId)
        tell application "Notes"
            set theFolder to first folder whose id is folderId
            set pathParts to {name of theFolder as text}
            try
                set currentContainer to container of theFolder
                repeat
                    try
                        if (class of currentContainer as text) is "folder" then
                            set beginning of pathParts to name of currentContainer as text
                            set currentContainer to container of currentContainer
                        else
                            exit repeat
                        end if
                    on error
                        exit repeat
                    end try
                end repeat
            end try
            set previousDelimiters to AppleScript's text item delimiters
            set AppleScript's text item delimiters to "/"
            set folderPathValue to pathParts as text
            set AppleScript's text item delimiters to previousDelimiters
            return folderPathValue
        end tell
    end folderPath
    """
