# informatik-01-codespace
Basic workspace/codespace setup, variant #01, for informaticians to use for running e.g. terminology server and openEHR-assistant tools

## Create your own Codespace

This repository that acts as a template repository is maintained by the workspace maintainers, likely from Karolinska's Platform team. If your organisation permits it, create a separate repository from this template (as described below) rather than working directly in the maintained repository. Repository creation and access are controlled by your organisation; ask its administrator if you cannot create a repository or access Codespaces.

### Create your own repository (first time)

1. Sign in to GitHub and open this repository.
2. Select **Use this template** and then **Create a new repository**. 
3. Choose an owner (either your private github account or your employee's, e.g. regionstockholm) and a choose a repository name. 
4. In the new repository, select **Code > Codespaces > Create codespace on main**.

GitHub tehn builds the development container from `.devcontainer/devcontainer.json`. The first build can take several minutes. When it is ready, VS Code will open in tha web browser - inside it open a "terminal" and check that at least these tools are available by typing each line folowed by enter:

```bash
sct --help
python3 --version
```

SNOMED CT RF2 ZIP archives are distributed separately and are not stored in Git. Import the releases you are authorized to use as described in "First-time SNOMED CT setup" below. The imported archives and generated databases remain local to your Codespace.

### Open a Codespace directly

If you have been granted access to an existing organisation repository (a renamed copy of the template repository), you do not need to create another copy. Open that repository on GitHub, select **Code > Codespaces > Create codespace on main**, and wait for the devcontainer to finish building. Use a separate Codespace for your own work so that personal files, generated databases, and running services do not interfere with anyone else's environment unless asked to cooperate in same codespace.

![alt text](image-3.png)

### First-time SNOMED CT setup

The container installs the SCT command, but it does not automatically download SNOMED CT releases or build a database. If you are a logged in employee of Region Stockholm Download the required RF2 ZIP files from the internal [Snomed-release-filer](https://sllse.sharepoint.com/:f:/s/KTeamsKITScrumTeams/IgCcDD7gSG9eRZrB6qmU0RO5Afr1xyJX7rxVpe4SxcFTdxw?e=ABU7RG) Teams file area. In the VS Code Explorer, drag the downloaded ZIP files into the repository's `import-landing-zone` folder, then run:

```bash
python3 .devcontainer/import-snomed-releases.py
python3 .devcontainer/load-snomed-release.py
python3 .devcontainer/build-latest-snomed-database.py
```

The import script identifies each release from its RF2 contents, moves it into the dated `snomed-ct/` folder, and removes it from `import-landing-zone`. It records the time and destination in `import-landing-zone/landing-zone-log.md`; after a successful import, that log is the only file left in the landing zone. The ZIP archives in `snomed-ct/` are ignored by Git and stay local to the Codespace.

After the build completes, start the local terminology server when needed:

```bash
cd "$SCT_DATA_HOME/data" && sct serve --db swedish-snomed.db
```

The forwarded server is available from the Codespace's **Ports** view. See [SCT terminology tooling](#sct-terminology-tooling) for selecting a release or troubleshooting compatible International and Swedish distributions.

 You can also from you own scripts call HL7 Nordic Ontoserver at https://tx-nordics.fhir.org/fhir/r4/, a FHIR R4 terminology server with SNOMED CT and other terminologies installed if you do not want to run a local copy 

## Available programming language runtimes
- Deno (for Javascript/Typescript)
- Python (version 3)
- Rust
- Java/JVM

## Installed servers, MCPs etc.
- openehr-assistant from https://cadasto.github.io/openehr-assistant/
- local SCT SNOMED CT tools backed by the built Swedish database

### SNOMED CT AI skills

This repository includes two reusable AI skills for the local `sct` MCP tools:

- [SNOMED CT term mapping](.github/skills/snomed-term-mapping/SKILL.md) maps proprietary term lists to existing concepts and flags uncertain results or `NO_MAP` items for review.
- [SNOMED CT concept modelling](.github/skills/snomed-concept-modelling/SKILL.md) turns unresolved items into a validated post-coordinated expression and a separate draft proposal for the responsible authoring or National Release Center process.

These skills support terminology work; they do not approve mappings, mint new SCTIDs, or replace clinical and terminology-authoring review.

For terminology lookups, agents and users can use either the local SCT tools or the [HL7 Nordic Ontoserver](https://tx-nordics.fhir.org/fhir/r4/). The Ontoserver provides SNOMED CT as well as some other installed terminologies through its FHIR R4 endpoint. When using it, identify the terminology and version or edition where relevant, and clearly distinguish results from the local Swedish SCT database.

### Using the openEHR assistant
For an openEHR task like translating, you can explicitly ask the assistant to use the MCP and its openEHR guidance:

> Use the openEHR MCP for this: Find and retrieve the existing archetype [paste its ID or name here] and add/update a translation of its human-readable text into Swedish. Preserve the archetype structure, node identifiers, terminology codes, and constraints. Clearly flag terms whose Swedish translation is uncertain or needs review, and identify the source archetype in your response.

Replace the placeholder with the ID or name you want to work on. The assistant should use the openEHR tools and guidance to retrieve the source before translating it; don’t ask it to invent an archetype or terminology codes.

### SCT terminology tooling
The codespace image installs [SCT](https://github.com/pacharanero/sct) v0.27.0 as the `sct` command. The version is pinned in `.devcontainer/Dockerfile`; rebuild the dev container after changing it.

In addition to the local SCT database, terminology services can be queried from the [HL7 Nordic Ontoserver](https://tx-nordics.fhir.org/fhir/r4/). It exposes SNOMED CT and some other terminologies through FHIR R4 and can be useful when the required terminology is not available in the local database.

International and Swedish SNOMED CT RF2 releases are imported into `snomed-ct/international/<YYYY-MM-DD>/` and `snomed-ct/sv/<YYYY-MM-DD>/`. Their original ZIP filenames are preserved, and the ZIPs are ignored by Git. Download only releases you are authorized to access from the internal [Snomed-release-filer](https://sllse.sharepoint.com/:f:/s/KTeamsKITScrumTeams/IgCcDD7gSG9eRZrB6qmU0RO5Afr1xyJX7rxVpe4SxcFTdxw?e=ABU7RG) Teams file area, then drag them into `import-landing-zone/` in the VS Code Explorer.

Run the importer to classify and move all ZIP files currently in the landing zone:

```bash
python3 .devcontainer/import-snomed-releases.py
```

The importer derives the edition and date from RF2 snapshot filenames, rejects unrecognized or ambiguous archives, and refuses to overwrite a ZIP already present for that edition and date. It moves accepted files into the dated folders and appends a timestamp and destination to `import-landing-zone/landing-zone-log.md`. It does not extract the archives. Release notes PDFs remain ordinary repository files; only RF2 ZIPs belong in the landing zone.

List Swedish releases now present in this Codespace, stage the newest one, or choose a specific tag:

```bash
python3 .devcontainer/load-snomed-release.py --list
python3 .devcontainer/load-snomed-release.py
python3 .devcontainer/load-snomed-release.py snomed-ct-sv-2026-05-31
```

The loader stages the selected Swedish archive under `SNOMED_CT_DISTRIBUTION_DIRECTORY` (`/shared-not-stored-in-git/snomed-ct-files`). SCT databases and derived files go under `SCT_DATA_HOME` (`/shared-not-stored-in-git/sct-data`). Each Codespace has its own persistent volume; these paths are not shared mounts across colleagues' Codespaces. Import both the Swedish release and the exact International release it requires before building.

To build the latest compatible Swedish release into its local SCT database, run:

```bash
python3 .devcontainer/build-latest-snomed-database.py
```

The script selects the newest Swedish folder, reads its International dependency from RF2 metadata, and requires that exact International release before layering the two archives. It stores `swedish-snomed.ndjson` and `swedish-snomed.db` under `$SCT_DATA_HOME/data`, applying the Swedish preferred terms from the Swedish language refset. It also builds SCT's transitive-closure table and indexes to speed up hierarchy queries. Example: The 2026-05-31 Swedish release requires International 2026-02-01; the later released bundled 2026-10-01 International release is not a substitute. To add or repair the closure table in an existing database, run `sct tct --db "$SCT_DATA_HOME/data/swedish-snomed.db"`. To start the server separately after a compatible build, run `cd "$SCT_DATA_HOME/data" && sct serve --db swedish-snomed.db`.

See [DEVCONTAINER-MAINTAINER-README.md](DEVCONTAINER-MAINTAINER-README.md) for release intake and compatibility requirements.

## Working with files and special directories 
You are remote controlling a small Linux computer
- The Visual Studio Code workspace that you see opens the directory /workspaces/informatik-01-codespace by default
- You can drag and drop files from you own computer (e.g. your windows laptop) onto the a directory in the file tree in Visual Studio Code and you can right-click a file in Visual Studio Code and select "Download" to let your browser download the file.
- /shared-not-stored-in-git - A persistent, non-version-controlled volume for staged SNOMED CT files and SCT data
- /personal-not-stored-in-git - A persistent, non-version-controlled volume for personal files
- There are many other directories on the computer:
![alt text](image-2.png)

## AI models

The Karolinska Platform team is investigating how to set up more user friendly and capable specialized enfironments in KIM (Karolinska's internal cloud), but for now we hope this free setup will help in some tasks regarding SNOMED CT, openEHR etc

Unless you have a Github subscription you will likely be provided with just a free (not so smart) AI agent, set it to "intelligence" before doing advanced work:
![alt text](image-1.png)

If you have some other subscription for example from Google, openAI/ChatGPT, ANthropic, [OpenCode](https://opencode.ai/) you can configure it under "manage models":
![alt text](image.png)

You will likely be asked for a secret api key - if you supply that secret you may not want to share your codespace with others who can copy your key and also don't put that key in a version controlled file in github...

### Free processor hours

Processor hours measure time while the Codespace is running, not how long the browser-based VS Code window is open. An open browser tab does not continuously use processor resources by itself, but terminals, servers, builds, and other processes running in the Codespace do. Persistent storage is handled separately.

To pause work in a terminal, press `Ctrl+C` to stop the foreground command, or type `exit` to close the shell. Check the **Terminal** panel for other open terminals and stop any running servers or jobs there too. For a quick check from a terminal, use `ps` or `top`; a server, build, or agent process that is still running can keep using Codespace resources even when its terminal is not visible. Closing the browser tab does not stop the Codespace.

When you are finished, stop the Codespace from the GitHub Codespaces menu, or from the Command Palette with **Codespaces: Stop Current Codespace**. A stopped Codespace keeps its files and can be restarted later, but it no longer uses processor hours. Delete it only when you also want to remove the Codespace environment and its stored data.

### Check usage 

To check usage, open GitHub **Settings > Billing & licensing > Plans and usage** (the exact menu names can vary) and look for the **Codespaces** usage section for processor hours and storage. The same page's **Copilot** section shows remaining or used agent and premium-request allowances when those are provided by your plan. Your organisation may instead show these details under its organisation billing or Copilot usage pages.