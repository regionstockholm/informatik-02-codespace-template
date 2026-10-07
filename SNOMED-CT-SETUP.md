# First-time SNOMED CT setup

[← Back to README](README.md)

The codespace container installs the SCT command automatically, but it does not automatically download SNOMED CT releases or build a database. You have to get hold of suitable SNOMED CT distribution ZIP files that are licensed to your organisation from your national release centre. Example: If you are a logged-in employee of Region Stockholm (which holds a licence) just download the required RF2 ZIP files from the internal [Snomed-release-filer](https://sllse.sharepoint.com/:f:/s/KTeamsKITScrumTeams/IgCcDD7gSG9eRZrB6qmU0RO5Afr1xyJX7rxVpe4SxcFTdxw?e=ABU7RG) Teams file area that is only available to employees. In the VS Code Explorer, drag the downloaded ZIP files into the repository's `import-landing-zone` folder, and check that they have all landed there (it can take some time), then run these three commands in the VS Code terminal:

```bash
python3 .devcontainer/import-snomed-releases.py
python3 .devcontainer/load-snomed-release.py
python3 .devcontainer/build-latest-snomed-database.py
```

The import script identifies each release from its RF2 contents, moves it into the dated `snomed-ct/` folder, and removes it from `import-landing-zone`. It records the time and destination in `import-landing-zone/landing-zone-log.md`; after a successful import, that log is the only file left in the landing zone. The ZIP archives in `snomed-ct/` are ignored by Git and stay local to the Codespace.

The script selects the newest Swedish folder, reads its International dependency from RF2 metadata, and requires that exact International release before layering the two archives. It stores `swedish-snomed.ndjson` and `swedish-snomed.db` under `$SCT_DATA_HOME/data`, applying the Swedish preferred terms from the Swedish language refset. It also builds SCT's transitive-closure table and indexes to speed up hierarchy queries. Example: The 2026-05-31 Swedish release requires International 2026-02-01; the later released bundled 2026-10-01 International release is not a substitute. To add or repair the closure table in an existing database, run `sct tct --db "$SCT_DATA_HOME/data/swedish-snomed.db"`. To start the server separately after a compatible build, run `cd "$SCT_DATA_HOME/data" && sct serve --db swedish-snomed.db`.

See [DEVCONTAINER-MAINTAINER-README.md](DEVCONTAINER-MAINTAINER-README.md) for release intake and compatibility requirements.
