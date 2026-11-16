from click.testing import CliRunner

from memo.memo import notes, rem


def test_notes_help(app: CliRunner):
    result = app.invoke(notes, ["--help"])
    assert result.exit_code == 0


def test_reminders_help(app: CliRunner):
    result = app.invoke(rem, ["--help"])
    assert result.exit_code == 0
