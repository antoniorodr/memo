from click.testing import CliRunner
from memo.memo import cli


def test_notes():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes"])
    assert result.exit_code == 0
    assert "All notes:" in result.output


def test_notes_folder_without_folder_name():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--folder"])
    assert result.exit_code == 2
    assert "Error: Option '--folder' requires an argument." in result.output


def test_notes_folder_not_exists():
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


def test_notes_edit():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--edit"], input="1")
    assert result.exit_code == 0
    assert "Enter the number of the note you want to edit:" in result.output


def test_notes_edit_indexerror():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--edit"], input="9999")
    assert result.exit_code == 1


def test_notes_delete():
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


def test_notes_flist():
    runner = CliRunner()
    result = runner.invoke(cli, ["notes", "--flist"])
    assert result.exit_code == 0
    assert "Folders and subfolders in Notes:" in result.output
