"""Machine-friendly API for notes (non-interactive)."""

from memo_helpers.get_memo import get_note


def list_notes(folder="", format="tsv"):
    """Fetch notes without cache and return formatted output."""
    note_map, notes_list = get_note(use_cache=False)
    notes_list_filter = [
        note for note in enumerate(notes_list, start=1) if folder in note[1]
    ]
    lines = []
    seen_id = set()
    for idx, note_title in notes_list_filter:
        note_data = note_map.get(idx)
        if note_data is None:
            continue
        note_id, full_title = note_data
        if note_id in seen_id:
            continue
        seen_id.add(note_id)
        if " - " in full_title:
            folder_name, title = full_title.split(" - ", 1)
        else:
            folder_name, title = "", full_title
        if format == "tsv":
            lines.append(f"{note_id}\t{folder_name}\t{title}")
        elif format == "lines":
            lines.append(f"{note_id}|{folder_name}|{title}")
        elif format == "json":
            import json
            lines.append(
                json.dumps({"id": note_id, "folder": folder_name, "title": title})
            )
    return "\n".join(lines)
