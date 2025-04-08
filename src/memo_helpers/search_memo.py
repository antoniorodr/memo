import subprocess
import tempfile
import os
import html2text
from memo_helpers.get_memo import get_note
from memo_helpers.id_search_memo import id_search_memo


def fuzzy_notes():
    note_map, unique_notes = get_note()
    title_to_id = {title: note_id for (_, (note_id, title)) in note_map.items()}

    with tempfile.TemporaryDirectory() as tmpdirname:
        for note_title in unique_notes:
            note_id = title_to_id[note_title]
            result = id_search_memo(note_id)
            original_html = result.stdout.strip()

            text_maker = html2text.HTML2Text()
            text_maker.body_width = 0
            original_md = text_maker.handle(original_html).strip()

            file_path = os.path.join(tmpdirname, f"{note_title}.md")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(original_md)

        fzf_command = r"""
        fzf --style=full \
            --border --padding=1,2 \
            --border-label=' Your Notes ' --input-label=' Input ' --header-label=' File Type ' \
            --preview='bat --style=plain --color=always {}' \
            --preview-window=right:60%:wrap:cycle \
            --bind='ctrl-d:preview-down,ctrl-u:preview-up' \
            --bind='result:transform-list-label:
                if [[ -z $FZF_QUERY ]]; then
                echo " $FZF_MATCH_COUNT items "
                else
                echo " $FZF_MATCH_COUNT matches for [$FZF_QUERY] "
                fi' \
            --bind='focus:transform-preview-label:[[ -n {} ]] && printf " Previewing [%s] " {}' \
            --bind='focus:+transform-header:file --brief {} || echo "No file selected"' \
            --bind='ctrl-r:change-list-label( Reloading the list )+reload(sleep 2; git ls-files)' \
            --color='border:#aaaaaa,label:#cccccc' \
            --color='preview-border:#9999cc,preview-label:#ccccff' \
            --color='list-border:#669966,list-label:#99cc99' \
            --color='input-border:#996666,input-label:#ffcccc' \
            --color='header-border:#6699cc,header-label:#99ccff'
        """
        subprocess.run(fzf_command, shell=True, cwd=tmpdirname)
