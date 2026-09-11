# Skills instructions

This document covers, in detail:

1. How this hub is organized
2. How to author a new skill repo
3. Git submodule command reference for this hub
4. Installing skills with `npx skills`, without touching submodules at all

## 1. Organization

- **This repo (`skills`)** is a hub/index. It can also contain small,
  installable operational skills under `skills/<name>/` when they support the
  hub's installation workflow.
- **`skills/<name>/`** — a root-level, installable operational skill owned by
  this hub (for example, `skills/herdr-diff-pane/`).
- **`skill-repos/<name>/`** — one Git submodule per themed skill repo (e.g.
  `skill-repos/writing-skills/`, `skill-repos/infra-skills/`). Each is a
  fully independent GitHub repo with its own history, issues, and releases.
- **`skill-repo-template/`** — scaffolding you copy out to start a brand new
  themed skill repo. It is *not* a submodule; it's tracked directly in this
  repo as a starting point.

Each skill repo, in turn, contains one folder per individual skill under its
own `skills/` directory:

```
<skill-repo>/
└── skills/
    ├── <skill-a>/
    │   └── SKILL.md
    ├── <skill-b>/
    │   └── SKILL.md
    └── ...
```

This layout (`hub -> skills/<operational skill>` or `hub -> skill-repos/<theme
submodule> -> skills/<individual skill>`) lets you:

- `git submodule update --init --recursive` the whole hub and get every
  skill from every linked theme, **or**
- `npx skills add <owner>/<theme-repo> --all` to grab every skill from one
  theme into a project, with no submodules involved at all — or
  `npx skills add <owner>/<theme-repo>@<individual-skill>` for just one
  skill (see [section 4](#4-installing-with-npx-skills) for the difference,
  it's easy to install only one skill by accident), **or**
- `npx skills add <owner>/skills@<operational-skill>` to install a root-level
  operational skill from this hub.

## 2. Authoring a new skill repo

Full walkthrough: [`skill-repo-template/README.md`](skill-repo-template/README.md).

Summary:

```bash
cp -R skill-repo-template ../my-new-skill-repo
cd ../my-new-skill-repo
rm -rf .git
mv skills/example-skill skills/my-first-skill
$EDITOR skills/my-first-skill/SKILL.md
git init && git add . && git commit -m "Initial my-new-skill-repo"
gh repo create <owner>/my-new-skill-repo --public --source=. --push
```

Each `SKILL.md` needs YAML frontmatter with `name` and `description` — see
the template for the exact format. Keep each skill's folder self-contained
(scripts, references, templates alongside its `SKILL.md`) so it installs
cleanly on its own via `npx skills add`.

## 3. Git submodule command reference

Run these from the root of this hub repo unless noted otherwise.

### Add a new skill repo as a submodule

```bash
git submodule add https://github.com/<owner>/<repo>.git skill-repos/<repo>
git commit -m "Add <repo> submodule"
```

### Clone the hub with all submodules in one step

```bash
git clone --recurse-submodules https://github.com/<owner>/skills.git
```

### Populate submodules after a plain clone

```bash
git submodule update --init --recursive
```

### Pull the latest upstream commit for one submodule

```bash
git submodule update --remote skill-repos/<repo>
git add skill-repos/<repo>
git commit -m "Bump <repo> submodule"
```

### Pull the latest upstream commit for ALL submodules

```bash
git submodule update --remote --merge
git add skill-repos
git commit -m "Bump all submodules"
```

### Pull hub changes + submodule changes together

```bash
git pull
git submodule update --init --recursive
```

Or in one step for future pulls:

```bash
git pull --recurse-submodules
```

### Make an edit inside a submodule and push it back to its own repo

```bash
cd skill-repos/<repo>
git checkout main            # submodules default to detached HEAD
$EDITOR skills/<skill>/SKILL.md
git add . && git commit -m "Update <skill>"
git push origin main
cd ../..
git add skill-repos/<repo>   # record the new commit pointer in the hub
git commit -m "Bump <repo> submodule"
```

### Remove a submodule

```bash
git submodule deinit -f skill-repos/<repo>
git rm -f skill-repos/<repo>
rm -rf .git/modules/skill-repos/<repo>
git commit -m "Remove <repo> submodule"
```

## 4. Installing with `npx skills`

[`npx skills`](https://www.skills.sh/) (by Vercel Labs, npm package
[`skills`](https://www.npmjs.com/package/skills)) is a package manager for
the open agent-skills ecosystem. It fetches `SKILL.md` files directly from a
GitHub repo and installs them into the selected agent's skill directory — no
cloning or submodules required. It supports Codex, Claude Code, Cursor,
OpenCode, and many other agents.

### Default installation policy for agents

When an agent is asked to install skills from this hub or one of its linked
skill repos, it **must install every skill for every supported agent in the
local project** unless the user explicitly gives different instructions:

```bash
npx skills add <owner>/<skill-repo> --all
```

After a root-level skill has been committed and pushed, use this command for
the hub itself:

```bash
npx skills add pujunru/skills --all
```

This discovers root-level skills under `skills/`, such as
`skills/herdr-diff-pane/SKILL.md`, and installs all of them for every
supported agent. `--all` covers all skills in the named source repository; it
does not traverse linked submodule repositories. Install each themed
collection from its own repository with a separate `--all` command, for
example `npx skills add pujunru/writing-skills --all`.

`--all` is shorthand for `--skill '*' --agent '*' -y` — it installs every
skill in the repo, to every supported agent, without prompting. Treat that as
the required default. Do not select a subset of skills, limit installation to
one agent, or use global scope unless the user has explicitly asked for it.

### User-directed exceptions

When the user explicitly directs a narrower installation, use the requested
agent identifier or skill name. For example:

```bash
npx skills add <owner>/<skill-repo> --skill '*' --agent codex -y
npx skills add <owner>/<skill-repo> --skill '*' --agent claude-code -y
```

> ⚠️ **Do not** append `@<skill-name>` unless you deliberately want only
> that one skill. Installing `<owner>/<skill-repo>@<skill-name>` (with no
> `--all`) installs **only that single skill** and silently skips every
> other skill in the repo — easy to mistake for a full install, since the
> command still succeeds and prints an "Installation complete" summary.

### Explicit skill or scope exceptions

If the user explicitly asks for one specific skill or a global install:

```bash
npx skills add <owner>/<skill-repo>@<skill-name> --agent codex -y
npx skills add <owner>/<skill-repo> --all -g
```

The first command installs a named skill for Codex; the second performs a
user-requested global installation for every supported agent.

### Updating after upstream changes

Re-run the same `add --all` command you used originally — it overwrites
existing installs with the latest content from the repo. There is no
separate "sync" step; `npx skills add` is idempotent and safe to re-run.

> **Note:** use a current version of the `skills` CLI. `npx skills` fetches
> the latest published version unless you have pinned an older version.

This install path is completely independent of the submodule mechanism
above — you can use one, the other, or both. Submodules are for pulling in
a *whole themed collection* and tracking it inside this hub; `npx skills
add` is for grabbing *one skill* into an unrelated project on demand.
