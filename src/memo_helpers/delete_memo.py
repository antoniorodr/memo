import click
from memo_helpers.id_search_memo import id_search_memo


def delete_note(note_id):
    result = id_search_memo(note_id)

    if result.returncode == 0:
        click.echo("\nNote deleted successfully.")
    else:
        click.echo(f"Error: {result.stderr}")
