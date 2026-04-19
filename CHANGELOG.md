# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.3] - 2026-04-19

### Added
- Add stale workflow by @antoniorodr

### Changed
- Merge branch 'chore/update-dependencies'
- Update dependencies to the last version
- Create git-cliff config
- Update release workflow to use git-cliff
- Delete logo from readme by @antoniorodr
- Delete back to top from readme by @antoniorodr
- Update logo size by @antoniorodr
- Update logo size by @antoniorodr
- Update readme by @antoniorodr
- Update license in pyproject by @antoniorodr
- Update tests workflow by @antoniorodr
- Update readme by @antoniorodr
- Update license by @antoniorodr
- Update workflows by @antoniorodr
- Update release workflow by @antoniorodr
- Merge pull request #37 from antoniorodr/dependabot/uv/pygments-2.20.0 by @antoniorodr in [#37](https://github.com/antoniorodr/memo/pull/37)
- Bump pygments from 2.19.2 to 2.20.0 by @dependabot[bot]

### Removed
- Delete white spaces

### New Contributors
* @dependabot[bot] made their first contribution

## [0.5.2] - 2026-03-24

### Added
- Add cycle detection to _render_tree to prevent RecursionError by @MehrabMirzaei
- Add the necessary files and modifications to run the no-autopilot action by @antoniorodr

### Changed
- Release v0.5.2 version by @antoniorodr
- Merge branch 'fix/render-tree-cycle-detection' by @antoniorodr in [#32](https://github.com/antoniorodr/memo/pull/32)
- Delete notify job from PR workflow by @antoniorodr
- Delete old ci workflow by @antoniorodr
- Update logo by @antoniorodr
- Update pyproject with dev group by @antoniorodr

### New Contributors
* @MehrabMirzaei made their first contribution

## [0.5.1] - 2026-03-07

### Added
- Add use of clear_cache and new flag by @antoniorodr
- Add new workflows for testing and release by @antoniorodr

### Changed
- Update changelog by @antoniorodr
- Update changelog and pyproject by @antoniorodr
- Move the test from test/ to tests/ by @antoniorodr
- Modify get_note to use the caching by @antoniorodr
- Create cache_memo for caching of notes by @antoniorodr
- Change from mkdocs material to zensical by @antoniorodr

## [0.5.0] - 2026-03-02

### Added
- Add a warning before selecting the note to edit by @antoniorodr
- Add avoiding check host to mirroring workflow by @antoniorodr
- Add debug mode to the mirroring workflow by @antoniorodr
- Add Codeberg mirroring yml by @antoniorodr

### Changed
- Update changelog and pyproject for the new version by @antoniorodr
- Merge branch 'feat/preserve-images-on-edit' by @antoniorodr
- Update readme with the AppleScript limitation warning about images by @antoniorodr
- Fix formatting by @antoniorodr
- Update mkdocs documentation by @antoniorodr
- Preserve inline images when editing notes by @Starefossen in [#24](https://github.com/antoniorodr/memo/pull/24)
- Undo LICENSE change. Back to MIT. by @antoniorodr
- Update mirroring workflow by @antoniorodr
- Delete debug mode from workflow by @antoniorodr
- Update mirroring workflow to use SSH by @antoniorodr
- Merge pull request #22 from antoniorodr/feat/mirroring by @antoniorodr in [#22](https://github.com/antoniorodr/memo/pull/22)
- Update mirroring yml by @antoniorodr
- Delete gitlab mirroring yml by @antoniorodr
- Change LICENSE to Apache 2.0 non AI by @antoniorodr

### New Contributors
* @Starefossen made their first contribution in [#24](https://github.com/antoniorodr/memo/pull/24)

## [0.4.0] - 2026-02-18

### Added
- Add --view/-v flag to read note content
- Add .editorconfig file to the project by @antoniorodr
- Add new info in CONTRIBUTING.md file by @antoniorodr

### Changed
- Merge pull request #21 from antoniorodr/feat/view-flag by @antoniorodr in [#21](https://github.com/antoniorodr/memo/pull/21)
- Update changelog by @antoniorodr
- Merge branch 'add-show-notes-content-feature' by @antoniorodr
- Update Changelog and pyproject by @antoniorodr
- Edit the edit test with mocking by @antoniorodr
- Delete an extra character by @antoniorodr
- Merge pull request #17 from antoniorodr/feat/update-readme by @antoniorodr in [#17](https://github.com/antoniorodr/memo/pull/17)
- Update Readme with OpenClaw mention by @antoniorodr
- Merge pull request #16 from antoniorodr/feat/editorconfig by @antoniorodr in [#16](https://github.com/antoniorodr/memo/pull/16)

### New Contributors
* @ made their first contribution

## [0.3.6] - 2026-02-11

### Changed
- Merge pull request #15 from antoniorodr/fix/hardcoded-title by @antoniorodr in [#15](https://github.com/antoniorodr/memo/pull/15)
- Fixed hardcoded note title when creating a new one by @antoniorodr

## [0.3.5] - 2026-02-10

### Changed
- Merge pull request #13 from antoniorodr/release/v0.3.5 by @antoniorodr in [#13](https://github.com/antoniorodr/memo/pull/13)
- Update changelog and pyproject for the new release by @antoniorodr
- Merge pull request #10 from sajal2692/fix/folder-listing-applescript-context by @antoniorodr in [#10](https://github.com/antoniorodr/memo/pull/10)
- Fix folder listing crash caused by AppleScript context loss by @sajal2692
- Merge pull request #12 from antoniorodr/export-to-custom-flag by @antoniorodr in [#12](https://github.com/antoniorodr/memo/pull/12)

### New Contributors
* @sajal2692 made their first contribution

## [0.3.4] - 2026-02-10

### Changed
- Update pyproject and mkdocs by @antoniorodr
- Update Changelog by @antoniorodr
- Update the export flag to add the possibility to export the notes to a custom folder by @antoniorodr

## [0.3.3] - 2026-01-22

### Changed
- Fix a bug that caosed memo to crash when searching notes by @antoniorodr
- Update urllib3 dependency by @antoniorodr
- Update changelog and pyproject by @antoniorodr

## [0.3.2] - 2026-01-16

### Added
- Add sponsorship badge and update readme by @antoniorodr
- Add gitlab sync workflow by @antoniorodr
- Add export to html and convert to md by @antoniorodr
- Add translations for Recently Deleted by @antoniorodr

### Changed
- Fix bug where memo crashed when the note title contained "|" by @antoniorodr
- Update readme with gif by @antoniorodr
- Release v0.3.1 by @antoniorodr
- Update readme by @antoniorodr

## [0.2.2] - 2025-04-14

### Added
- Add support to edit reminders by @antoniorodr

## [0.2.1] - 2025-04-11

### Added
- Add support to remove folders from Apple Notes by @antoniorodr
- Add support to Apple Reminders by @antoniorodr
- Add fuzzy search and refactoring by @antoniorodr

### Changed
- Update readme, add changelog, contributing and code of conduct by @antoniorodr

## [0.1.1] - 2025-04-07

### Added
- Add new tests by @antoniorodr
- Add memo_notes_test and refactor memo.py by @antoniorodr

### Changed
- Small fix and refactoring by @antoniorodr
- Delete author from readme by @antoniorodr
- Update issue templates by @antoniorodr
- Update readme with warning for notes with images/att by @antoniorodr
- Update readme with demo by @antoniorodr

## [0.1.0] - 2025-04-06

### Changed
- Update pyproject.toml by @antoniorodr
- Update README by @antoniorodr
- Refactoring by @antoniorodr
- Update validation_memo function to make add need a folder by @antoniorodr
- Update readme by @antoniorodr
- Update readme and add new functions as flist by @antoniorodr
- Small fix and add function to move the note from folder by @antoniorodr
- Initial commit by @antoniorodr

### New Contributors
* @antoniorodr made their first contribution

[0.5.3]: https://github.com/antoniorodr/memo/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/antoniorodr/memo/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/antoniorodr/memo/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/antoniorodr/memo/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/antoniorodr/memo/compare/v0.3.6...v0.4.0
[0.3.6]: https://github.com/antoniorodr/memo/compare/v0.3.5...v0.3.6
[0.3.5]: https://github.com/antoniorodr/memo/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/antoniorodr/memo/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/antoniorodr/memo/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/antoniorodr/memo/compare/v0.2.2...v0.3.2
[0.2.2]: https://github.com/antoniorodr/memo/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/antoniorodr/memo/compare/v0.1.1...v0.2.1
[0.1.1]: https://github.com/antoniorodr/memo/compare/v0.1.0...v0.1.1

<!-- generated by git-cliff -->
