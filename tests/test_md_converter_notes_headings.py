from types import SimpleNamespace

import pytest

from memo_helpers.md_converter import md_converter


def _markdown_from_notes_html(html):
    """Run the existing Notes HTML -> Markdown path used by the CLI."""
    markdown, original_html, image_map = md_converter(SimpleNamespace(stdout=html))
    return markdown, original_html, image_map


# Characterization tests for a suspected heading-collapse bug.
# Apple Notes can export headings as styled div/b/span blocks instead of <h1>/<h2>/<h3>.
# The current converter path appears to collapse those blocks to bold Markdown rather than
# heading syntax. These assertions document the current behavior without endorsing it.
@pytest.mark.parametrize(
    ("html", "expected_markdown"),
    [
        (
            '<div><b><span style="font-size: 24px">Title</span></b></div>',
            "**Title**",
        ),
        (
            '<div><b><span style="font-size: 18px">Section One</span></b></div>',
            "**Section One**",
        ),
        ("<div><b>Subsection One</b></div>", "**Subsection One**"),
    ],
    ids=["notes-h1-like", "notes-h2-like", "notes-h3-like"],
)
def test_notes_heading_like_html_currently_collapses_to_bold(
    html, expected_markdown
):
    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == expected_markdown
    assert original_html == html
    assert image_map == {}
    assert "#" not in markdown


def test_notes_heading_like_blocks_stay_bold_in_mixed_content():
    html = (
        '<div><b><span style="font-size: 24px">Title</span></b></div>\n'
        "<div>Body paragraph</div>\n"
        '<div><b><span style="font-size: 18px">Section One</span></b></div>\n'
        "<div><b>Subsection One</b></div>"
    )

    markdown, _, _ = _markdown_from_notes_html(html)

    assert "**Title**" in markdown
    assert "Body paragraph" in markdown
    assert "**Section One**" in markdown
    assert "**Subsection One**" in markdown
    assert "# Title" not in markdown
    assert "## Section One" not in markdown
    assert "### Subsection One" not in markdown
