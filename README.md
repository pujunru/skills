# skills

A monorepo hub of open, [agent-skills](https://www.skills.sh/)-compatible
skill collections. The skills can be installed for Codex, Claude Code,
Cursor, OpenCode, and other supported agents; they are not proprietary to any
one coding agent.

Themed collections of skills — e.g. "writing skills," "infra skills," "data
skills" — live in their **own** GitHub repositories, and this hub links to
each one as a [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
under [`skill-repos/`](skill-repos/). The hub can also contain small,
installable operational skills under [`skills/`](skills/) when they support
the hub's installation workflow.

See [`SKILLS.md`](SKILLS.md) for the full authoring, submodule, and
installation instructions.

## Layout

```
skills/
├── README.md
├── SKILLS.md                 detailed instructions (submodules + npx install)
├── .gitmodules                registered submodules (populated as you add repos)
├── skills/                    installable hub operational skills
│   └── herdr-diff-pane/
│       └── SKILL.md
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

## Installing skills without cloning

Skills in any linked repo can also be installed directly using the
[`npx skills`](https://www.skills.sh/) CLI, no submodules or cloning
required.

### Default installation policy for agents

When an agent is asked to install skills from this hub or a linked skill repo,
it **must install every skill for every supported agent in the local project**
by default:

```bash
npx skills add <owner>/<skill-repo> --all
```

After a root-level skill has been committed and pushed, install all hub-owned
operational skills with:

```bash
npx skills add pujunru/skills --all
```

That command discovers every root-level skill under `skills/`, including
`skills/herdr-diff-pane/SKILL.md`, then installs each one for every supported
agent. `--all` applies only to the repository named in the command. A themed
collection remains a separate source, for example:

```bash
npx skills add pujunru/writing-skills --all
```

`--all` expands to `--skill '*' --agent '*' -y`. Do not narrow the skill set,
agent targets, or installation scope unless the user explicitly instructs you
to do so. A user may explicitly request a single agent, a subset of skills, or
a global (`-g`) installation.

For example, only after an explicit request to target one agent:

```bash
npx skills add <owner>/<skill-repo> --skill '*' --agent codex -y
npx skills add <owner>/<skill-repo> --skill '*' --agent claude-code -y
```

> ⚠️ Omitting `--all` and appending `@<skill-name>` installs **only that one
> skill**, silently skipping the rest of the repo. See
> [`SKILLS.md`](SKILLS.md#installing-with-npx-skills) for the full
> explanation and when to use each form.
