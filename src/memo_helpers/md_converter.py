import re
import html2text


def extract_images(html):
    """Extract inline images from HTML, replacing them with placeholders.

    Returns (cleaned_html, image_map) where image_map maps placeholder
    strings like '[MEMO_IMG_1]' to the original HTML image blocks.
    """
    image_map = {}
    counter = 0

    def replace_img(match):
        nonlocal counter
        counter += 1
        placeholder = f"[MEMO_IMG_{counter}]"
        image_map[placeholder] = match.group(0)
        return f"<div>{placeholder}</div>"

    cleaned = re.sub(
        r"<div>\s*<img\s[^>]*src=\"data:[^\"]+\"[^>]*/>\s*(?:<br>)?\s*</div>",
        replace_img,
        html,
    )
    return cleaned, image_map


def restore_images(html, image_map):
    """Restore image placeholders back to original HTML image blocks."""
    for placeholder, original_img in image_map.items():
        html = html.replace(f"<p>{placeholder}</p>", original_img)
        html = html.replace(placeholder, original_img)
    return html


def md_converter(id_search_result):
    original_html = id_search_result.stdout.strip()

    cleaned_html, image_map = extract_images(original_html)

    text_maker = html2text.HTML2Text()
    text_maker.images_to_alt = True
    text_maker.body_width = 0
    original_md = text_maker.handle(cleaned_html).strip()
    return [original_md, original_html, image_map]
