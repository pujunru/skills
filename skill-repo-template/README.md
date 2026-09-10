# Skill Repo Template

This is the scaffolding for a **skill repository** — a standalone GitHub repo
that holds one *themed* collection of related Claude Code (or other
skills-compatible agent) skills. For example: a "writing skills" repo holding
`clear-writing`, `editing-pass`, `tone-check`, etc.

A skill repo is meant to be:

1. Cloned/used directly on its own, **and**
2. Linked into a hub repo (like the parent [`skills`](../) monorepo) as a
   Git submodule, **and**
3. Installable per-skill via [`npx skills`](https://www.skills.sh/) without
   cloning anything.

## Layout

```
skill-repo-template/
├── README.md              this file — describe the theme of the collection
└── skills/
    └── example-skill/
        └── SKILL.md       one folder per skill, each with a SKILL.md
```

Every skill lives in its own folder under `skills/`. The folder name is the
skill's slug (kebab-case) and must contain a `SKILL.md`. Add any supporting
files (scripts, templates, reference docs) alongside `SKILL.md` in that same
folder — keep each skill self-contained so it can be installed independently.

## SKILL.md format

```markdown
---
name: example-skill
description: One sentence describing what this skill does and when to use it.
---

Instructions for the skill go here...
```

The frontmatter `name` and `description` are what agents use to decide when
to invoke the skill (surfaced e.g. in Claude Code's `/` menu), so keep the
description specific and action-oriented.

## Using this template

To start a new themed skill repo (e.g. "writing-skills"):

```bash
# 1. Copy this template out to a new directory
cp -R skill-repo-template ../writing-skills
cd ../writing-skills
rm -rf .git  # if copied with git history by accident

# 2. Rename the example skill, or add your own
mv skills/example-skill skills/clear-writing
$EDITOR skills/clear-writing/SKILL.md

# 3. Init git and push to a new GitHub repo
git init
git add .
git commit -m "Initial writing-skills repo"
gh repo create <your-account>/writing-skills --public --source=. --push

# 4. Link it into this hub as a submodule (see hub README)
```

## Installing a skill from this repo with npx

Once pushed to GitHub as `<owner>/<repo>`, any skill in `skills/<name>/` can
be installed directly into another project without cloning:

```bash
npx skills add <owner>/<repo>@<skill-name>
```

For example, once `writing-skills` exists:

```bash
npx skills add <owner>/writing-skills@clear-writing
```

See <https://www.skills.sh/> for the full CLI reference.
