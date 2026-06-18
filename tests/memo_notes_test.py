from click.testing import CliRunner
from memo.memo import cli
from unittest.mock import patch, MagicMock

FAKE_NOTE_ID = "x-coredata://fake-id-123"
FAKE_NOTE_TITLE = "My Folder - Test Note"
FAKE_NOTE_MAP = {1: (FAKE_NOTE_ID, FAKE_NOTE_TITLE)}
FAKE_NOTES_LIST = [FAKE_NOTE_TITLE]
FAKE_FOLDERS = "My Folder"


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes"])
    assert result.exit_code == 0
    assert "All your notes:" in result.output


def test_notes_folder_without_folder_name():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--folder"])
    assert result.exit_code == 2
    assert "Error: Option '--folder' requires an argument." in result.output


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_folder_not_exists(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--folder", "ksndclskdnc"])
    assert result.exit_code == 0
    assert "The folder does not exists." in result.output


def test_notes_add_no_folder():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--add"])
    assert result.exit_code == 2
    assert (
        "Error: --add must be used indicating a folder to create the note to."
        in result.output
    )


@patch("memo.memo.edit_note")
@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_edit(mock_get_note, mock_notes_folders, mock_edit_note):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    mock_edit_note.return_value = None
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--edit"], input="1\n")
    assert "Enter the number of the note you want to edit:" in result.output


def test_notes_edit_indexerror():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--edit"], input="9999")
    assert result.exit_code == 1


@patch("memo_helpers.delete_memo.subprocess.run")
@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_delete(mock_get_note, mock_notes_folders, mock_subprocess):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    mock_subprocess.return_value = MagicMock(returncode=0, stderr="", stdout="")
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--delete"], input="1")
    assert result.exit_code == 0
    assert "Note deleted successfully." in result.output


def test_notes_delete_indexerror():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--delete"], input="9999")
    assert result.exit_code == 1


def test_notes_move_indexerror():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--move"], input="9999")
    assert result.exit_code == 1


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_flist(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--flist"])
    assert result.exit_code == 0
    assert "Folders and subfolders in Notes:" in result.output


@patch("memo.memo.id_search_memo")
@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_view(mock_get_note, mock_notes_folders, mock_id_search):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    mock_id_search.return_value = MagicMock(
        returncode=0, stdout="<div>Test content</div>", stderr=""
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--view", "1"])
    assert result.exit_code == 0


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_view_invalid(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--view", "99999"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_notes_view_combined_with_edit():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--view", "1", "--edit"])
    assert result.exit_code == 2
    assert "Only one of" in result.output


# Regression test for issue #48: `memo notes -e --folder <folder>` showed
# 1-based offsets into the unfiltered notes list as the selection number, but
# `pick_note` was passing that number to `note_map.get(choice)` (the global
# note map). When the user selected a note whose global key was outside the
# filtered range, or whose local index differed from the global key, this
# raised IndexError or picked the wrong note. After the fix, the displayed
# numbers are sequential local indices and the correct note is selected.

@patch("memo.memo.edit_note")
@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_edit_with_folder_uses_local_index(
    mock_get_note, mock_notes_folders, mock_edit
):
    # 5 notes, only notes 2 and 4 are in ExampleFolder. The bug would cause
    # picking local #2 to either fail or select the wrong note because the
    # global note_map key for "ExampleFolder - Note 2" is also 2 — but with
    # notes_list containing non-folder entries, the displayed numbers (1, 2)
    # no longer line up with global note_map keys for all configurations.
    note_map = {
        1: ("id-1", "Other - Note 1"),
        2: ("id-2", "ExampleFolder - Note 2"),
        3: ("id-3", "Other - Note 3"),
        4: ("id-4", "ExampleFolder - Note 4"),
        5: ("id-5", "Other - Note 5"),
    }
    notes_list = [note_map[k][1] for k in note_map]
    mock_get_note.return_value = [note_map, notes_list]
    mock_notes_folders.return_value = "ExampleFolder"
    mock_edit.return_value = None
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "--folder", "ExampleFolder", "--edit"], input="2\n"
    )
    assert result.exit_code == 0, result.output
    # "2" should select the second note in the filtered list, which is
    # global key 4 ("ExampleFolder - Note 4") with id "id-4".
    mock_edit.assert_called_once_with("id-4")
    # The displayed list should show local indices, not global keys.
    assert "1. ExampleFolder - Note 2" in result.output
    assert "2. ExampleFolder - Note 4" in result.output
