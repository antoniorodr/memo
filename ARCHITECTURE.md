# Technical Architecture - Call Recording Support

## System Overview

Memo now includes read-only support for Apple Notes call recordings (iOS 18.1+). This document describes the implemented architecture for listing, viewing transcripts, extracting audio, and searching call recordings.

> **Design principle**: No external dependencies. Apple already provides on-device transcription for call recordings, so no AI/cloud transcription services are needed.

## Architecture

### Component Diagram
```
┌──────────────────────────────────────────────────────────────┐
│                         Memo CLI                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │   memo.py   │  │ Click CLI    │  │  Command Groups     │ │
│  │   (main)    │──│  Framework   │──│  - notes             │ │
│  └─────────────┘  └──────────────┘  │  - rem               │ │
│                                      │  - recordings (NEW)  │ │
│                                      └─────────────────────┘ │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           v
┌──────────────────────────────────────────────────────────────┐
│                     Memo Helpers                              │
│  ┌──────────────┐  ┌───────────────────┐  ┌───────────────┐ │
│  │  Existing    │  │  Recordings (NEW) │  │  Search       │ │
│  │  - get_memo  │  │  - get_recordings │  │  - fuzzy_notes│ │
│  │  - add_memo  │  │  - recording_utils│  │  - fuzzy_rec. │ │
│  │  - edit_memo │  └───────────────────┘  │  - _run_fzf   │ │
│  │  - export    │                          └───────────────┘ │
│  │  - cache     │                                             │
│  │  - md_conv.  │                                             │
│  └──────────────┘                                             │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           v
┌──────────────────────────────────────────────────────────────┐
│                   AppleScript Bridge                          │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  subprocess.run(["osascript", "-e", script])         │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           v
┌──────────────────────────────────────────────────────────────┐
│                      Apple Notes                              │
│  ┌──────────────┐  ┌─────────────────────────────────────┐   │
│  │   Folders    │  │             Notes                    │   │
│  │              │  │  ┌────────────────────────────────┐  │   │
│  │  (Smart)     │  │  │  Body (HTML)                   │  │   │
│  │  Call Rec.   │  │  │  - Auto-generated transcript   │  │   │
│  │              │  │  │  - Speaker labels               │  │   │
│  │  (Regular)   │  │  └────────────────────────────────┘  │   │
│  │  Notes       │  │  ┌────────────────────────────────┐  │   │
│  │  Imported    │  │  │  Attachments                   │  │   │
│  │              │  │  │  - Audio (M4A)                 │  │   │
│  │              │  │  │  - Images (existing support)   │  │   │
│  └──────────────┘  └─────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

#### List Recordings
```
User: memo recordings
  → get_recordings() [AppleScript: smart folder → name-pattern fallback]
  → Display numbered list with dates
```

#### View Transcript
```
User: memo recordings -v N
  → get_recordings() → note_id
  → get_recording_transcript(note_id) → id_search_memo → md_converter
  → Print markdown to stdout
```

#### Extract Audio
```
User: memo recordings -x N -o /path
  → get_recordings() → note_id
  → extract_recording_audio(note_id, output_path)
    → AppleScript: get attachment name
    → AppleScript: save att in POSIX file "/path/name.m4a"
  → Print success message
```

#### Search Transcripts
```
User: memo recordings -s
  → fuzzy_recordings()
    → get_recordings() → all recordings
    → _populate_temp_dir() → markdown files in tmpdir
    → _run_fzf(tmpdir, "Call Recordings")
```

## Module Architecture

### New Modules

#### `get_recordings.py`

Fetches call recordings using a **dual detection strategy**:

1. **Smart folder** — `folder "Call Recordings"` accessed directly by name (system-level smart folder, not in `folders` enumeration)
2. **Name pattern fallback** — scans all notes for names starting with `"Call with"`

```python
def _parse_recordings_output(stdout) -> tuple[dict, list]:
    """Parse pipe-delimited AppleScript output."""

def get_recordings() -> tuple[dict, list]:
    """Returns (recording_map, recordings_list) matching get_note() format."""
```

> **Why dual strategy?** The "Call Recordings" folder is a system-level smart folder that doesn't appear in AppleScript's `folders` enumeration. Accessing it by name works but may fail on non-English locales or older macOS versions.

#### `recording_utils.py`

Utility functions for individual recordings:

```python
def get_recording_transcript(note_id) -> tuple | None:
    """Fetch note body HTML → markdown via id_search_memo + md_converter."""

def get_recording_attachments(note_id) -> list[dict]:
    """List attachments with index, name, content_id."""

def extract_recording_audio(note_id, output_path, attachment_index=1) -> str | None:
    """Extract audio using AppleScript's `save att in POSIX file`."""

def get_recording_metadata(note_id) -> dict | None:
    """Fetch name, creation_date, modification_date, attachment_count."""
```

### Modified Modules

#### `search_memo.py`

Refactored to extract reusable helpers:

```python
def _run_fzf(directory, label="Your Notes"):
    """Shared fzf invocation with customizable border label."""

def _populate_temp_dir(tmpdirname, note_map_items):
    """Write markdown files for each note into a temp directory."""

def fuzzy_notes():        # Existing, now uses _run_fzf
def fuzzy_recordings():   # NEW — searches recording transcripts
```

#### `memo.py`

Added `recordings` command:

```python
@cli.command()
@click.option("--view", "-v", type=int)
@click.option("--extract", "-x", type=int)
@click.option("--output", "-o", type=str)
@click.option("--search", "-s", is_flag=True)
def recordings(view, extract, output, search):
```

## AppleScript API Reference

### Call Recording Specifics

#### Smart Folder Access
```applescript
-- Access system-level smart folder directly by name
tell application "Notes"
    set recFolder to folder "Call Recordings"
    set noteIDs to id of every note of recFolder
end tell
```

> **Note**: This folder does NOT appear in `folders` enumeration. It must be accessed by name.

#### Attachment Extraction
```applescript
-- WORKS: save command writes attachment to disk
tell application "Notes"
    set n to first note whose id is "NOTE_ID"
    set att to attachment 1 of n
    save att in POSIX file "/path/to/output.m4a"
end tell
```

> **Critical**: Call recording attachments **cannot** be coerced to alias, text, or furl. The standard pattern `POSIX path of (file of att as alias)` fails with error -1700. Only `save att in POSIX file` works.

#### Attachment Properties
```applescript
-- Get attachment name and content identifier
tell application "Notes"
    set n to first note whose id is "NOTE_ID"
    set att to attachment 1 of n
    return {name of att, content identifier of att}
end tell
```

> **Note**: Use `content identifier` (two words) not `contentIdentifier` (camelCase).

### Known Limitations

1. **Smart folder visibility**: "Call Recordings" doesn't appear in `folders` enumeration — must use direct name access or name-pattern fallback
2. **Attachment coercion**: `file of att as alias`, `contents as alias/text/furl` all fail with -1700 for call recording attachments
3. **Sandbox**: Terminal cannot access `~/Library/Group Containers/group.com.apple.notes/` directly ("Operation not permitted") — must use AppleScript's `save` command
4. **Attachment position**: Attachments always appear at the end of the note body
5. **iCloud sync latency**: Recordings made on iPhone may take time to sync to Mac

## Testing Architecture

### Test Structure
```
tests/
├── memo_notes_test.py          # Existing notes CLI tests (12 tests)
├── memo_rem_test.py            # Existing reminders tests
├── test_md_converter_images.py # Existing image roundtrip tests (7 tests)
└── test_recordings.py          # NEW: recordings tests (12 tests)
```

### Test Pattern

All tests mock `subprocess.run` and use `click.testing.CliRunner`:

```python
@patch("memo.memo.get_recordings")
def test_recordings_list(mock_get_recordings):
    mock_get_recordings.return_value = (FAKE_MAP, FAKE_LIST)
    runner = CliRunner()
    result = runner.invoke(cli, ["recordings"])
    assert "Your Call Recordings:" in result.output
```

### Coverage

| Module | Coverage |
|---|---|
| `get_recordings.py` | 100% |
| `recording_utils.py` | 58% (uncovered: error branches requiring real AppleScript) |
| `memo.py` (recordings cmd) | 78% |

## Backward Compatibility

All changes are **additive** — the new `recordings` command doesn't affect existing `notes` or `rem` commands. No configuration files, no new dependencies, no cache format changes.

### Change Log
- 2026-03-24: Implemented call recording support (list, view, extract, search)
- 2024-03-24: Initial architecture document created
