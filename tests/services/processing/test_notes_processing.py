import pytest
from click.testing import CliRunner

from memo.memo import notes
from memo.services.notes_services.processing.notes_processing import NotesProcessing


def test_string_escaping():
    input_string = 'This is a "test" string with \\ backslashes.'
    expected_output = 'This is a \\"test\\" string with \\\\ backslashes.'
    assert NotesProcessing.applescript_escape(input_string) == expected_output


def test_add_flag_without_folder(app: CliRunner):
    result = app.invoke(notes, ["--add"])
    assert result.exit_code != 0


def test_add_flag_with_folder(app: CliRunner):
    # Uses `env` to set the EDITOR environment variable to a no-op command (`/usr/bin/true`) to avoid opening an editor during testing.
    result = app.invoke(
        notes, ["--add", "--folder", "Ideer"], env={"EDITOR": "/usr/bin/true"}
    )
    assert result.exit_code == 0


def test_flist_flag_without_other_flags(app: CliRunner):
    result = app.invoke(notes, ["--flist"])
    assert result.exit_code == 0


def test_flist_flag_with_other_flags(app: CliRunner):
    result = app.invoke(notes, ["--flist", "--add", "--folder", "Ideer"])
    assert result.exit_code != 0


@pytest.mark.parametrize(
    "flags",
    [
        pytest.param(["--edit", "--delete"], id="edit-delete"),
        pytest.param(["--edit", "--move"], id="edit-move"),
        pytest.param(["--edit", "--remove"], id="edit-remove"),
        pytest.param(["--edit", "--search"], id="edit-search"),
        pytest.param(["--edit", "--export"], id="edit-export"),
        pytest.param(["--edit", "--view"], id="edit-view"),
        pytest.param(["--delete", "--move"], id="delete-move"),
        pytest.param(["--delete", "--remove"], id="delete-remove"),
        pytest.param(["--delete", "--search"], id="delete-search"),
        pytest.param(["--delete", "--export"], id="delete-export"),
    ],
)
def test_modifier_flags_combination(app: CliRunner, flags: list[str]):
    result = app.invoke(notes, flags)
    assert result.exit_code != 0
