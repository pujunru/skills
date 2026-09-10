# skills

A monorepo hub of [Claude Code](https://claude.com/claude-code) (and other
[agent-skills](https://www.skills.sh/)-compatible) skill collections.

This repo does not hold skills directly. Instead, each themed collection of
skills — e.g. "writing skills," "infra skills," "data skills" — lives in its
**own** GitHub repository, and this hub links to each one as a
[Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) under
[`skill-repos/`](skill-repos/). Think of this repo as an index/registry of
skill repos, not a place where individual skills are authored.

See [`SKILLS.md`](SKILLS.md) for the full authoring, submodule, and
installation instructions.

## Layout

```
skills/
├── README.md
├── SKILLS.md                 detailed instructions (submodules + npx install)
├── .gitmodules                registered submodules (populated as you add repos)
├── skill-repos/                each subfolder is a submodule -> a skill repo
│   └── <your-skill-repo>/      (added via `git submodule add`)
└── skill-repo-template/        scaffolding for starting a NEW skill repo
    └── skills/
        └── example-skill/
            └── SKILL.md
```

## Quick start

Clone this hub with all submodules populated:

```bash
git clone --recurse-submodules <this-repo-url>
```

Already cloned without `--recurse-submodules`? Pull them in after the fact:

```bash
git submodule update --init --recursive
```

## Adding a new skill repo (submodule)

1. Create the new skill repo from the template — see
   [`skill-repo-template/README.md`](skill-repo-template/README.md) for the
   full scaffolding walkthrough (layout, `SKILL.md` format, publishing to
   GitHub).
2. Link it into this hub:

   ```bash
   git submodule add https://github.com/<owner>/<your-skill-repo>.git skill-repos/<your-skill-repo>
   git commit -m "Add <your-skill-repo> submodule"
   ```

3. Pushing/pulling: submodule commits are independent of the hub's commits.
   After updating a submodule's own repo, come back here and:

   ```bash
   git submodule update --remote skill-repos/<your-skill-repo>
   git add skill-repos/<your-skill-repo>
   git commit -m "Bump <your-skill-repo> submodule"
   ```

Full command reference (clone, update, remove, etc.) is in
[`SKILLS.md`](SKILLS.md#git-submodule-command-reference).

## Installing individual skills without cloning

Skills in any linked repo can also be installed a la carte into another
project using the [`npx skills`](https://www.skills.sh/) CLI, no submodules
or cloning required:

```bash
npx skills add <owner>/<skill-repo>@<skill-name>
```

See [`SKILLS.md`](SKILLS.md#installing-with-npx-skills) for details.
