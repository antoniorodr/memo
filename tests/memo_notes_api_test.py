from click.testing import CliRunner
from memo.memo import cli
from unittest.mock import patch, MagicMock

from tests.memo_notes_test import (
    FAKE_NOTE_ID,
    FAKE_NOTE_TITLE,
    FAKE_NOTE_MAP,
    FAKE_NOTES_LIST,
    FAKE_FOLDERS,
)


@patch("memo.memo.list_notes")
def test_api_list_default_tsv(mock_list_notes):
    mock_list_notes.return_value = f"{FAKE_NOTE_ID}\t{FAKE_FOLDERS}\t{FAKE_NOTE_TITLE}"
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "list"])
    assert result.exit_code == 0
    assert FAKE_NOTE_ID in result.output
    assert FAKE_FOLDERS in result.output
    assert FAKE_NOTE_TITLE in result.output
    mock_list_notes.assert_called_once_with(folder="", format="tsv")


@patch("memo.memo.list_notes")
def test_api_list_with_folder_and_json(mock_list_notes):
    mock_list_notes.return_value = (
        f'{{"id": "{FAKE_NOTE_ID}", "folder": "{FAKE_FOLDERS}", "title": "{FAKE_NOTE_TITLE}"}}'
    )
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "api", "list", "--folder", FAKE_FOLDERS, "--format", "json"]
    )
    assert result.exit_code == 0
    assert FAKE_NOTE_ID in result.output
    assert FAKE_FOLDERS in result.output
    assert FAKE_NOTE_TITLE in result.output
    mock_list_notes.assert_called_once_with(folder=FAKE_FOLDERS, format="json")


@patch("memo.memo.show_note")
def test_api_show_success(mock_show_note):
    mock_show_note.return_value = ("# Title\n\nBody", None)
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "show", "note-id"])
    assert result.exit_code == 0
    assert "# Title" in result.output
    mock_show_note.assert_called_once_with("note-id")


@patch("memo.memo.show_note")
def test_api_show_error(mock_show_note):
    mock_show_note.return_value = (None, "Failed to fetch")
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "show", "note-id"])
    assert result.exit_code == 2
    assert "Failed to fetch" in result.output


@patch("memo.memo._read_stdin_content")
def test_api_edit_requires_stdin(mock_read_stdin):
    mock_read_stdin.return_value = None
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "edit", "note-id"])
    assert result.exit_code == 1
    assert "No input provided" in result.output


@patch("memo.memo.edit_note_stdin")
@patch("memo.memo._read_stdin_content")
def test_api_edit_success(mock_read_stdin, mock_edit_note_stdin):
    mock_read_stdin.return_value = "# Updated"
    mock_edit_note_stdin.return_value = (True, None)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "api", "edit", "note-id"], input="# Updated"
    )
    assert result.exit_code == 0
    mock_edit_note_stdin.assert_called_once_with("note-id", "# Updated")


@patch("memo.memo.edit_note_stdin")
@patch("memo.memo._read_stdin_content")
def test_api_edit_failure(mock_read_stdin, mock_edit_note_stdin):
    mock_read_stdin.return_value = "# Updated"
    mock_edit_note_stdin.return_value = (False, "Failed to update note.")
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "api", "edit", "note-id"], input="# Updated"
    )
    assert result.exit_code == 3
    assert "Failed to update note." in result.output


@patch("memo.memo._read_stdin_content")
def test_api_add_requires_stdin(mock_read_stdin):
    mock_read_stdin.return_value = None
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "add", "--folder", "Work"])
    assert result.exit_code == 1
    assert "No input provided" in result.output


@patch("memo.memo.add_note_stdin")
@patch("memo.memo._read_stdin_content")
def test_api_add_success(mock_read_stdin, mock_add_note_stdin):
    mock_read_stdin.return_value = "# New note"
    mock_add_note_stdin.return_value = (True, None)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "api", "add", "--folder", "Work"], input="# New note"
    )
    assert result.exit_code == 0
    mock_add_note_stdin.assert_called_once_with("Work", "# New note")


@patch("memo.memo.add_note_stdin")
@patch("memo.memo._read_stdin_content")
def test_api_add_failure(mock_read_stdin, mock_add_note_stdin):
    mock_read_stdin.return_value = "# New note"
    mock_add_note_stdin.return_value = (False, "Failed to create note.")
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "api", "add", "--folder", "Work"], input="# New note"
    )
    assert result.exit_code == 3
    assert "Failed to create note." in result.output


def test_api_add_requires_folder():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "add"])
    assert result.exit_code == 2
    assert "Missing option '--folder'" in result.output


@patch("memo.memo.delete_note")
def test_api_delete_success(mock_delete_note):
    mock_delete_note.return_value = (True, None)
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "delete", "note-id"])
    assert result.exit_code == 0
    mock_delete_note.assert_called_once_with("note-id", quiet=True)


@patch("memo.memo.delete_note")
def test_api_delete_failure(mock_delete_note):
    mock_delete_note.return_value = (False, "Failed to delete note.")
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "delete", "note-id"])
    assert result.exit_code == 3
    assert "Failed to delete note." in result.output


@patch("memo.memo.move_note")
def test_api_move_success(mock_move_note):
    mock_move_note.return_value = (True, None)
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "move", "note-id", "Target"])
    assert result.exit_code == 0
    mock_move_note.assert_called_once_with("note-id", "Target", quiet=True)


@patch("memo.memo.move_note")
def test_api_move_failure(mock_move_note):
    mock_move_note.return_value = (False, "Failed to move note.")
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "move", "note-id", "Target"])
    assert result.exit_code == 3
    assert "Failed to move note." in result.output


@patch("memo.memo.list_folders")
def test_api_folders_default_format(mock_list_folders):
    mock_list_folders.return_value = "Work\nPersonal"
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "folders"])
    assert result.exit_code == 0
    assert "Work" in result.output
    assert "Personal" in result.output
    mock_list_folders.assert_called_once_with(format="tsv")


@patch("memo.memo.list_folders")
def test_api_folders_json_format(mock_list_folders):
    mock_list_folders.return_value = '{"path": "Work"}'
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "folders", "--format", "json"])
    assert result.exit_code == 0
    assert '{"path": "Work"}' in result.output
    mock_list_folders.assert_called_once_with(format="json")


@patch("memo.memo.search_notes")
def test_api_search_title_only(mock_search_notes):
    mock_search_notes.return_value = (
        f"{FAKE_NOTE_ID}\t{FAKE_FOLDERS}\t{FAKE_NOTE_TITLE}"
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "search", "Test"])
    assert result.exit_code == 0
    assert FAKE_NOTE_ID in result.output
    assert FAKE_FOLDERS in result.output
    assert FAKE_NOTE_TITLE in result.output
    mock_search_notes.assert_called_once_with("Test", "", "tsv", search_body=False)


@patch("memo.memo.search_notes")
def test_api_search_with_options(mock_search_notes):
    mock_search_notes.return_value = (
        f"{FAKE_NOTE_ID}\t{FAKE_FOLDERS}\t{FAKE_NOTE_TITLE}"
    )
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "notes",
            "api",
            "search",
            "Test",
            "--folder",
            FAKE_FOLDERS,
            "--format",
            "json",
            "--body",
        ],
    )
    assert result.exit_code == 0
    assert FAKE_NOTE_ID in result.output
    assert FAKE_FOLDERS in result.output
    assert FAKE_NOTE_TITLE in result.output
    mock_search_notes.assert_called_once_with(
        "Test", FAKE_FOLDERS, "json", search_body=True
    )


def test_api_remove_requires_force_flag():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "api", "remove", "Work"])
    assert result.exit_code == 2
    assert "Missing option '--force'" in result.output


@patch("memo.memo.delete_note_folder")
def test_api_remove_success(mock_delete_note_folder):
    mock_delete_note_folder.return_value = (True, None)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "api", "remove", "Work/Meetings", "--force"]
    )
    assert result.exit_code == 0
    mock_delete_note_folder.assert_called_once_with("Work/Meetings", quiet=True)


@patch("memo.memo.delete_note_folder")
def test_api_remove_failure(mock_delete_note_folder):
    mock_delete_note_folder.return_value = (False, "Failed to remove folder.")
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "api", "remove", "Work/Meetings", "--force"]
    )
    assert result.exit_code == 3
    assert "Failed to remove folder." in result.output


@patch("memo.memo.os.makedirs")
@patch("memo.memo.os.path.exists")
@patch("memo.memo.export_memo")
def test_api_export_creates_directory_and_exports(
    mock_export_memo, mock_path_exists, mock_makedirs
):
    mock_path_exists.return_value = False
    mock_export_memo.return_value = (True, None)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "api", "export", "--path", "/tmp/memo-export"]
    )
    assert result.exit_code == 0
    mock_path_exists.assert_any_call("/tmp/memo-export")
    mock_makedirs.assert_called_once_with("/tmp/memo-export", exist_ok=True)
    mock_export_memo.assert_called_once_with(
        "/tmp/memo-export", quiet=True, to_markdown=False
    )


@patch("memo.memo.os.path.exists")
@patch("memo.memo.export_memo")
def test_api_export_failure(mock_export_memo, mock_path_exists):
    mock_path_exists.return_value = True
    mock_export_memo.return_value = (False, "Failed to export.")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "notes",
            "api",
            "export",
            "--path",
            "/tmp/memo-export",
            "--markdown",
        ],
    )
    assert result.exit_code == 3
    assert "Failed to export." in result.output
    mock_export_memo.assert_called_once_with(
        "/tmp/memo-export", quiet=True, to_markdown=True
    )

