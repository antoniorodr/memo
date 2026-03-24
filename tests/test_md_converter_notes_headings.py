from types import SimpleNamespace

import pytest

from memo_helpers.md_converter import md_converter


def _markdown_from_notes_html(html):
    """Run the existing Notes HTML -> Markdown path used by the CLI."""
    markdown, original_html, image_map = md_converter(SimpleNamespace(stdout=html))
    return markdown, original_html, image_map


# Apple Notes can export headings as styled div/b/span blocks instead of <h1>/<h2>/<h3>.
# The converter normalizes those Notes-specific blocks before generic html2text handling.
@pytest.mark.parametrize(
    ("html", "expected_markdown"),
    [
        (
            '<div><b><span style="font-size: 24px">Title</span></b></div>',
            "# Title",
        ),
        (
            '<div><b><span style="font-size: 18px">Section One</span></b></div>',
            "## Section One",
        ),
        ("<div><b>Subsection One</b></div>", "### Subsection One"),
    ],
    ids=["notes-h1-like", "notes-h2-like", "notes-h3-like"],
)
def test_notes_heading_like_html_maps_to_headings(html, expected_markdown):
    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == expected_markdown
    assert original_html == html
    assert image_map == {}


def test_notes_heading_like_blocks_map_to_headings_in_mixed_content():
    html = (
        '<div><b><span style="font-size: 24px">Title</span></b></div>\n'
        "<div>Body paragraph</div>\n"
        '<div><b><span style="font-size: 18px">Section One</span></b></div>\n'
        "<div>Section body</div>\n"
        "<div><b>Subsection One</b></div>\n"
        "<div>Subsection body</div>"
    )

    markdown, _, _ = _markdown_from_notes_html(html)

    assert markdown == (
        "# Title\n\n"
        "Body paragraph\n\n"
        "## Section One\n\n"
        "Section body\n\n"
        "### Subsection One\n\n"
        "Subsection body"
    )


def test_plain_bold_block_does_not_become_a_heading():
    html = "<div><b>Bold sentence with punctuation.</b></div>"

    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == "**Bold sentence with punctuation.**"
    assert original_html == html
    assert image_map == {}
