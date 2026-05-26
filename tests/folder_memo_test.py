from memo_helpers.folder_memo import (
    folder_paths_from_tree,
    note_belongs_to_folder,
    normalize_folder_path,
    resolve_folder_path,
)

DUPLICATE_LEAF_FOLDERS = "Alpha\n  Reports\nBeta\n  Reports"


def test_normalize_folder_path_strips_and_joins_segments():
    assert normalize_folder_path(" Alpha / Reports ") == "Alpha/Reports"


def test_folder_paths_from_tree_includes_full_nested_paths():
    paths = folder_paths_from_tree(DUPLICATE_LEAF_FOLDERS)
    assert paths == ["Alpha", "Alpha/Reports", "Beta", "Beta/Reports"]


def test_resolve_folder_path_matches_full_nested_path():
    paths = folder_paths_from_tree(DUPLICATE_LEAF_FOLDERS)
    assert resolve_folder_path("Alpha/Reports", paths) == "Alpha/Reports"


def test_resolve_folder_path_rejects_ambiguous_leaf_name():
    paths = folder_paths_from_tree(DUPLICATE_LEAF_FOLDERS)
    assert resolve_folder_path("Reports", paths) == ""


def test_note_belongs_to_folder_matches_full_path_prefix():
    assert note_belongs_to_folder("Alpha/Reports - Summary note", "Alpha/Reports")


def test_note_belongs_to_folder_rejects_other_branch_with_same_leaf():
    assert not note_belongs_to_folder("Beta/Reports - Summary note", "Alpha/Reports")


def test_note_belongs_to_folder_rejects_leaf_only_title_for_nested_filter():
    assert not note_belongs_to_folder("Reports - Summary note", "Alpha/Reports")


def test_note_belongs_to_folder_allows_leaf_fallback_for_single_segment_filter():
    assert note_belongs_to_folder("Child - Summary note", "Child")
