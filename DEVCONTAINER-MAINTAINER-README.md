# Devcontainer Maintainer Guide

This guide covers maintaining the devcontainer and its authorized International and Swedish SNOMED CT distributions.

## Add a SNOMED CT release

Keep release notes in the repository under a folder named for the release date:

```text
snomed-ct/international/YYYY-MM-DD/
snomed-ct/sv/YYYY-MM-DD/
```

Do not add RF2 ZIP archives to Git. They are distributed through the internal [Snomed-release-filer](https://sllse.sharepoint.com/:f:/s/KTeamsKITScrumTeams/IgCcDD7gSG9eRZrB6qmU0RO5Afr1xyJX7rxVpe4SxcFTdxw?e=ABU7RG) Teams file area and imported into each Codespace as needed. The ZIP files are ignored by Git after import; release notes PDFs can remain in the dated repository folders.

Before building, check the Swedish package's active module dependency metadata. The builder reads its required International target effective time and will only use the matching dated International folder. Do not substitute a newer or older International release. The 2026-05-31 Swedish package requires International 2026-02-01, so the 2026-10-01 International release cannot be used for that build; download the matching 2026-02-01 RF2 package from Teams and import it into the Codespace.

Ensure the Teams file area and its permissions remain limited to people authorized to access the distributions. Anyone who can access the archive can copy it, so do not place RF2 ZIPs in Git, public storage, or an unapproved shared location.

Users download the required RF2 ZIPs from Teams and drag them from their computer into the Codespace's `import-landing-zone/` folder in the VS Code Explorer. The importer identifies release edition and date from RF2 snapshot files, moves each archive into the matching local dated folder, and records the move in `import-landing-zone/landing-zone-log.md`:

```bash
python3 .devcontainer/import-snomed-releases.py
```

Import one or more ZIPs at a time. The script validates every ZIP and checks for destination conflicts before moving any of them. It preserves the original ZIP filename and does not extract archives. After import, the landing zone contains only its log. Do not commit the imported archives.

The loader lists imported Swedish releases and stages the newest or a selected one into each Codespace's persistent directory:

```bash
python3 .devcontainer/load-snomed-release.py --list
python3 .devcontainer/load-snomed-release.py
python3 .devcontainer/load-snomed-release.py snomed-ct-sv-2026-05-31
```

The no-argument form selects the newest imported Swedish release. A specific tag selects a particular imported release. No token or Releases API access is needed. Each Codespace stages its own copy under `/shared-not-stored-in-git/snomed-ct-files/<tag>/`; the build script stages the compatible International package alongside it.

## Devcontainer maintenance

SCT's binary version is pinned by `SCT_VERSION` in `.devcontainer/Dockerfile`. Update the pin and rebuild the devcontainer to change it. Bundling RF2 files does not automatically load them into SCT.

`SNOMED_CT_DISTRIBUTION_DIRECTORY` points to `/shared-not-stored-in-git/snomed-ct-files`. `SCT_DATA_HOME` points to `/shared-not-stored-in-git/sct-data`, where SCT discovers generated databases under `data/`. Both are per-Codespace Docker volumes, not network-shared storage.

## Repository roadmap

- Add authorized International and Swedish SNOMED CT RF2 releases using the dated-folder process above.
- Provide an example of archetype translation.
- Provide an example of SNOMED terminology mapping.
- Add VS Code plugins for Excel, ADL, AQL, and related formats.

Possible longer-term work:

- Plugins for ontologies/OWL2.
- Add a small-scale CDR, such as FerroEHR.