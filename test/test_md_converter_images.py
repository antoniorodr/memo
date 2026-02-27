"""Tests for image extraction and restoration in md_converter."""
import pytest
from memo_helpers.md_converter import extract_images, restore_images
import mistune
import html2text


def _roundtrip_md(html):
    """Helper: extract images, convert to MD, convert back, restore."""
    cleaned, image_map = extract_images(html)
    h = html2text.HTML2Text()
    h.images_to_alt = True
    h.body_width = 0
    md = h.handle(cleaned).strip()
    return md, image_map


def test_extract_single_image():
    html = (
        '<div>Text</div>\n'
        '<div><img style="max-width: 100%;" '
        'src="data:image/heic;base64,AAAA1234=="/><br></div>'
    )
    cleaned, image_map = extract_images(html)
    assert len(image_map) == 1
    assert "[MEMO_IMG_1]" in cleaned
    assert "data:image" not in cleaned


def test_extract_no_images():
    html = '<div><h1>Title</h1></div>\n<div>Just text</div>'
    cleaned, image_map = extract_images(html)
    assert len(image_map) == 0
    assert cleaned == html


def test_extract_multiple_images():
    html = (
        '<div><img src="data:image/png;base64,IMG1=="/><br></div>\n'
        '<div>Between</div>\n'
        '<div><img src="data:image/jpeg;base64,IMG2=="/><br></div>'
    )
    cleaned, image_map = extract_images(html)
    assert len(image_map) == 2
    assert "[MEMO_IMG_1]" in cleaned
    assert "[MEMO_IMG_2]" in cleaned


def test_extract_image_without_br():
    html = '<div><img src="data:image/png;base64,DATA=="/></div>'
    cleaned, image_map = extract_images(html)
    assert len(image_map) == 1


def test_roundtrip_preserves_image():
    html = (
        '<div>Keep this</div>\n'
        '<div><img src="data:image/png;base64,KEEPME=="/><br></div>'
    )
    md, image_map = _roundtrip_md(html)
    assert "[MEMO_IMG_1]" in md

    edited_html = mistune.markdown(md + "\n\nNew paragraph")
    restored = restore_images(edited_html, image_map)
    assert "KEEPME" in restored
    assert "New paragraph" in restored


def test_roundtrip_user_removes_placeholder():
    html = '<div><img src="data:image/png;base64,GONE=="/><br></div>'
    md, image_map = _roundtrip_md(html)

    edited_md = md.replace("[MEMO_IMG_1]", "").strip()
    edited_html = mistune.markdown(edited_md)
    restored = restore_images(edited_html, image_map)
    assert "GONE" not in restored


def test_restore_handles_p_wrapped_placeholder():
    image_map = {"[MEMO_IMG_1]": '<div><img src="data:image/png;base64,X=="/><br></div>'}
    html = "<p>Text</p>\n<p>[MEMO_IMG_1]</p>"
    restored = restore_images(html, image_map)
    assert '<div><img src="data:image/png;base64,X=="/><br></div>' in restored
    assert "<p>[MEMO_IMG_1]</p>" not in restored
