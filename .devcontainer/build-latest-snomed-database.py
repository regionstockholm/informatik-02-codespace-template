#!/usr/bin/env python3
"""Build an SCT database from a compatible International release and Swedish extension."""

import csv
import datetime
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile


ARCHIVE_NAME = "snomed-ct-rf2.zip"
TAG_PREFIX = "snomed-ct-sv-"
SWEDISH_LANGUAGE_REFSET_ID = "46011000052107"
PREFERRED_ACCEPTABILITY_ID = "900000000000548007"
INTERNATIONAL_CORE_MODULE_ID = "900000000000012004"


def apply_swedish_preferred_terms(ndjson_path, rf2_archive):
    records = [
        json.loads(line)
        for line in ndjson_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    concept_ids = {record["id"] for record in records if "id" in record}

    with ZipFile(rf2_archive) as archive:
        description_paths = [
            name
            for name in archive.namelist()
            if "/Snapshot/Terminology/sct2_Description_Snapshot-sv_" in name
        ]
        language_paths = [
            name
            for name in archive.namelist()
            if "/Snapshot/Refset/Language/der2_cRefset_LanguageSnapshot-sv_" in name
        ]
        if len(description_paths) != 1 or len(language_paths) != 1:
            raise RuntimeError("Expected one Swedish snapshot description and language refset file.")

        descriptions = {}
        with archive.open(description_paths[0]) as source:
            reader = csv.DictReader(
                io.TextIOWrapper(source, encoding="utf-8-sig", newline=""),
                delimiter="\t",
            )
            for row in reader:
                if row["active"] == "1" and row["conceptId"] in concept_ids:
                    descriptions[row["id"]] = (row["conceptId"], row["term"])

        preferred_terms = {}
        with archive.open(language_paths[0]) as source:
            reader = csv.DictReader(
                io.TextIOWrapper(source, encoding="utf-8-sig", newline=""),
                delimiter="\t",
            )
            for row in reader:
                description = descriptions.get(row["referencedComponentId"])
                if (
                    row["active"] == "1"
                    and row["refsetId"] == SWEDISH_LANGUAGE_REFSET_ID
                    and row["acceptabilityId"] == PREFERRED_ACCEPTABILITY_ID
                    and description
                ):
                    concept_id, term = description
                    previous_term = preferred_terms.setdefault(concept_id, term)
                    if previous_term != term:
                        raise RuntimeError(
                            f"Multiple Swedish preferred terms found for concept {concept_id}."
                        )

    for record in records:
        if "id" not in record:
            continue
        preferred_term = preferred_terms.get(record["id"])
        if preferred_term and preferred_term != record["preferred_term"]:
            synonyms = record.get("synonyms") or []
            if record["preferred_term"] not in synonyms:
                synonyms.append(record["preferred_term"])
            record["preferred_term"] = preferred_term
            record["synonyms"] = [term for term in synonyms if term != preferred_term]

    for record in records:
        if record.get("_type") == "sct_provenance":
            record.pop("content_fingerprint", None)

    localized_path = ndjson_path.with_suffix(".localized.ndjson")
    try:
        with localized_path.open("w", encoding="utf-8") as destination:
            for record in records:
                destination.write(json.dumps(record, ensure_ascii=False) + "\n")
        localized_path.replace(ndjson_path)
    finally:
        localized_path.unlink(missing_ok=True)


def required_international_release_date(swedish_archive):
    with ZipFile(swedish_archive) as archive:
        dependency_paths = [
            name
            for name in archive.namelist()
            if "/Snapshot/Refset/Metadata/der2_ssRefset_ModuleDependencySnapshot_" in name
        ]
        if len(dependency_paths) != 1:
            raise RuntimeError("Expected one Swedish snapshot module dependency file.")

        target_dates = set()
        with archive.open(dependency_paths[0]) as source:
            reader = csv.DictReader(
                io.TextIOWrapper(source, encoding="utf-8-sig", newline=""),
                delimiter="\t",
            )
            for row in reader:
                if (
                    row["active"] == "1"
                    and row["referencedComponentId"] == INTERNATIONAL_CORE_MODULE_ID
                ):
                    target_dates.add(row["targetEffectiveTime"])

    if len(target_dates) != 1:
        raise RuntimeError(
            "The Swedish release must declare exactly one International core release dependency."
        )
    target_date = next(iter(target_dates))
    try:
        return datetime.datetime.strptime(target_date, "%Y%m%d").date().isoformat()
    except ValueError as error:
        raise RuntimeError(
            f"Invalid International release dependency date: {target_date}."
        ) from error


def main():
    script_dir = Path(__file__).resolve().parent
    loader = script_dir / "load-snomed-release.py"

    releases = subprocess.run(
        [sys.executable, str(loader), "--list"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.splitlines()
    tags = [line.strip() for line in releases if line.strip().startswith(TAG_PREFIX)]
    if not tags:
        raise RuntimeError("No imported Swedish SNOMED CT releases found.")

    tag = tags[0]
    subprocess.run([sys.executable, str(loader), tag], check=True)

    distribution_dir = Path(
        os.environ.get(
            "SNOMED_CT_DISTRIBUTION_DIRECTORY",
            "/shared-not-stored-in-git/snomed-ct-files",
        )
    )
    archive = (distribution_dir / tag / ARCHIVE_NAME).resolve()
    if not archive.is_file():
        raise RuntimeError(f"The staged RF2 archive was not found: {archive}")
    international_date = required_international_release_date(archive)
    international_dir = (
        script_dir.parent / "snomed-ct" / "international" / international_date
    )
    international_archives = (
        sorted(
            path
            for path in international_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ".zip"
        )
        if international_dir.is_dir()
        else []
    )
    if len(international_archives) != 1:
        raise RuntimeError(
            f"The Swedish release requires International RF2 {international_date}; "
            f"expected exactly one ZIP in {international_dir}. "
            "Do not substitute a different International release."
        )

    staged_international_dir = distribution_dir / f"snomed-ct-int-{international_date}"
    staged_international_dir.mkdir(parents=True, exist_ok=True)
    staged_international_archive = staged_international_dir / ARCHIVE_NAME
    temporary_archive = staged_international_dir / f".{ARCHIVE_NAME}.tmp"
    try:
        shutil.copy2(international_archives[0], temporary_archive)
        os.replace(temporary_archive, staged_international_archive)
    finally:
        temporary_archive.unlink(missing_ok=True)

    data_dir = Path(
        os.environ.get("SCT_DATA_HOME", "/shared-not-stored-in-git/sct-data")
    ).expanduser() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "sct",
            "ndjson",
            "--rf2",
            str(staged_international_archive),
            "--rf2",
            str(archive),
            "--locale",
            "sv-SE",
            "--output",
            "swedish-snomed.ndjson",
        ],
        check=True,
        cwd=data_dir,
    )
    apply_swedish_preferred_terms(data_dir / "swedish-snomed.ndjson", archive)
    subprocess.run(
        [
            "sct",
            "sqlite",
            "--ndjson",
            "swedish-snomed.ndjson",
            "--transitive-closure",
        ],
        check=True,
        cwd=data_dir,
    )
    print(
        f"Built SCT database for {tag} on International RF2 {international_date} "
        f"in {data_dir}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)