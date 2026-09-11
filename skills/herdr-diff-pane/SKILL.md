---
name: herdr-diff-pane
description: Open the current Git diff in a sibling Herdr pane with an interactive, scrollable Delta view. Use when the user asks to inspect a diff in another Herdr pane.
user-invocable: true
---

# Herdr Diff Pane

Open a sibling pane that shows the current repository diff through `delta` and
`less`, preserving the user's focus in the calling pane.

## Prerequisites

Check these prerequisites in this order before using any Herdr command:

```bash
command -v herdr >/dev/null && echo herdr-found || echo herdr-missing
test "${HERDR_ENV:-}" = 1 && echo in-herdr || echo not-in-herdr
command -v delta >/dev/null && echo delta-found || echo delta-missing
```

If any check fails, report the failed prerequisite and stop. Do not install a
missing tool, open a pane, or attempt to control Herdr from outside its active
environment.

## Open the diff view

After all checks pass, read the current Herdr instructions before controlling
the session:

```bash
herdr --skill
herdr pane layout --current
```

Use the layout to choose a sibling direction: split a wide pane to the right;
split a narrow or tall pane downward. Preserve the current working directory
and keep focus in the caller pane:

```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus
```

Read the new pane ID from the JSON response. Never infer it from the pane
layout or UI position. Run the interactive view in that returned pane:

```bash
herdr pane run <pane-id> "git diff --submodule=diff --color=always | delta --paging=never | less -R"
```

`less -R` keeps ANSI color and provides scrolling. The user can use arrow
keys, Page Up/Page Down, or `/` to search, then press `q` to return to the
shell. Leave the pane open until the user asks to close it.
