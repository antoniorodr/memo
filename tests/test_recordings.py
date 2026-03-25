from click.testing import CliRunner
from memo.memo import cli
from unittest.mock import patch, MagicMock

FAKE_RECORDING_ID = "x-coredata://fake-recording-123"
FAKE_RECORDING_TITLE = "Call Recordings - Call with John (March 24, 2026)"
FAKE_RECORDING_MAP = {1: (FAKE_RECORDING_ID, FAKE_RECORDING_TITLE)}
FAKE_RECORDINGS_LIST = [FAKE_RECORDING_TITLE]


@patch("memo.memo.get_recordings")
def test_recordings_list(mock_get_recordings):
    mock_get_recordings.return_value = (FAKE_RECORDING_MAP, FAKE_RECORDINGS_LIST)
    runner = CliRunner()
    result = runner.invoke(cli, ["recordings"])
    assert result.exit_code == 0
    assert "Your Call Recordings:" in result.output
    assert FAKE_RECORDING_TITLE in result.output


@patch("memo.memo.get_recordings")
def test_recordings_list_empty(mock_get_recordings):
    mock_get_recordings.return_value = ({}, [])
    runner = CliRunner()
    result = runner.invoke(cli, ["recordings"])
    assert result.exit_code == 0
    assert "No call recordings found" in result.output


@patch("memo.memo.get_recording_transcript")
@patch("memo.memo.get_recordings")
def test_recordings_view(mock_get_recordings, mock_transcript):
    mock_get_recordings.return_value = (FAKE_RECORDING_MAP, FAKE_RECORDINGS_LIST)
    mock_transcript.return_value = (
        "# Call with John\n\nHello, this is a test transcript.",
        "Call with John",
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["recordings", "--view", "1"])
    assert result.exit_code == 0
    assert "Call with John" in result.output
    mock_transcript.assert_called_once_with(FAKE_RECORDING_ID)


@patch("memo.memo.get_recordings")
def test_recordings_view_invalid(mock_get_recordings):
    mock_get_recordings.return_value = (FAKE_RECORDING_MAP, FAKE_RECORDINGS_LIST)
    runner = CliRunner()
    result = runner.invoke(cli, ["recordings", "--view", "999"])
    assert result.exit_code == 0
    assert "not found" in result.output


@patch("memo.memo.extract_recording_audio")
@patch("memo.memo.get_recordings")
def test_recordings_extract(mock_get_recordings, mock_extract):
    mock_get_recordings.return_value = (FAKE_RECORDING_MAP, FAKE_RECORDINGS_LIST)
    mock_extract.return_value = "/Users/test/Desktop/call.m4a"
    runner = CliRunner()
    result = runner.invoke(cli, ["recordings", "--extract", "1"])
    assert result.exit_code == 0
    assert "Audio extracted to" in result.output


@patch("memo.memo.extract_recording_audio")
@patch("memo.memo.get_recordings")
def test_recordings_extract_with_output(mock_get_recordings, mock_extract):
    mock_get_recordings.return_value = (FAKE_RECORDING_MAP, FAKE_RECORDINGS_LIST)
    mock_extract.return_value = "/tmp/calls/call.m4a"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["recordings", "--extract", "1", "--output", "/tmp/calls"]
    )
    assert result.exit_code == 0
    mock_extract.assert_called_once_with(FAKE_RECORDING_ID, "/tmp/calls")


@patch("memo.memo.get_recordings")
def test_recordings_extract_invalid(mock_get_recordings):
    mock_get_recordings.return_value = (FAKE_RECORDING_MAP, FAKE_RECORDINGS_LIST)
    runner = CliRunner()
    result = runner.invoke(cli, ["recordings", "--extract", "999"])
    assert result.exit_code == 0
    assert "not found" in result.output


# --- Unit tests for get_recordings module ---


@patch("memo_helpers.get_recordings.subprocess.run")
def test_get_recordings_parses_output(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="x-coredata://id1|Call Recordings - First Call (Jan 1)\nx-coredata://id2|Call Recordings - Second Call (Jan 2)\n",
        stderr="",
    )
    from memo_helpers.get_recordings import get_recordings

    recording_map, recordings_list = get_recordings()
    assert len(recording_map) == 2
    assert recording_map[1] == ("x-coredata://id1", "Call Recordings - First Call (Jan 1)")
    assert recording_map[2] == ("x-coredata://id2", "Call Recordings - Second Call (Jan 2)")
    assert len(recordings_list) == 2


@patch("memo_helpers.get_recordings.subprocess.run")
def test_get_recordings_empty(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    from memo_helpers.get_recordings import get_recordings

    recording_map, recordings_list = get_recordings()
    assert recording_map == {}
    assert recordings_list == []


@patch("memo_helpers.get_recordings.subprocess.run")
def test_get_recordings_error(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
    from memo_helpers.get_recordings import get_recordings

    recording_map, recordings_list = get_recordings()
    assert recording_map == {}
    assert recordings_list == []


# --- Unit tests for recording_utils ---


@patch("memo_helpers.recording_utils.subprocess.run")
def test_get_recording_attachments(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="1|call_recording.m4a|audio/x-m4a\n",
        stderr="",
    )
    from memo_helpers.recording_utils import get_recording_attachments

    attachments = get_recording_attachments("fake-id")
    assert len(attachments) == 1
    assert attachments[0]["name"] == "call_recording.m4a"
    assert attachments[0]["content_id"] == "audio/x-m4a"


@patch("memo_helpers.recording_utils.os.path.exists", return_value=True)
@patch("memo_helpers.recording_utils.subprocess.run")
def test_extract_recording_audio(mock_run, mock_exists):
    # First call returns the attachment name, second call does the save.
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="call_recording.m4a", stderr=""),
        MagicMock(returncode=0, stdout="", stderr=""),
    ]
    from memo_helpers.recording_utils import extract_recording_audio

    result = extract_recording_audio("fake-id", "/tmp/output")
    assert result is not None
    assert mock_run.call_count == 2
