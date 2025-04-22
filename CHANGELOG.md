# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 23.04.2025

### Added

- Added support for exporting notes to the desktop and converting them to markdown format. Attachments and images will not be converted.

### Changed

- Small changes and updates to the README file.

## [0.2.3] - 15.04.2025

### Changed

- Added translations for the folder "Recently Deleted" to be able to filter it on all the languages MacOS supports.
- Small changes and updates to the README file.

### Fixed

- Fixed a bug caused by images on Notes when using the `-edit`flag. The images will not appear in the markdown preview (Temporary fix).

## [0.2.2] - 14.04.2025

### Added

- Added support for editing Apple Reminders title and due date.

### Changed

- Small changes and updates to the README file.
- Refactored codebase and applied minor output improvements.

## [0.2.1] - 11.04.2025

### Added

- Added support for delete Apple Notes folders with the `--remove` flag.

### Changed

- Small changes and updates to the README file.

## [0.2.0] - 09.04.2025

### Added

- Added functionality to `--delete` for Apple Notes.
- Added support to Apple Reminders. Now you can create, delete and mark reminders as completed.
- Basic test coverage for Apple Reminders.

### Changed

- Improved the output of some of the flags, with colors and better formatting.
- Small changes and updates to the README file.
- Refactored codebase and applied minor output improvements.

## [0.1.2] - 08.04.2025

### Added

- Added the `--search` flag to enable fuzzy searching of your notes.

### Changed

- Refactored codebase and applied minor output improvements.

## [0.1.1] - 07.04.2025

### Added

- Confirmation prompt when editing or moving notes that contain images or attachments.
- Memo will notify you if the folder you are trying to filter does not exist when using `memo notes --folder <foldername>`.
- Basic test coverage.

### Changed

- Refactored codebase and applied minor output improvements.

## [0.1.0] - 06.04.2025

Initial Release.

### Added

Initial release with core Apple Notes functionality:

- Create new notes in Apple Notes
- Edit existing notes
- Delete notes
- View a list of all notes
- Move notes between folders
- List all folders and subfolders

[0.3.0]: htpps://github.com/antoniorodr/memo/releases/tag/v0.3.0
[0.2.3]: https://github.com/antoniorodr/memo/releases/tag/v0.2.3
[0.2.2]: https://github.com/antoniorodr/memo/releases/tag/v0.2.2
[0.2.1]: https://github.com/antoniorodr/memo/releases/tag/v0.2.1
[0.2.0]: https://github.com/antoniorodr/memo/releases/tag/v0.2.0
[0.1.2]: https://github.com/antoniorodr/memo/releases/tag/v0.1.2
[0.1.1]: https://github.com/antoniorodr/memo/releases/tag/v0.1.1
[0.1.0]: https://github.com/antoniorodr/memo/releases/tag/v0.1.0
