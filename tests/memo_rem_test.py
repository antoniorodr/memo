import datetime
from click.testing import CliRunner
from memo.memo import cli
from unittest.mock import patch, MagicMock

FAKE_REMINDER_ID = "x-apple-reminder://fake-id-123"
FAKE_REMINDER_TITLE = "Test Reminder"
FAKE_DUE = datetime.datetime(2099, 12, 31, 12, 0, 0)
FAKE_REMINDERS_MAP = {1: (FAKE_REMINDER_ID, FAKE_REMINDER_TITLE, FAKE_DUE)}
FAKE_REMINDERS_LIST = [
    f"{FAKE_REMINDER_TITLE} | {FAKE_DUE.strftime('%Y-%m-%d %H:%M:%S')}"
]


@patch("memo.memo.get_reminder")
def test_rem(mock_get_reminder):
    mock_get_reminder.return_value = [FAKE_REMINDERS_MAP, FAKE_REMINDERS_LIST]
    runner = CliRunner()
    result = runner.invoke(cli, ["rem"])
    assert result.exit_code == 0
    assert "Your Reminders:" in result.output


@patch("memo_helpers.delete_memo.subprocess.run")
@patch("memo.memo.get_reminder")
def test_rem_complete(mock_get_reminder, mock_subprocess):
    mock_get_reminder.return_value = [FAKE_REMINDERS_MAP, FAKE_REMINDERS_LIST]
    mock_subprocess.return_value = MagicMock(returncode=0, stderr="", stdout="")
    runner = CliRunner()
    result = runner.invoke(cli, ["rem", "--complete"], input="1")
    assert result.exit_code == 0
    assert "Reminder marked successfully as completed." in result.output


@patch("memo_helpers.delete_memo.subprocess.run")
@patch("memo.memo.get_reminder")
def test_rem_delete(mock_get_reminder, mock_subprocess):
    mock_get_reminder.return_value = [FAKE_REMINDERS_MAP, FAKE_REMINDERS_LIST]
    mock_subprocess.return_value = MagicMock(returncode=0, stderr="", stdout="")
    runner = CliRunner()
    result = runner.invoke(cli, ["rem", "--delete"], input="1")
    assert result.exit_code == 0
    assert "Reminder deleted successfully." in result.output
