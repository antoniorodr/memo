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


# --- Non-interactive add tests ---


@patch("memo_helpers.add_memo.subprocess.run")
@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_add_noninteractive_title_and_body(
    mock_get_note, mock_notes_folders, mock_subprocess
):
    """--title and --body skip the editor and create the note directly."""
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    mock_subprocess.return_value = MagicMock(returncode=0, stderr="", stdout="")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "notes",
            "--add",
            "--folder", "My Folder",
            "--title", "My Test Note",
            "--body", "Hello from the test.",
        ],
    )
    assert result.exit_code == 0
    assert "Note created in 'My Folder' folder." in result.output
    # The editor must NOT have been opened — only osascript should have been called.
    called_commands = [call.args[0] for call in mock_subprocess.call_args_list]
    assert all(cmd[0] == "osascript" for cmd in called_commands)


@patch("memo_helpers.add_memo.subprocess.run")
@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_add_noninteractive_title_only(
    mock_get_note, mock_notes_folders, mock_subprocess
):
    """--title without --body creates a note with a title and no body."""
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    mock_subprocess.return_value = MagicMock(returncode=0, stderr="", stdout="")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["notes", "--add", "--folder", "My Folder", "--title", "Title Only"],
    )
    assert result.exit_code == 0
    assert "Note created in 'My Folder' folder." in result.output


def test_notes_add_title_without_add_flag():
    """--title without --add should raise a UsageError."""
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "--folder", "My Folder", "--title", "Orphaned Title"]
    )
    assert result.exit_code == 2
    assert "--title and --body must be used with --add." in result.output


def test_notes_add_body_without_add_flag():
    """--body without --add should raise a UsageError."""
    runner = CliRunner()
    result = runner.invoke(
        cli, ["notes", "--folder", "My Folder", "--body", "Orphaned body"]
    )
    assert result.exit_code == 2
    assert "--title and --body must be used with --add." in result.output


@patch("memo_helpers.add_memo.subprocess.run")
@patch("memo.memo.notes_folders")
@patch("memo.memo.get_note")
def test_notes_add_noninteractive_stdin(
    mock_get_note, mock_notes_folders, mock_subprocess
):
    """Piped stdin content is used as Markdown when no --title/--body given."""
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_notes_folders.return_value = FAKE_FOLDERS
    mock_subprocess.return_value = MagicMock(returncode=0, stderr="", stdout="")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["notes", "--add", "--folder", "My Folder"],
        input="# Piped Note\n\nThis came from stdin.",
    )
    assert result.exit_code == 0
    assert "Note created in 'My Folder' folder." in result.output
