import html2text


def md_converter(id_search_result):
    original_html = id_search_result.stdout.strip()

    text_maker = html2text.HTML2Text()
    text_maker.images_to_alt = True
    text_maker.body_width = 0
    original_md = text_maker.handle(original_html).strip()
    return [original_md, original_html]
