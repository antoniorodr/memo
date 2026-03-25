import subprocess
import os
import sqlite3
import glob
import click


# ── Contact name resolution ─────────────────────────────────────────

_CONTACT_CACHE = {}


def _lookup_contact_name(phone):
    """Resolve a phone number to a contact name via macOS Contacts.

    Caches results to avoid repeated AppleScript calls.
    Returns the contact name or None if not found.
    """
    if not phone:
        return None
    if phone in _CONTACT_CACHE:
        return _CONTACT_CACHE[phone]

    # Normalise to last 9 digits for matching (strip country code).
    digits = phone.lstrip("+").lstrip("0")
    suffix = digits[-9:] if len(digits) >= 9 else digits

    # Try both international (+27...) and local (0...) formats.
    local_fmt = "0" + suffix if len(suffix) == 9 else phone

    script = f'''
    tell application "Contacts"
        set matchedPeople to (every person whose value of phones contains "{phone}")
        if (count of matchedPeople) = 0 then
            set matchedPeople to (every person whose value of phones contains "{local_fmt}")
        end if
        if (count of matchedPeople) > 0 then
            set p to item 1 of matchedPeople
            return (first name of p & " " & last name of p)
        end if
        return ""
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=5,
        )
        name = result.stdout.strip()
        _CONTACT_CACHE[phone] = name if name else None
        return _CONTACT_CACHE[phone]
    except Exception:
        _CONTACT_CACHE[phone] = None
        return None


# Path pattern for the NoteStore.sqlite database.
_NOTESTORE_GLOB = os.path.expanduser(
    "~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite"
)


def _find_notestore_db():
    """Locate the NoteStore.sqlite database file."""
    matches = glob.glob(_NOTESTORE_GLOB)
    return matches[0] if matches else _NOTESTORE_GLOB


def _extract_transcript_from_db(note_id):
    """Extract transcript text from NoteStore.sqlite.

    Apple stores call recording transcripts in the ZICCLOUDSYNCINGOBJECT
    table, specifically in the ``ZMERGEABLEDATA1`` column of the
    *attachment* record (the M4A audio), not the note record itself.

    The data is an Apple CRDT protobuf blob with alternating UUID,
    speaker phone number, and text segments.

    Returns the formatted transcript text or None.
    """
    db_path = _find_notestore_db()

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.OperationalError:
        return None

    try:
        # The note_id looks like: x-coredata://UUID/ICNote/pNNN
        note_pk = note_id.rsplit("/p", 1)[-1] if "/p" in note_id else None
        if not note_pk:
            return None

        # Get ZMERGEABLEDATA1 from the attachment record linked to the note.
        cursor = conn.execute(
            """
            SELECT ZMERGEABLEDATA1
            FROM ZICCLOUDSYNCINGOBJECT
            WHERE ZNOTE = ? AND ZMERGEABLEDATA1 IS NOT NULL
            LIMIT 1
            """,
            (int(note_pk),),
        )
        row = cursor.fetchone()
        if not row or not row[0]:
            return None

        return _parse_crdt_transcript(row[0])
    except Exception:
        return None
    finally:
        conn.close()


# ── CRArchive protobuf decoder ──────────────────────────────────────
#
# Apple stores call recording transcripts in ZMERGEABLEDATA1 as a
# CRArchive – an NSKeyedArchiver-like container built on protobuf.
# The archive has:
#   - object[]   (field 3)  – list of CRDT objects
#   - keyItem[]  (field 4)  – string keys for custom objects
#   - typeItem[] (field 5)  – type names (e.g. "com.apple.notes.ICTTTranscriptSegment")
#   - uuidItem[] (field 6)  – byte UUIDs
#
# Each object is one of: registerLatest, dictionary, string,
# custom (key-value with typed references), or orderedSet.
#
# The root object (object[0]) is an ICTTAudioRecording with keys:
#   callLocalSpeakerHandle, callRemoteSpeakerHandle, fragments, etc.
#
# Transcript segments are ICTTTranscriptSegment custom objects with:
#   speaker → NSString, text → NSString, timestamp → NSNumber.


def _uvarint(data, pos):
    """Decode an unsigned varint at *pos*, returning (value, new_pos)."""
    x = s = 0
    while True:
        b = data[pos]
        pos += 1
        x |= (b & 0x7F) << s
        if not (b & 0x80):
            return x, pos
        s += 7


def _readbytes(data, pos):
    length, pos = _uvarint(data, pos)
    return data[pos : pos + length], pos + length


def _readfixed(fmt, size):
    import struct as _struct

    return lambda data, pos: (_struct.unpack_from(fmt, data, pos)[0], pos + size)


_READERS = [
    _uvarint,            # 0: varint
    _readfixed("<d", 8), # 1: 64-bit
    _readbytes,          # 2: length-delimited
    None,                # 3: start group (unused)
    None,                # 4: end group (unused)
    _readfixed("<f", 4), # 5: 32-bit
]


def _parse_protobuf(data, schema):
    """Parse *data* using a schema dict.

    Schema format per field:
        field_number: ["name", is_repeated, sub_schema_or_type]
    where sub_schema_or_type is a nested dict (sub-message), ``"string"``
    (decode bytes as UTF-8), ``"bytes"`` (leave raw), or ``0`` (varint /
    float – keep as-is).
    """
    obj = {}
    pos = 0
    while pos < len(data):
        tag, pos = _uvarint(data, pos)
        wire_type = tag & 7
        field_num = tag >> 3
        if wire_type >= len(_READERS) or _READERS[wire_type] is None:
            break
        val, pos = _READERS[wire_type](data, pos)
        if field_num not in schema:
            continue
        name, repeated, typ = schema[field_num]
        if isinstance(typ, dict):
            val = _parse_protobuf(val, typ)
        elif typ == "string":
            val = val.decode("utf-8")
        if repeated:
            val = obj.get(name, []) + [val]
        obj[name] = val
    return obj


# ── Protobuf schemas for the CRArchive ─────────────────────────────

_S_OBJECTID = {
    2: ["unsignedIntegerValue", 0, 0],
    3: ["doubleValue", 0, 0],  # fixed64 – for NSNumber timestamps
    4: ["stringValue", 0, "string"],
    6: ["objectIndex", 0, 0],
}

_S_CUSTOM = {
    1: ["type", 0, 0],
    3: ["mapEntry", 1, {1: ["key", 0, 0], 2: ["value", 0, _S_OBJECTID]}],
}

_S_DICT = {
    1: ["element", 1, {
        1: ["key", 0, _S_OBJECTID],
        2: ["value", 0, _S_OBJECTID],
    }],
}

_S_STRING = {2: ["string", 0, "string"]}

_S_DOCOBJ = {
    1: ["registerLatest", 0, {2: ["contents", 0, _S_OBJECTID]}],
    6: ["dictionary", 0, _S_DICT],
    10: ["string", 0, _S_STRING],
    13: ["custom", 0, _S_CUSTOM],
}

_S_CRARCHIVE = {
    3: ["object", 1, _S_DOCOBJ],
    4: ["keyItem", 1, "string"],
    5: ["typeItem", 1, "string"],
    6: ["uuidItem", 1, "bytes"],
}


def _parse_crdt_transcript(data):
    """Parse a call recording transcript from a CRDT protobuf blob.

    Decodes the CRArchive structure, walks the object graph to extract
    ICTTTranscriptSegment entries, and assembles them into a formatted
    transcript with "You" / "Participant" speaker labels.

    Returns the formatted transcript as a string, or None.
    """
    try:
        archive = _parse_protobuf(data, _S_CRARCHIVE)
    except Exception:
        return None

    objects = archive.get("object", [])
    key_items = archive.get("keyItem", [])
    type_items = archive.get("typeItem", [])

    if not objects or not key_items or not type_items:
        return None

    # ── helpers for resolving object references ──

    def _resolve_string(obj_idx):
        """Follow registerLatest → NSString → self → stringValue."""
        if obj_idx >= len(objects):
            return None
        obj = objects[obj_idx]
        if "registerLatest" in obj:
            c = obj["registerLatest"].get("contents", {})
            if "objectIndex" in c:
                return _resolve_string(c["objectIndex"])
        if "custom" in obj:
            for me in obj["custom"].get("mapEntry", []):
                kn = key_items[me["key"]] if me["key"] < len(key_items) else ""
                if kn == "self":
                    if "stringValue" in me["value"]:
                        return me["value"]["stringValue"]
                    if "objectIndex" in me["value"]:
                        return _resolve_string(me["value"]["objectIndex"])
        if "string" in obj:
            return obj["string"].get("string")
        return None

    def _resolve_number(obj_idx):
        """Follow registerLatest → NSNumber → doubleValue chain."""
        if obj_idx >= len(objects):
            return None
        obj = objects[obj_idx]
        if "registerLatest" in obj:
            c = obj["registerLatest"].get("contents", {})
            if "objectIndex" in c:
                return _resolve_number(c["objectIndex"])
            if "unsignedIntegerValue" in c:
                return c["unsignedIntegerValue"]
            if "doubleValue" in c:
                return c["doubleValue"]
        if "custom" in obj:
            for me in obj["custom"].get("mapEntry", []):
                kn = (
                    key_items[me["key"]]
                    if me["key"] < len(key_items)
                    else ""
                )
                if kn == "doubleValue":
                    v = me["value"]
                    if "objectIndex" in v:
                        return _resolve_number(v["objectIndex"])
                    if "doubleValue" in v:
                        return v["doubleValue"]
                if kn == "integerValue":
                    v = me["value"]
                    if "objectIndex" in v:
                        return _resolve_number(v["objectIndex"])
                    if "unsignedIntegerValue" in v:
                        return v["unsignedIntegerValue"]
        return None

    def _root_map():
        """Build {key_name: value_ref} for the root custom object."""
        root = objects[0]
        if "custom" not in root:
            return {}
        return {
            key_items[e["key"]]: e["value"]
            for e in root["custom"].get("mapEntry", [])
            if e["key"] < len(key_items)
        }

    rmap = _root_map()

    # Get speaker handles from root ICTTAudioRecording.
    local_phone = (
        _resolve_string(rmap["callLocalSpeakerHandle"]["objectIndex"])
        if "callLocalSpeakerHandle" in rmap
        and "objectIndex" in rmap["callLocalSpeakerHandle"]
        else None
    )
    remote_phone = (
        _resolve_string(rmap["callRemoteSpeakerHandle"]["objectIndex"])
        if "callRemoteSpeakerHandle" in rmap
        and "objectIndex" in rmap["callRemoteSpeakerHandle"]
        else None
    )

    # ── collect transcript segments with timestamps ──

    raw_segments = []  # list of (timestamp, speaker_label, text)
    for obj in objects:
        if "custom" not in obj:
            continue
        typ_idx = obj["custom"]["type"]
        if typ_idx >= len(type_items):
            continue
        if "TranscriptSegment" not in type_items[typ_idx]:
            continue

        seg_map = {}
        for e in obj["custom"].get("mapEntry", []):
            if e["key"] < len(key_items):
                seg_map[key_items[e["key"]]] = e["value"]

        text = (
            _resolve_string(seg_map["text"]["objectIndex"])
            if "text" in seg_map and "objectIndex" in seg_map["text"]
            else None
        )
        speaker = (
            _resolve_string(seg_map["speaker"]["objectIndex"])
            if "speaker" in seg_map and "objectIndex" in seg_map["speaker"]
            else None
        )
        timestamp = (
            _resolve_number(seg_map["timestamp"]["objectIndex"])
            if "timestamp" in seg_map
            and "objectIndex" in seg_map["timestamp"]
            else None
        )

        if not text or not text.strip():
            continue

        # Resolve speaker to contact name or fallback label.
        if speaker == local_phone:
            label = _lookup_contact_name(local_phone) or "You"
        elif speaker == remote_phone:
            label = _lookup_contact_name(remote_phone) or "Participant"
        else:
            label = _lookup_contact_name(speaker) or speaker or "Unknown"

        raw_segments.append((timestamp or 0, label, text.strip()))

    if not raw_segments:
        return None

    # Sort by timestamp to get correct reading order.
    raw_segments.sort(key=lambda s: s[0])

    # ── merge consecutive same-speaker fragments ──

    merged = []
    prev_label = None
    buffer = []
    for _ts, label, text in raw_segments:
        if label == prev_label:
            buffer.append(text)
        else:
            if buffer:
                merged.append(f"**{prev_label}**: {' '.join(buffer)}")
            buffer = [text]
            prev_label = label
    if buffer:
        merged.append(f"**{prev_label}**: {' '.join(buffer)}")

    return "\n\n".join(merged) if merged else None


def get_recording_transcript(note_id):
    """Retrieve the transcript of a call recording.

    Apple stores transcripts in NoteStore.sqlite, NOT in the note body
    (which only contains the title).  Accessing the database requires
    Full Disk Access for the terminal application.

    Returns (transcript_text, note_title) or None on error.
    """
    # Try SQLite-based extraction first (requires Full Disk Access).
    transcript = _extract_transcript_from_db(note_id)

    # Get the note title via AppleScript (always works).
    title_script = f"""
    tell application "Notes"
        set n to first note whose id is "{note_id}"
        return name of n
    end tell
    """
    title_result = subprocess.run(
        ["osascript", "-e", title_script], capture_output=True, text=True
    )
    title = title_result.stdout.strip() if title_result.returncode == 0 else "Unknown"

    if transcript:
        return (f"# {title}\n\n{transcript}", title)

    # Fallback: transcript not accessible.
    return None


def get_recording_attachments(note_id):
    """List attachments in a call recording note.

    Returns a list of dicts with 'index', 'name', and 'content_id' keys,
    or an empty list on error.
    """
    script = f"""
    tell application "Notes"
        set n to first note whose id is "{note_id}"
        set attCount to count of attachments of n
        set attList to ""
        repeat with i from 1 to attCount
            set att to attachment i of n
            set attName to name of att
            set attCID to content identifier of att
            set attList to attList & i & "|" & attName & "|" & attCID & linefeed
        end repeat
        return attList
    end tell
    """

    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )

    if result.returncode != 0:
        return []

    attachments = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 2)
        if len(parts) >= 2:
            attachments.append(
                {
                    "index": int(parts[0]),
                    "name": parts[1],
                    "content_id": parts[2] if len(parts) > 2 else "",
                }
            )

    return attachments


def extract_recording_audio(note_id, output_path, attachment_index=1):
    """Extract the audio attachment from a call recording note to disk.

    By default extracts the first attachment (index=1) which is typically
    the audio file.  Uses AppleScript's ``save`` command to write the
    attachment directly to the output path.

    Returns the final output file path on success, or None on error.
    """
    # First get the attachment name to build the destination path.
    name_script = f"""
    tell application "Notes"
        set n to first note whose id is "{note_id}"
        set att to attachment {attachment_index} of n
        return name of att
    end tell
    """

    name_result = subprocess.run(
        ["osascript", "-e", name_script], capture_output=True, text=True
    )

    if name_result.returncode != 0:
        click.secho("\nError: Could not access recording attachment.", fg="red")
        click.secho(name_result.stderr.strip(), fg="red")
        return None

    att_name = name_result.stdout.strip()

    # Determine final output path.
    if os.path.isdir(output_path):
        dest_path = os.path.join(output_path, att_name)
    else:
        dest_path = output_path

    dest_dir = os.path.dirname(os.path.abspath(dest_path))
    os.makedirs(dest_dir, exist_ok=True)

    # Use AppleScript's save command to write the attachment to disk.
    # This bypasses the sandbox restrictions that prevent direct file
    # access to Notes' internal Media directory.
    save_script = f"""
    tell application "Notes"
        set n to first note whose id is "{note_id}"
        set att to attachment {attachment_index} of n
        save att in POSIX file "{dest_path}"
    end tell
    """

    save_result = subprocess.run(
        ["osascript", "-e", save_script], capture_output=True, text=True
    )

    if save_result.returncode != 0:
        click.secho("\nError: Could not extract recording.", fg="red")
        click.secho(save_result.stderr.strip(), fg="red")
        return None

    if not os.path.exists(dest_path):
        click.secho(
            f"\nError: File was not written to {dest_path}", fg="red"
        )
        return None

    return dest_path


def get_recording_metadata(note_id):
    """Fetch metadata for a call recording note.

    Returns a dict with name, creation_date, modification_date, and
    attachment_count, or None on error.
    """
    script = f"""
    tell application "Notes"
        set n to first note whose id is "{note_id}"
        set noteName to name of n
        set noteCreated to creation date of n as string
        set noteModified to modification date of n as string
        set attCount to count of attachments of n
        return noteName & "|" & noteCreated & "|" & noteModified & "|" & attCount
    end tell
    """

    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )

    if result.returncode != 0:
        return None

    parts = result.stdout.strip().split("|")
    if len(parts) < 4:
        return None

    return {
        "name": parts[0],
        "creation_date": parts[1],
        "modification_date": parts[2],
        "attachment_count": int(parts[3]),
    }
