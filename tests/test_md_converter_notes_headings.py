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


def test_notes_heading_like_block_with_trailing_br_maps_to_heading():
    html = '<div><b><span style="font-size: 24px">2026 North Side</span></b><br></div>'

    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == "# 2026 North Side"
    assert original_html == html
    assert image_map == {}


def test_blank_heading_fragments_are_ignored_in_notes_body():
    html = (
        '<div><b><span style="font-size: 24px">Title</span></b></div>\n'
        '<div><b><span style="font-size: 24px"> </span></b><br></div>\n'
        "<div>Body</div>"
    )

    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == "# Title\n\nBody"
    assert original_html == html
    assert image_map == {}


def test_adjacent_same_level_heading_fragments_are_merged_sensibly():
    html = (
        '<div><b><span style="font-size: 24px">Air</span></b></div>\n'
        '<div><b><span style="font-size: 24px"> </span></b></div>\n'
        '<div><b><span style="font-size: 24px">conditioning</span></b><br></div>\n'
        "<div>Body</div>"
    )

    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == "# Air conditioning\n\nBody"
    assert original_html == html
    assert image_map == {}


def test_plain_bold_block_does_not_become_a_heading():
    html = "<div><b>Bold sentence with punctuation.</b></div>"

    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == "**Bold sentence with punctuation.**"
    assert original_html == html
    assert image_map == {}


def test_blank_heading_fragments_do_not_emit_stray_bold_spacers():
    html = (
        '<div><b><span style="font-size: 18px">Preferences</span></b></div>\n'
        '<div><b><span style="font-size: 18px"> </span></b></div>\n'
        "<div>Bring extra blankets</div>"
    )

    markdown, _, _ = _markdown_from_notes_html(html)

    assert markdown == "## Preferences\n\nBring extra blankets"
    assert "****" not in markdown


@pytest.mark.parametrize(
    ("html", "expected_markdown"),
    [
        (
            "<ul><li>First</li><li>Second</li></ul>",
            "* First\n* Second",
        ),
        (
            '<ul class="Apple-dash-list"><li>First</li><li>Second</li></ul>',
            "* First\n* Second",
        ),
        (
            "<ul><li>Parent<ul><li>Child</li></ul></li><li>Sibling</li></ul>",
            "* Parent\n  * Child\n* Sibling",
        ),
    ],
    ids=["regular-ul", "apple-dash-list", "nested-ul"],
)
def test_notes_unordered_lists_preserve_readable_markdown_structure(
    html, expected_markdown
):
    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == expected_markdown
    assert original_html == html
    assert image_map == {}


@pytest.mark.parametrize(
    ("html", "expected_markdown"),
    [
        ("<div>https://example.com/path?q=1</div>", "https://example.com/path?q=1"),
        (
            '<div><a href="https://example.com/path?q=1">Example</a></div>',
            "[Example](https://example.com/path?q=1)",
        ),
        (
            '<div><a href="https://example.com">https://example.com</a></div>',
            "<https://example.com>",
        ),
    ],
    ids=["plain-url-line", "anchor-link", "autolink"],
)
def test_notes_links_are_preserved_when_html_has_plain_urls_or_anchors(
    html, expected_markdown
):
    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == expected_markdown
    assert original_html == html
    assert image_map == {}


@pytest.mark.parametrize(
    ("html", "expected_markdown"),
    [
        ("<div><b>Label:</b> value</div>", "**Label:** value"),
        (
            "<ul><li><b>Label:</b> value</li><li>Next</li></ul>",
            "* **Label:** value\n* Next",
        ),
    ],
    ids=["paragraph-bold-label", "list-bold-label"],
)
def test_notes_bold_labels_are_preserved_in_paragraphs_and_lists(
    html, expected_markdown
):
    markdown, original_html, image_map = _markdown_from_notes_html(html)

    assert markdown == expected_markdown
    assert original_html == html
    assert image_map == {}
