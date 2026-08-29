# Bulk File Renamer

A simple, dependency-free Python CLI tool for renaming multiple files at once.

No third-party libraries required — just Python's standard library.

## Features

- ✅ Add a prefix and/or suffix to filenames
- ✅ Find and replace text within filenames
- ✅ Sequential numbering (e.g. `photo_001.jpg`, `photo_002.jpg`, ...)
- ✅ Change file extensions in bulk
- ✅ Recursive mode (include subfolders)
- ✅ **Dry-run mode** — preview every change before anything is renamed
- ✅ **Undo** — revert the last rename operation

## Requirements

- Python 3.7+
- No external dependencies

## Usage

```bash
python bulk_rename.py <directory> [options]
```

### Options

| Flag           | Description                                              |
|----------------|-----------------------------------------------------------|
| `--prefix`     | Text to add to the start of each filename                 |
| `--suffix`     | Text to add before the extension                          |
| `--find`       | Text to search for in filenames                            |
| `--replace`    | Text to replace `--find` matches with                       |
| `--sequence`   | Base name for sequential numbering (e.g. `photo_`)          |
| `--start`      | Starting number for `--sequence` (default: `1`)            |
| `--padding`    | Digit padding for sequence numbers (default: `3`)           |
| `--ext`        | Change the file extension (e.g. `.txt`)                    |
| `--recursive`  | Include files in subdirectories                             |
| `--dry-run`    | Preview changes without renaming anything                   |
| `--undo`       | Revert the most recent rename operation in this directory    |

### Examples

**Preview adding a prefix:**
```bash
python bulk_rename.py ./photos --prefix "vacation_" --dry-run
```

**Actually apply the prefix:**
```bash
python bulk_rename.py ./photos --prefix "vacation_"
```

**Replace text in filenames:**
```bash
python bulk_rename.py ./photos --find "IMG" --replace "photo"
```

**Sequentially number files:**
```bash
python bulk_rename.py ./photos --sequence "photo_" --start 1 --padding 3
# IMG_9938.jpg -> photo_001.jpg
# IMG_9939.jpg -> photo_002.jpg
```

**Change file extensions:**
```bash
python bulk_rename.py ./docs --ext ".md"
```

**Undo the last operation:**
```bash
python bulk_rename.py ./photos --undo
```

## How undo works

Every time files are renamed, a hidden log file (`.bulk_rename_log.json`) is
written to the target directory recording the old and new name of each file.
Running `--undo` reads that log and reverses the changes, then deletes the log.

⚠️ Only the most recent operation can be undone. Running the tool again
overwrites the log.

## Safety notes

- Always run with `--dry-run` first to preview changes.
- The tool skips renames that would overwrite an existing file or collide
  with another planned name in the same batch.
- This tool renames files **in place** — it does not create copies. Back up
  important files before running bulk operations, just in case.

## Running tests

```bash
python -m unittest discover tests
```
