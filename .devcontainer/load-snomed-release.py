#!/usr/bin/env python3
"""Stage an imported Swedish SNOMED CT RF2 release."""

import argparse
import datetime
import os
import re
import shutil
import sys
from pathlib import Path


TAG_PREFIX = "snomed-ct-sv-"
ARCHIVE_NAME = "snomed-ct-rf2.zip"
RELEASES_DIR = Path(__file__).resolve().parents[1] / "snomed-ct" / "sv"


def is_swedish_tag(tag):
    if not tag.startswith(TAG_PREFIX):
        return False
    date_string = tag[len(TAG_PREFIX) :]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_string):
        return False
    try:
        datetime.date.fromisoformat(date_string)
    except ValueError:
        return False
    return True


def list_swedish_releases():
    if not RELEASES_DIR.is_dir():
        return []
    dates = [
        path.name
        for path in RELEASES_DIR.iterdir()
        if path.is_dir()
        and is_swedish_tag(f"{TAG_PREFIX}{path.name}")
        and sum(
            child.is_file() and child.suffix.lower() == ".zip"
            for child in path.iterdir()
        ) == 1
    ]
    return [f"{TAG_PREFIX}{date}" for date in sorted(dates, reverse=True)]


def get_release_archive(tag):
    if not is_swedish_tag(tag):
        raise RuntimeError("Use a tag like snomed-ct-sv-2026-05-31, or 'latest'.")
    release_date = tag.removeprefix(TAG_PREFIX)
    release_dir = RELEASES_DIR / release_date
    archives = sorted(
        path for path in release_dir.iterdir() if path.is_file() and path.suffix.lower() == ".zip"
    )
    if len(archives) != 1:
        raise RuntimeError(f"{release_dir} must contain exactly one RF2 ZIP archive.")
    return archives[0]


def main():
    parser = argparse.ArgumentParser(
        description="Stage the latest or a selected imported Swedish SNOMED CT RF2 release."
    )
    parser.add_argument("tag", nargs="?", default="latest", help="release tag, or latest (default)")
    parser.add_argument("--list", action="store_true", help="list imported Swedish SNOMED CT tags")
    args = parser.parse_args()

    releases = list_swedish_releases()
    if args.list:
        if not releases:
            print("No imported Swedish SNOMED CT releases found.")
        for release in releases:
            print(release)
        return 0

    if args.tag == "latest":
        if not releases:
            raise RuntimeError("No imported Swedish SNOMED CT releases found.")
        tag = releases[0]
    else:
        tag = args.tag
    source_archive = get_release_archive(tag)

    data_root = Path(
        os.environ.get(
            "SNOMED_CT_DISTRIBUTION_DIRECTORY",
            "/shared-not-stored-in-git/snomed-ct-files",
        )
    )
    release_dir = data_root / tag
    archive_path = release_dir / ARCHIVE_NAME
    release_dir.mkdir(parents=True, exist_ok=True)

    temporary_archive = release_dir / f".{ARCHIVE_NAME}.tmp"
    try:
        shutil.copy2(source_archive, temporary_archive)
        os.replace(temporary_archive, archive_path)
    finally:
        temporary_archive.unlink(missing_ok=True)

    print(f"Staged {tag}: {archive_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)