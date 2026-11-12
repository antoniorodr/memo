import re

import click
import html2text


class NotesProcessing:
    """Class to handle processing of notes."""

    @staticmethod
    def applescript_escape(value: str) -> str:
        """Escape a string for safe interpolation into an AppleScript string literal."""
        return value.replace("\\", "\\\\").replace('"', '\\"')

    @staticmethod
    def selection_notes_validation(
        folder, edit, delete, move, add, flist, search, remove, export, view
    ):
        used_flags = {
            "folder": bool(folder),
            "edit": edit,
            "delete": delete,
            "move": move,
            "add": add,
            "flist": flist,
            "search": search,
            "remove": remove,
            "export": export,
            "view": view is not None,
        }

        if add and not folder:
            raise click.UsageError(
                "--add must be used indicating a folder to create the note to."
            )

        if flist and sum(used_flags.values()) > 1:
            raise click.UsageError(
                "--flist must be used alone. It cannot be combined with other flags or --folder."
            )

        modifier_flags = [
            "edit",
            "delete",
            "move",
            "remove",
            "search",
            "export",
            "view",
        ]
        used_modifiers = [f for f in modifier_flags if used_flags[f]]
        if len(used_modifiers) > 1:
            raise click.UsageError(
                "Only one of --edit, --delete, --move, --remove, --export, --view, or --search can be used at a time."
            )

    @staticmethod
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

    @staticmethod
    def restore_images(html, image_map):
        """Restore image placeholders back to original HTML image blocks."""
        for placeholder, original_img in image_map.items():
            html = html.replace(f"<p>{placeholder}</p>", original_img)
            html = html.replace(placeholder, original_img)
        return html

    @staticmethod
    def md_converter(id_search_result):
        original_html = id_search_result.stdout.strip()

        cleaned_html, image_map = NotesProcessing.extract_images(original_html)

        text_maker = html2text.HTML2Text()
        text_maker.images_to_alt = True
        text_maker.body_width = 0
        original_md = text_maker.handle(cleaned_html).strip()
        return [original_md, original_html, image_map]

    @staticmethod
    def _decode_image_to_tempfile(img_html):
        """Extract base64 data from an <img> HTML block and write to a temp file."""
        match = re.search(r'src="data:image/(\w+);base64,([^"]+)"', img_html)
        if not match:
            return None
        ext = match.group(1)
        data = base64.b64decode(match.group(2))
        fd, path = tempfile.mkstemp(suffix=f".{ext}")
        os.write(fd, data)
        os.close(fd)
        return path

    @staticmethod
    def _reattach_images(note_id, surviving_images):
        """Delete orphaned attachments and re-add surviving images."""

        escaped_note_id = NotesProcessing.applescript_escape(note_id)
        script = f"""tell application "Notes"
            set n to first note whose id is "{escaped_note_id}"
            repeat while (count of attachments of n) > 0
                delete first attachment of n
            end repeat
        end tell"""

        subprocess.run(
            [
                "osascript",
                "-e",
                script,
            ],
            capture_output=True,
            text=True,
        )

        expected = 0
        for key in sorted(surviving_images.keys()):
            filepath = NotesProcessing._decode_image_to_tempfile(surviving_images[key])
            if not filepath:
                continue
            expected += 1

            escaped_filepath = NotesProcessing.applescript_escape(filepath)

            script = f"""tell application "Notes"
                set n to first note whose id is "{escaped_note_id}"
                make new attachment at end of attachments of n with data POSIX file
                "{escaped_filepath}"
                if (count of attachments of n) > {expected} then
                    delete last attachment of n
                end if
            end tell"""

            subprocess.run(
                [
                    "osascript",
                    "-e",
                    script,
                ],
                capture_output=True,
                text=True,
            )
            os.unlink(filepath)

    @staticmethod
    def edit_note(note_id):
        result = NotesOperations.id_search_memo(note_id)
        original_md, original_html, image_map = NotesProcessing.md_converter(result)

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
            temp_file.write(original_md.encode("utf-8"))
            temp_file_path = temp_file.name

        if image_map:
            click.secho(
                f"\nℹ️ This note contains {len(image_map)} image(s), shown as [MEMO_IMG_N] placeholders.",
                fg="cyan",
            )
            click.secho(
                "Keep placeholders to preserve images, remove them to delete images.",
                fg="cyan",
            )

        editor = os.getenv("EDITOR", "vim")
        subprocess.run([editor, temp_file_path])

        with open(temp_file_path, "r", encoding="utf-8") as file:
            edited_md = file.read().strip()

        if edited_md == original_md:
            click.secho("\nNo changes made.", fg="yellow")
            return

        # Determine which images the user kept (placeholder still present)
        surviving_images = {}
        if image_map:
            for key, img_html in image_map.items():
                if key in edited_md:
                    surviving_images[key] = img_html
            # Remove placeholders before converting to HTML
            for key in image_map:
                edited_md = edited_md.replace(key, "")

        edited_html = mistune.markdown(edited_md)

        escaped_note_id = NotesProcessing.applescript_escape(note_id)
        escaped_edited_html = NotesProcessing.applescript_escape(edited_html)

        update_script = f"""
            tell application "Notes"
                set selectedNote to first note whose id is "{escaped_note_id}"
                set body of selectedNote to "{escaped_edited_html}"
            end tell
            """

        process = subprocess.run(
            ["osascript", "-e", update_script], capture_output=True, text=True
        )
        if process.returncode != 0:
            click.secho("\nError: Could not update note.\n", fg="red")
            click.secho(process.stderr, fg="red")
            return

        # Re-add images as attachments (set body strips inline base64 images)
        if surviving_images:
            NotesProcessing._reattach_images(note_id, surviving_images)
            click.secho(
                f"\nNote updated. {len(surviving_images)} image(s) preserved.",
                fg="green",
            )
        else:
            click.secho("\nNote updated.", fg="green")
