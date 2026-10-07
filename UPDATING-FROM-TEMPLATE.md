# Updating your repository copy from the template repository

[← Back to README](README.md)

A repository you create with **Use this template** is a separate Git repository. GitHub does _not_ auto-sync it when the template (e.g. `informatik-02-codespace-template`) changes (unlike a fork’s **Sync fork** button). GitHub also does **not** copy the template’s commit history into your repo — only the files at one snapshot — so your `main` and the template’s `main` are unrelated histories until you link them once (see below).

**One-time setup** — in your copy’s clone, add the template as an extra remote (name it `upstream`; keep `origin` as your repo):

```bash
git remote add upstream https://github.com/regionstockholm/informatik-02-codespace-template.git
```

**If/when you want updates from the template** — run these in a terminal in your clone (or Codespace):

```bash
git fetch upstream
git checkout main
git merge upstream/main
git status
```

**First merge only:** if Git says `fatal: refusing to merge unrelated histories`, that is expected for a repo created from the template. Run the same merge once with:

```bash
git merge upstream/main --allow-unrelated-histories
```

Resolve conflicts (very common in `README.md` if you rewrote it; also possible under `.devcontainer/`):

- Either manually: remove `<<<<<<<` / `=======` / `>>>>>>>` markers, `git add` the fixed files, then `git commit` (or `git merge --continue`).
- Or ask the AI in VS Code Chat to help resolve the conflicted files.

After this one-time merge, later updates can use plain `git merge upstream/main` without the extra flag.

**Partial updates (optional):** if you only want maintainer changes in certain paths (e.g. tooling, not the template README), after `git fetch upstream` you can bring over paths explicitly, then review and commit — for example:

```bash
git checkout upstream/main -- .devcontainer/ .github/
```

That overwrites those folders in your working tree with the template versions; adjust the paths to what you need.

**After a successful merge:** `git push origin main`. If `.devcontainer/` changed, rebuild the dev container (**Command Palette** → **Codespaces: Rebuild Container**).

Later runs: if `git merge upstream/main` prints **`Already up to date.`**, your branch already contains the template commits you merged previously. Use `git log --oneline main..upstream/main` to see template commits you have not merged yet.

You only need the steps above; there is no requirement to merge on every template change. Cherry-pick individual commits if you only want part of an update.
