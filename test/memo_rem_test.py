from click.testing import CliRunner
from memo.memo import cli


def test_rem():
    runner = CliRunner()
    result = runner.invoke(cli, ["rem"])
    assert result.exit_code == 0
    assert "Your Reminders:" in result.output


def test_rem_complete():
    runner = CliRunner()
    result = runner.invoke(cli, ["rem", "--complete"], input="1")
    assert result.exit_code == 0
    assert "Reminder marked successfully as completed." in result.output


def test_rem_delete():
    runner = CliRunner()
    result = runner.invoke(cli, ["rem", "--delete"], input="1")
    assert result.exit_code == 0
    assert "Reminder deleted successfully." in result.output
