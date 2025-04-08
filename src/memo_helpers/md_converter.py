import html2text


def md_converter(result):
    original_html = result.stdout.strip()

    text_maker = html2text.HTML2Text()
    text_maker.body_width = 0
    original_md = text_maker.handle(original_html).strip()
    return [original_md, original_html]
