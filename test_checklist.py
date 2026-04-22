# test_checklist.py
import pytest
from memo_helpers.checklist import (
    apple_checklist_to_markdown,
    markdown_tasklist_to_apple_html,
)


class TestAppleChecklistToMarkdown:
    def test_single_checked_item(self):
        html = '<ul class="checklist"><li data-checked="true">Buy milk</li></ul>'
        result = apple_checklist_to_markdown(html)
        assert "- [x] Buy milk" in result
        assert "<ul" not in result  # should be plain text lines

    def test_single_unchecked_item(self):
        html = '<ul class="checklist"><li data-checked="false">Buy eggs</li></ul>'
        result = apple_checklist_to_markdown(html)
        assert "- [ ] Buy eggs" in result

    def test_multiple_items(self):
        html = (
            '<ul class="checklist">'
            '<li data-checked="true">Task 1</li>'
            '<li data-checked="false">Task 2</li>'
            '<li data-checked="true">Task 3</li>'
            '</ul>'
        )
        result = apple_checklist_to_markdown(html)
        lines = [line.strip() for line in result.splitlines() if line.strip()]
        expected = ["- [x] Task 1", "- [ ] Task 2", "- [x] Task 3"]
        assert lines == expected

    def test_mixed_with_regular_html(self):
        html = (
            "<div>Regular paragraph</div>"
            '<ul class="checklist"><li data-checked="true">Check me</li></ul>'
            "<p>Another paragraph</p>"
        )
        result = apple_checklist_to_markdown(html)
        assert "Regular paragraph" in result
        assert "- [x] Check me" in result
        assert "Another paragraph" in result

    def test_no_checklist(self):
        html = "<ul><li>Plain bullet</li></ul>"
        result = apple_checklist_to_markdown(html)
        # Should remain unchanged (not convert to task list)
        assert "<ul><li>Plain bullet</li></ul>" in result

    def test_empty_checklist(self):
        html = '<ul class="checklist"></ul>'
        result = apple_checklist_to_markdown(html)
        assert result.strip() == "" or result == "\n"

    def test_li_with_extra_whitespace(self):
        html = '<ul class="checklist"><li data-checked="true">   Spaced text   </li></ul>'
        result = apple_checklist_to_markdown(html)
        assert "- [x] Spaced text" in result  # stripped


class TestMarkdownTasklistToAppleHtml:
    def test_single_checked(self):
        md = "- [x] Buy milk"
        html = markdown_tasklist_to_apple_html(md)
        assert '<ul class="checklist">' in html
        assert '<li data-checked="true">Buy milk</li>' in html
        assert '</ul>' in html

    def test_single_unchecked(self):
        md = "- [ ] Buy eggs"
        html = markdown_tasklist_to_apple_html(md)
        assert '<li data-checked="false">Buy eggs</li>' in html

    def test_multiple_items(self):
        md = "- [x] Task 1\n- [ ] Task 2\n- [x] Task 3"
        html = markdown_tasklist_to_apple_html(md)
        assert '<ul class="checklist">' in html
        assert '<li data-checked="true">Task 1</li>' in html
        assert '<li data-checked="false">Task 2</li>' in html
        assert '<li data-checked="true">Task 3</li>' in html

    def test_mixed_with_other_markdown(self):
        md = "Normal paragraph\n\n- [x] Checklist item\n\nAnother paragraph"
        html = markdown_tasklist_to_apple_html(md)
        # Mistune should convert normal markdown to HTML
        assert "<p>Normal paragraph</p>" in html
        assert '<ul class="checklist">' in html
        assert '<li data-checked="true">Checklist item</li>' in html
        assert "<p>Another paragraph</p>" in html

    def test_no_tasklist(self):
        md = "- Plain bullet\n* Another bullet"
        html = markdown_tasklist_to_apple_html(md)
        # Should be normal Markdown conversion (task list plugin won't trigger)
        # Mistune produces <ul><li> for plain bullets
        assert "<ul>" in html or "<li>" in html
        assert "checklist" not in html  # no checklist class

    def test_empty_tasklist_not_present(self):
        md = ""
        html = markdown_tasklist_to_apple_html(md)
        assert html == "" or "<p></p>" in html  # empty output

    def test_indented_tasklist(self):
        md = "  - [x] Indented item"
        html = markdown_tasklist_to_apple_html(md)
        # Should still become a checklist (indent ignored for grouping)
        assert '<ul class="checklist">' in html
        assert '<li data-checked="true">Indented item</li>' in html


class TestRoundTrip:
    def test_roundtrip_preserves_state(self):
        original_html = (
            '<ul class="checklist">'
            '<li data-checked="true">Item 1</li>'
            '<li data-checked="false">Item 2</li>'
            '</ul>'
        )
        # HTML -> Markdown
        md = apple_checklist_to_markdown(original_html)
        # Markdown -> HTML
        roundtrip_html = markdown_tasklist_to_apple_html(md)
        # Compare key attributes (ignore whitespace differences)
        assert 'data-checked="true"' in roundtrip_html
        assert 'data-checked="false"' in roundtrip_html
        assert "Item 1" in roundtrip_html
        assert "Item 2" in roundtrip_html
        assert "checklist" in roundtrip_html

    def test_roundtrip_with_surrounding_text(self):
        original_html = (
            "<div>Top text</div>"
            '<ul class="checklist"><li data-checked="true">Todo</li></ul>'
            "<div>Bottom text</div>"
        )
        md = apple_checklist_to_markdown(original_html)
        roundtrip_html = markdown_tasklist_to_apple_html(md)
        assert "Top text" in roundtrip_html
        assert "Bottom text" in roundtrip_html
        assert "Todo" in roundtrip_html
        assert "checklist" in roundtrip_html


class TestRegressionPlainBulletLists:
    """Ensure standard bullet lists are never turned into checklists."""

    def test_plain_ul_unchanged_by_apple_converter(self):
        html = "<ul><li>Plain bullet</li></ul>"
        result = apple_checklist_to_markdown(html)
        # Should output the same HTML (or markdown bullet, but not task list)
        # Since our function only transforms <ul class="checklist">, plain <ul> passes through.
        assert "checklist" not in result
        assert "<li>Plain bullet</li>" in result or "- Plain bullet" in result

    def test_plain_markdown_bullet_not_converted_to_checklist_html(self):
        md = "- Plain bullet\n- Another bullet"
        html = markdown_tasklist_to_apple_html(md)
        assert "checklist" not in html
        assert "<ul>" in html
        assert "<li>Plain bullet</li>" in html