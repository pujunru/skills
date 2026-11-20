---
name: excalidraw-input
description: Let the user contribute context as a hand-drawn Excalidraw diagram instead of prose. Opens a live Excalidraw canvas inside the chat when the client supports one; otherwise pre-creates a drawing file, opens it in the user's editor, waits for them to draw, then reads the diagram back into context. Use when the user runs /excalidraw-input, says "let me draw it", "I'll sketch this", "hard to explain in words", or wants to give a diagram as input.
user-invocable: true
argument-hint: "[what to draw, e.g. 'the auth flow']"
---

# Excalidraw Input

The user draws; you read the drawing and treat it as context, the same way
you would treat a pasted spec. The arguments, if any, say what the drawing is
about. Use them as the drawing's title and as the question you will answer
with it.

Pick the first mode that works:

1. **Live canvas** — the client can render an Excalidraw canvas inline.
2. **File** — create a drawing file, open it for the user, wait.

Either way, end by reading the drawing back and confirming your reading
(see [Read it back](#read-it-back)).

## 1. Live canvas

Use this mode when a tool that renders Excalidraw scenes in the chat is
available — for example an Excalidraw MCP app exposing `read_me` and
`create_view`. If the tools are deferred, load them first. If no such tool
exists, skip to [File](#2-file).

1. Call the format reference tool (`read_me`) once per conversation.
2. Call `create_view` with a starter scene:
   - a `cameraUpdate` first (800×600 is a good default),
   - a title text (fontSize 28) naming what to draw,
   - a muted hint text (`#757575`, fontSize 16): "Expand to fullscreen to
     draw. Tell me when you're done."
   - **Optional seed:** if the conversation already holds a model of the
     thing (components, steps, entities), draw that draft as labeled boxes
     and arrows so the user corrects it instead of starting blank. Say that
     it's a draft.
3. Remember the returned `checkpointId`.
4. Tell the user in one or two lines: expand the canvas to fullscreen, draw
   or edit, then reply "done" (with anything they want to add in words).
   Then **stop and wait** — end your turn.

When the user replies:

- If their edits reached you (the app sends the edited scene or a context
  update with element data), read the elements the way
  [Read it back](#read-it-back) describes.
- If you can only see your own starter scene, don't guess at what they drew.
  Say the canvas didn't send their edits back, then switch to
  [File](#2-file): create the file pre-filled with your starter elements and
  ask them to redraw there. You can continue the canvas later with
  `{"type":"restoreCheckpoint","id":"<checkpointId>"}` as the first element
  if you need to show them your interpretation.

## 2. File

The helper script lives next to this file:
`scripts/excalidraw_io.py` (Python 3, standard library only). Resolve its
absolute path from this skill's directory and run it with `python3`.

### Choose where the file goes

- **Obsidian vault.** If the user keeps an Obsidian vault with an Excalidraw
  workflow (the working directory is inside one, or the user's or vault's
  instructions describe one), follow those instructions. Typically: the
  vault's assets folder, `--format obsidian`, which writes
  `<Title> YYYY-MM-DD HH.MM.SS.excalidraw.md` in the plugin's parsed format.
  If the drawing belongs to a note, embed it there with
  `![[<file name without .md>]]` once the user agrees.
- **Anywhere else.** A plain `.excalidraw` file. Default to a `diagrams/`
  folder in the current project if it has one, else the session's scratch or
  temp directory. Don't litter a repo: ask before adding a new folder to it.

### Create it

```bash
python3 <skill-dir>/scripts/excalidraw_io.py new \
  --title "Auth flow" --prompt "Sketch the login flow" \
  --dir <folder> [--format obsidian]
```

The command prints the absolute path. `--blank` skips the title and hint.
It never overwrites an existing file unless you pass `--force`.

### Open it for the user

Try these in order and stop at the first that works:

- **Obsidian file:** an Obsidian tool that opens a vault file (for example
  `open_file` from an Obsidian REST MCP server, with the vault-relative
  path). Without one, on macOS:
  `open "obsidian://open?vault=<vault name>&file=<URL-encoded vault-relative path>"`.
  If it opens as Markdown, tell the user to switch to Excalidraw view from
  the "More options" menu.
- **`.excalidraw` file:** VS Code with the Excalidraw extension
  (`code --list-extensions | grep -i excalidraw`, then `code <path>`);
  otherwise the OS default app (`open <path>` on macOS, `xdg-open` on
  Linux). If nothing handles the type, tell the user to open
  <https://excalidraw.com>, load the file (Open → choose file), draw, and
  save it back to the same path.

Tell the user the file name, how it opened, and to reply "done" when
finished. Then **stop and wait** — end your turn. Do not poll the file.

## Read it back

When the user says they're done:

```bash
python3 <skill-dir>/scripts/excalidraw_io.py read <path>
```

It handles `.excalidraw`, `.excalidraw.json`, and Obsidian `.excalidraw.md`
(both `json` and `compressed-json` scenes) and prints:

- frames and how many elements each holds,
- shapes in reading order, with labels, fills and dashed outlines,
- free text,
- arrows and lines resolved to the shapes they connect (unbound arrows are
  matched by proximity and flagged as such),
- groups, freehand pen strokes (with the nearest labeled thing), and
  embedded images.

Use `read <path> --json` when you need exact coordinates or styles.

If the file hasn't changed since you created it (same elements as the
starter), the editor may not have saved yet — Obsidian and iCloud can lag a
few seconds. Ask the user to save, or wait for them to confirm, then read
again. Don't loop.

Then, in your reply:

1. **Restate the diagram** in a few lines: the entities, how they connect,
   and what the layout implies (left-to-right flow, layers, grouping,
   dashed = optional/async, color meaning if consistent).
2. **Ask about what the data can't tell you**: freehand strokes, ambiguous
   arrows flagged as matched by proximity, symbols without labels. Keep it
   to the questions that change your understanding.
3. **Carry on with the original task** using the diagram as context. If the
   user gave no task, ask what they'd like done with it.

Keep the file. If the user wants changes drawn back into the diagram, edit
that same file (for Obsidian, follow the vault's format rules: every text
element also listed under `## Text Elements` as `text ^id`).
