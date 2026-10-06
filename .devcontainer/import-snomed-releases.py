#!/usr/bin/env python3
"""Import RF2 ZIP files dropped into the Codespace landing zone."""

import argparse
import datetime
import re
import shutil
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LANDING_ZONE = REPOSITORY_ROOT / "import-landing-zone"
SWEDISH_CONCEPT = re.compile(
    r"/Snapshot/Terminology/sct2_Concept_Snapshot_(?!INT_)[A-Z0-9]+_(\d{8})\.txt$"
)
INTERNATIONAL_CONCEPT = re.compile(
    r"/Snapshot/Terminology/sct2_Concept_Snapshot_INT_(\d{8})\.txt$"
)


def dated_members(names, pattern):
    return [match.group(1) for name in names if (match := pattern.search(name))]


def release_target(archive_path):
    try:
        with ZipFile(archive_path) as archive:
            names = archive.namelist()
    except (BadZipFile, OSError) as error:
        raise RuntimeError(f"Not a readable RF2 ZIP archive: {archive_path.name}") from error

    swedish_concepts = dated_members(names, SWEDISH_CONCEPT)
    swedish_descriptions = [
        name for name in names if "/Snapshot/Terminology/sct2_Description_Snapshot-sv_" in name
    ]
    swedish_languages = [
        name for name in names if "/Snapshot/Refset/Language/der2_cRefset_LanguageSnapshot-sv_" in name
    ]
    swedish_dependencies = [
        name for name in names if "/Snapshot/Refset/Metadata/der2_ssRefset_ModuleDependencySnapshot_" in name
    ]

    if swedish_concepts or swedish_descriptions or swedish_languages:
        if not (
            len(swedish_concepts) == 1
            and len(swedish_descriptions) == 1
            and len(swedish_languages) == 1
            and len(swedish_dependencies) == 1
        ):
            raise RuntimeError(
                f"Could not uniquely identify the Swedish RF2 release in {archive_path.name}."
            )
        dates = [
            swedish_concepts[0],
            *dated_members(swedish_descriptions, re.compile(r"_(\d{8})\.txt$")),
            *dated_members(swedish_languages, re.compile(r"_(\d{8})\.txt$")),
            *dated_members(swedish_dependencies, re.compile(r"_(\d{8})\.txt$")),
        ]
        release_type = "sv"
    else:
        international_concepts = dated_members(names, INTERNATIONAL_CONCEPT)
        international_dependencies = [
            name
            for name in names
            if re.search(
                r"/Snapshot/Refset/Metadata/der2_ssRefset_ModuleDependencySnapshot_INT_\d{8}\.txt$",
                name,
            )
        ]
        if len(international_concepts) != 1 or len(international_dependencies) != 1:
            raise RuntimeError(
                f"Could not uniquely identify an International RF2 release in {archive_path.name}."
            )
        dates = [
            international_concepts[0],
            *dated_members(international_dependencies, re.compile(r"_(\d{8})\.txt$")),
        ]
        release_type = "international"

    expected_date_count = 4 if release_type == "sv" else 2
    if len(dates) != expected_date_count:
        raise RuntimeError(f"Could not determine a unique release date in {archive_path.name}.")
    if len(set(dates)) != 1:
        raise RuntimeError(f"RF2 files declare inconsistent release dates in {archive_path.name}.")

    try:
        release_date = datetime.datetime.strptime(dates[0], "%Y%m%d").date().isoformat()
    except ValueError as error:
        raise RuntimeError(f"Invalid RF2 release date in {archive_path.name}.") from error
    return release_type, release_date


def import_archives(landing_zone, repository_root):
    landing_zone.mkdir(parents=True, exist_ok=True)
    log_path = landing_zone / "landing-zone-log.md"
    if not log_path.exists():
        log_path.write_text("# SNOMED CT landing-zone import log\n", encoding="utf-8")

    archives = sorted(
        path for path in landing_zone.iterdir() if path.is_file() and path.suffix.lower() == ".zip"
    )
    if not archives:
        print(f"No RF2 ZIP files found in {landing_zone}.")
        return 0

    planned_moves = []
    planned_releases = set()
    for archive in archives:
        release_type, release_date = release_target(archive)
        destination_dir = repository_root / "snomed-ct" / release_type / release_date
        destination = destination_dir / archive.name
        release_key = (release_type, release_date)
        if release_key in planned_releases:
            raise RuntimeError(
                f"More than one ZIP in the landing zone identifies {release_type} {release_date}."
            )
        existing_archives = destination_dir.is_dir() and any(
            path.is_file() and path.suffix.lower() == ".zip"
            for path in destination_dir.iterdir()
        )
        if destination.exists() or existing_archives:
            raise RuntimeError(
                f"A ZIP already exists for {release_type} {release_date} in {destination_dir}; "
                "move or review it before importing another archive for this release."
            )
        planned_moves.append((archive, destination, release_type, release_date))
        planned_releases.add(release_key)

    with log_path.open("a", encoding="utf-8") as log:
        for source, destination, release_type, release_date in planned_moves:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            relative_destination = destination.relative_to(repository_root).as_posix()
            timestamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
            log.write(
                f"\n- {timestamp}: moved `{source.name}` to `{relative_destination}` "
                f"({release_type} {release_date})."
            )
            print(f"Imported {source.name} -> {relative_destination}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Move RF2 ZIP files from import-landing-zone into dated release folders."
    )
    parser.add_argument(
        "--landing-zone", type=Path, default=LANDING_ZONE, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--repository-root", type=Path, default=REPOSITORY_ROOT, help=argparse.SUPPRESS
    )
    args = parser.parse_args()
    return import_archives(args.landing_zone.resolve(), args.repository_root.resolve())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)