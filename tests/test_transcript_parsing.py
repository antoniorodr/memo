"""Regression tests for Apple Notes call recording transcript parsing.

Uses a real CRDT blob fixture to validate that _parse_crdt_transcript
produces correct transcripts with proper word ordering, speaker
assignment, and formatting.

The fixture file (tests/fixtures/recording2_crdt.bin) is gitignored
because it contains private call recording data.  Tests are skipped
when the fixture is absent (e.g. in CI).
"""

import os
import re
from unittest.mock import patch

import pytest

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "recording2_crdt.bin"
)

# Skip the entire module if the fixture is missing (CI environments).
pytestmark = pytest.mark.skipif(
    not os.path.exists(FIXTURE_PATH),
    reason="CRDT fixture not available (gitignored, local-only)",
)


@pytest.fixture
def crdt_blob():
    with open(FIXTURE_PATH, "rb") as f:
        return f.read()


@pytest.fixture
def transcript(crdt_blob):
    """Parse the CRDT blob with contact lookup disabled."""
    with patch(
        "memo_helpers.recording_utils._lookup_contact_name",
        return_value=None,
    ):
        from memo_helpers.recording_utils import _parse_crdt_transcript

        return _parse_crdt_transcript(crdt_blob)


class TestCRDTTranscriptParsing:
    def test_returns_transcript(self, transcript):
        assert transcript is not None
        assert len(transcript) > 100

    def test_has_both_speakers(self, transcript):
        """Both You and Participant labels should be present."""
        assert "**Participant**:" in transcript
        assert "**You**:" in transcript

    def test_participant_speaks_first(self, transcript):
        """Participant should speak the opening line."""
        first_line = transcript.strip().split("\n")[0]
        assert first_line.startswith("**Participant**:")

    def test_speaker_turns_alternate(self, transcript):
        """Speaker labels should alternate (no two consecutive same-speaker)."""
        lines = [
            l.strip() for l in transcript.split("\n") if l.strip()
        ]
        prev = None
        for line in lines:
            match = re.match(r"\*\*(.+?)\*\*:", line)
            assert match, f"Line missing speaker label: {line[:60]}"
            current = match.group(1)
            assert current != prev, (
                f"Consecutive same-speaker: {current}"
            )
            prev = current

    def test_you_has_short_responses(self, transcript):
        """'You' speaker should have characteristically short responses."""
        lines = [
            l.strip() for l in transcript.split("\n") if l.strip()
        ]
        you_lines = [l for l in lines if l.startswith("**You**:")]
        assert len(you_lines) > 0
        # At least half of You's responses should be short (< 50 chars).
        short = sum(
            1 for l in you_lines if len(l) - len("**You**: ") < 50
        )
        assert short >= len(you_lines) // 2

    def test_no_binary_garbage(self, transcript):
        """No binary noise, float artifacts, or CRDT metadata."""
        assert "com.apple." not in transcript
        assert "CRDT" not in transcript
        assert "\ufffc" not in transcript
        # No standalone float artifacts (e.g. "3.14159265").
        floats = re.findall(r"\b\d+\.\d{4,}\b", transcript)
        assert not floats, f"Float artifacts found: {floats}"

    def test_minimum_turn_count(self, transcript):
        """Should have a reasonable number of speaker turns."""
        lines = [
            l.strip() for l in transcript.split("\n") if l.strip()
        ]
        assert len(lines) >= 10, (
            f"Only {len(lines)} turns — expected at least 10"
        )

    def test_words_form_sentences(self, transcript):
        """Merged fragments should form multi-word sentences, not
        single-word garbage."""
        lines = [
            l.strip() for l in transcript.split("\n") if l.strip()
        ]
        multi_word = sum(
            1 for l in lines if len(l.split()) > 3
        )
        # At least a third of lines should be multi-word.
        assert multi_word >= len(lines) // 3


class TestCRDTTranscriptWithContactNames:
    """Test that contact names replace default labels when available."""

    def test_contact_names_replace_labels(self, crdt_blob):
        names = {}

        def mock_lookup(phone):
            if phone and phone not in names:
                names[phone] = f"Contact_{len(names) + 1}"
            return names.get(phone)

        with patch(
            "memo_helpers.recording_utils._lookup_contact_name",
            side_effect=mock_lookup,
        ):
            from memo_helpers.recording_utils import (
                _parse_crdt_transcript,
            )

            transcript = _parse_crdt_transcript(crdt_blob)

        assert transcript is not None
        # Default labels should NOT appear when contacts resolve.
        assert "**You**:" not in transcript
        assert "**Participant**:" not in transcript
        # Contact names should be used instead.
        assert "**Contact_" in transcript
