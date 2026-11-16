from click.testing import CliRunner

from memo.memo import notes


def test_create_note(app: CliRunner):
    # Uses `env` to set the EDITOR environment variable to a no-op command (`/usr/bin/true`) to avoid opening an editor during testing.
    result = app.invoke(
        notes, ["--add", "--folder", "Ideer"], env={"EDITOR": "/usr/bin/true"}
    )
    assert result.exit_code == 0
