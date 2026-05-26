from click.testing import CliRunner
from memo.memo import cli
from unittest.mock import patch, MagicMock

FAKE_NOTE_ID = "x-coredata://fake-id-123"
FAKE_NOTE_TITLE = "My Folder - Test Note"
FAKE_NOTE_MAP = {1: (FAKE_NOTE_ID, FAKE_NOTE_TITLE)}
FAKE_NOTES_LIST = [FAKE_NOTE_TITLE]
FAKE_FOLDERS = "My Folder"
FAKE_NESTED_FOLDER = "Projects/Memo"
FAKE_NESTED_FOLDERS = "Projects\n  Memo\nArchive"
FAKE_NESTED_NOTE_TITLE = "Projects/Memo - Nested Note"
FAKE_PARENT_NOTE_TITLE = "Projects - Parent Note"
FAKE_ALPHA_REPORTS_NOTE_TITLE = "Alpha/Reports - Summary note"
FAKE_BETA_REPORTS_NOTE_TITLE = "Beta/Reports - Summary note"
FAKE_LEAF_ONLY_NOTE_TITLE = "Reports - Summary note"
FAKE_DUPLICATE_LEAF_FOLDERS = "Alpha\n  Reports\nBeta\n  Reports"


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


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_folder_supports_subfolder_path(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [
        {
            1: (FAKE_NOTE_ID, FAKE_NESTED_NOTE_TITLE),
            2: ("x-coredata://fake-id-456", FAKE_PARENT_NOTE_TITLE),
        },
        [FAKE_NESTED_NOTE_TITLE, FAKE_PARENT_NOTE_TITLE],
    ]
    mock_notes_folders.return_value = FAKE_NESTED_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--folder", FAKE_NESTED_FOLDER])
    assert result.exit_code == 0
    assert f"Your Notes in folder {FAKE_NESTED_FOLDER}:" in result.output
    assert FAKE_NESTED_NOTE_TITLE in result.output
    assert FAKE_PARENT_NOTE_TITLE not in result.output


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_folder_resolves_unique_subfolder_name(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [
        {1: (FAKE_NOTE_ID, FAKE_NESTED_NOTE_TITLE)},
        [FAKE_NESTED_NOTE_TITLE],
    ]
    mock_notes_folders.return_value = FAKE_NESTED_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--folder", "Memo"])
    assert result.exit_code == 0
    assert f"Your Notes in folder {FAKE_NESTED_FOLDER}:" in result.output
    assert FAKE_NESTED_NOTE_TITLE in result.output


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_folder_filters_duplicate_leaf_paths_by_full_path(
    mock_get_note, mock_notes_folders
):
    mock_get_note.return_value = [
        {
            1: (FAKE_NOTE_ID, FAKE_ALPHA_REPORTS_NOTE_TITLE),
            2: ("x-coredata://fake-id-456", FAKE_BETA_REPORTS_NOTE_TITLE),
            3: ("x-coredata://fake-id-789", FAKE_LEAF_ONLY_NOTE_TITLE),
        },
        [
            FAKE_ALPHA_REPORTS_NOTE_TITLE,
            FAKE_BETA_REPORTS_NOTE_TITLE,
            FAKE_LEAF_ONLY_NOTE_TITLE,
        ],
    ]
    mock_notes_folders.return_value = FAKE_DUPLICATE_LEAF_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--folder", "Alpha/Reports"])
    assert result.exit_code == 0
    assert "Your Notes in folder Alpha/Reports:" in result.output
    assert FAKE_ALPHA_REPORTS_NOTE_TITLE in result.output
    assert f"2. {FAKE_BETA_REPORTS_NOTE_TITLE}" not in result.output
    assert f"3. {FAKE_LEAF_ONLY_NOTE_TITLE}" not in result.output
    assert f"1. {FAKE_LEAF_ONLY_NOTE_TITLE}" not in result.output


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_folder_rejects_ambiguous_leaf_name(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [
        {
            1: (FAKE_NOTE_ID, FAKE_ALPHA_REPORTS_NOTE_TITLE),
            2: ("x-coredata://fake-id-456", FAKE_BETA_REPORTS_NOTE_TITLE),
        },
        [FAKE_ALPHA_REPORTS_NOTE_TITLE, FAKE_BETA_REPORTS_NOTE_TITLE],
    ]
    mock_notes_folders.return_value = FAKE_DUPLICATE_LEAF_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--folder", "Reports"])
    assert result.exit_code == 0
    assert "The folder does not exists." in result.output


@patch("memo.memo.clear_cache")
@patch("memo.memo.add_note")
@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_add_uses_resolved_subfolder_path(
    mock_get_note, mock_notes_folders, mock_add_note, mock_clear_cache
):
    mock_get_note.return_value = [
        {1: (FAKE_NOTE_ID, FAKE_NESTED_NOTE_TITLE)},
        [FAKE_NESTED_NOTE_TITLE],
    ]
    mock_notes_folders.return_value = FAKE_NESTED_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--folder", "Memo", "--add"])
    assert result.exit_code == 0
    mock_add_note.assert_called_once_with(FAKE_NESTED_FOLDER)
    mock_clear_cache.assert_called_once()


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


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_edit_indexerror(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
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


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_delete_indexerror(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--delete"], input="9999")
    assert result.exit_code == 1


@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_move_indexerror(mock_get_note, mock_notes_folders):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
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
