# memo_helpers/checklist.py
import re
from html.parser import HTMLParser
import mistune


def apple_checklist_to_markdown(html: str) -> str:
    """
    Convert Apple Notes checklist HTML to GFM task list lines.
    If no checklist is found, return the original HTML unchanged.
    """
    class ChecklistParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.lines = []
            self.in_checklist = False
            self.in_li = False
            self.current_li_text = []
            self.checked = False
            self.found_checklist = False

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            if tag == 'ul' and attrs_dict.get('class') == 'checklist':
                self.in_checklist = True
                self.found_checklist = True
            elif self.in_checklist and tag == 'li':
                self.in_li = True
                self.current_li_text = []
                self.checked = attrs_dict.get('data-checked', 'false').lower() == 'true'
            else:
                if not self.in_checklist:
                    # Preserve exact tag with attributes
                    attrs_str = ''.join(f' {k}="{v}"' for k, v in attrs)
                    self.lines.append(f'<{tag}{attrs_str}>')

        def handle_endtag(self, tag):
            if self.in_checklist and tag == 'li' and self.in_li:
                text = ''.join(self.current_li_text).strip()
                checkbox = '[x]' if self.checked else '[ ]'
                self.lines.append(f'- {checkbox} {text}')
                self.in_li = False
            elif self.in_checklist and tag == 'ul':
                self.in_checklist = False
            elif not self.in_checklist:
                self.lines.append(f'</{tag}>')

        def handle_data(self, data):
            if self.in_li:
                self.current_li_text.append(data)
            elif not self.in_checklist:
                self.lines.append(data)

        def handle_entityref(self, name):
            if not self.in_checklist:
                self.lines.append(f'&{name};')

        def handle_charref(self, name):
            if not self.in_checklist:
                self.lines.append(f'&#{name};')

    parser = ChecklistParser()
    parser.feed(html)
    if not parser.found_checklist:
        return html  # return unchanged
    output = '\n'.join(parser.lines).strip()
    return output


def markdown_tasklist_to_apple_html(md: str) -> str:
    """
    Convert GFM task list lines to Apple Notes checklist HTML.
    All other Markdown is converted using mistune.
    """
    lines = md.splitlines()
    groups = []
    i = 0
    while i < len(lines):
        line = lines[i]
        task_match = re.match(r'^(\s*)- \[([ x])\] (.*)$', line)
        if task_match:
            indent, checked_char, text = task_match.groups()
            group_start = i
            group_items = []
            while i < len(lines):
                line2 = lines[i]
                match2 = re.match(r'^(\s*)- \[([ x])\] (.*)$', line2)
                if match2 and match2.group(1) == indent:
                    group_items.append((match2.group(2) == 'x', match2.group(3)))
                    i += 1
                else:
                    break
            groups.append((indent, group_items, group_start, i))
        else:
            i += 1

    if not groups:
        return mistune.markdown(md)

    # Use placeholders that mistune will not interpret as Markdown (double curly braces)
    placeholder_map = {}
    new_lines = lines[:]
    for idx, (indent, items, start, end) in enumerate(groups):
        placeholder = f'{{{{CHECKLIST_PLACEHOLDER_{idx}}}}}'
        placeholder_map[placeholder] = items
        new_lines[start:end] = [placeholder]

    md_with_placeholders = '\n'.join(new_lines)
    html_with_placeholders = mistune.markdown(md_with_placeholders)

    for placeholder, items in placeholder_map.items():
        checklist_html = '<ul class="checklist">\n'
        for checked, text in items:
            checked_str = 'true' if checked else 'false'
            checklist_html += f'<li data-checked="{checked_str}">{text}</li>\n'
        checklist_html += '</ul>'
        # Mistune wraps the placeholder in <p> tags
        html_with_placeholders = html_with_placeholders.replace(f'<p>{placeholder}</p>', checklist_html)
        # Also handle if no <p> wrap
        html_with_placeholders = html_with_placeholders.replace(placeholder, checklist_html)

    return html_with_placeholders