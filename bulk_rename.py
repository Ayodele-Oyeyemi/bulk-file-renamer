#!/usr/bin/env python3
"""
bulk_rename.py

A simple CLI tool to bulk rename files in a directory.

Supports:
  - Adding a prefix and/or suffix to filenames
  - Find and replace text within filenames
  - Sequential numbering (e.g. photo_001.jpg, photo_002.jpg...)
  - Changing file extensions
  - Dry-run mode (preview changes before applying them)
  - Undo (rolls back the most recent rename operation using a log file)

Usage examples:
  # Preview adding a prefix to all files in a folder
  python bulk_rename.py ./photos --prefix "vacation_" --dry-run

  # Actually rename with a prefix
  python bulk_rename.py ./photos --prefix "vacation_"

  # Replace "IMG" with "photo" in filenames
  python bulk_rename.py ./photos --find "IMG" --replace "photo"

  # Sequentially number files, keeping original extensions
  python bulk_rename.py ./photos --sequence "photo_" --start 1 --padding 3

  # Undo the last rename operation performed in this folder
  python bulk_rename.py ./photos --undo
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

LOG_FILENAME = ".bulk_rename_log.json"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bulk rename files in a directory."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Path to the directory containing files to rename",
    )
    parser.add_argument(
        "--prefix", type=str, default="", help="Text to add to the start of each filename"
    )
    parser.add_argument(
        "--suffix", type=str, default="", help="Text to add to the end of each filename (before extension)"
    )
    parser.add_argument(
        "--find", type=str, default=None, help="Text to find in filenames"
    )
    parser.add_argument(
        "--replace", type=str, default="", help="Text to replace --find matches with"
    )
    parser.add_argument(
        "--sequence",
        type=str,
        default=None,
        help="Base name for sequential numbering, e.g. 'photo_' produces photo_001.jpg",
    )
    parser.add_argument(
        "--start", type=int, default=1, help="Starting number for --sequence (default: 1)"
    )
    parser.add_argument(
        "--padding", type=int, default=3, help="Digit padding for --sequence numbers (default: 3)"
    )
    parser.add_argument(
        "--ext", type=str, default=None, help="Change the file extension (e.g. '.txt')"
    )
    parser.add_argument(
        "--recursive", action="store_true", help="Include files in subdirectories"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without renaming any files"
    )
    parser.add_argument(
        "--undo", action="store_true", help="Undo the last rename operation in this directory"
    )
    return parser.parse_args()


def get_files(directory: Path, recursive: bool):
    if recursive:
        return sorted([p for p in directory.rglob("*") if p.is_file() and p.name != LOG_FILENAME])
    return sorted([p for p in directory.iterdir() if p.is_file() and p.name != LOG_FILENAME])


def build_new_name(original: Path, index: int, args) -> str:
    stem, ext = original.stem, original.suffix

    if args.sequence is not None:
        number = str(args.start + index).zfill(args.padding)
        new_stem = f"{args.sequence}{number}"
    else:
        new_stem = stem
        if args.find is not None:
            new_stem = new_stem.replace(args.find, args.replace)
        new_stem = f"{args.prefix}{new_stem}{args.suffix}"

    new_ext = args.ext if args.ext else ext
    if new_ext and not new_ext.startswith("."):
        new_ext = f".{new_ext}"

    return f"{new_stem}{new_ext}"


def load_log(directory: Path):
    log_path = directory / LOG_FILENAME
    if not log_path.exists():
        return None
    with open(log_path, "r") as f:
        return json.load(f)


def save_log(directory: Path, renames: list):
    log_path = directory / LOG_FILENAME
    with open(log_path, "w") as f:
        json.dump(
            {"timestamp": datetime.now().isoformat(), "renames": renames},
            f,
            indent=2,
        )


def do_undo(directory: Path):
    log = load_log(directory)
    if not log:
        print("No previous rename operation found to undo.")
        return

    errors = 0
    for entry in reversed(log["renames"]):
        old_path = Path(entry["old"])
        new_path = Path(entry["new"])
        if new_path.exists():
            new_path.rename(old_path)
            print(f"Restored: {new_path.name} -> {old_path.name}")
        else:
            print(f"Warning: expected file not found, skipping: {new_path}")
            errors += 1

    (directory / LOG_FILENAME).unlink(missing_ok=True)
    if errors:
        print(f"\nUndo completed with {errors} warning(s).")
    else:
        print("\nUndo completed successfully.")


def main():
    args = parse_args()
    directory = Path(args.directory).expanduser().resolve()

    if not directory.is_dir():
        print(f"Error: '{directory}' is not a valid directory.")
        sys.exit(1)

    if args.undo:
        do_undo(directory)
        return

    if not any([args.prefix, args.suffix, args.find is not None, args.sequence, args.ext]):
        print("Error: specify at least one of --prefix, --suffix, --find/--replace, --sequence, or --ext.")
        sys.exit(1)

    files = get_files(directory, args.recursive)
    if not files:
        print("No files found to rename.")
        return

    planned = []
    seen_names = set()
    for i, path in enumerate(files):
        new_name = build_new_name(path, i, args)
        new_path = path.parent / new_name

        if new_name in seen_names or (new_path.exists() and new_path != path):
            print(f"Skipping (name collision): {path.name} -> {new_name}")
            continue
        seen_names.add(new_name)

        if new_path != path:
            planned.append((path, new_path))

    if not planned:
        print("No files need renaming (names already match, or all skipped).")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Planned renames ({len(planned)}):\n")
    for old_path, new_path in planned:
        print(f"  {old_path.name}  ->  {new_path.name}")

    if args.dry_run:
        print("\nDry run only — no files were changed. Remove --dry-run to apply.")
        return

    renames_log = []
    for old_path, new_path in planned:
        old_path.rename(new_path)
        renames_log.append({"old": str(old_path), "new": str(new_path)})

    save_log(directory, renames_log)
    print(f"\nDone. {len(planned)} file(s) renamed.")
    print("Run with --undo to revert this operation if needed.")


if __name__ == "__main__":
    main()
