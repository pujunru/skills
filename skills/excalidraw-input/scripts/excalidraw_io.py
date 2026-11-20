#!/usr/bin/env python3
"""Create and read Excalidraw drawings for the excalidraw-input skill.

Two subcommands, standard library only:

  new   Create a starter drawing and print its absolute path.
        --format excalidraw  -> <dir>/<slug>.excalidraw (plain Excalidraw JSON)
        --format obsidian    -> <dir>/<Title> YYYY-MM-DD HH.MM.SS.excalidraw.md

  read  Summarize a drawing so an agent can reason about it: labeled shapes,
        free text, arrows resolved to the shapes they connect, frames, groups,
        and freehand strokes. Accepts .excalidraw, .excalidraw.json, and
        Obsidian .excalidraw.md (parsed `json` or `compressed-json` scenes).
        --json dumps the raw non-deleted elements instead.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# lz-string decompressFromBase64 (Obsidian stores scenes as compressed-json)
# --------------------------------------------------------------------------

_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
_B64_REV = {ch: i for i, ch in enumerate(_B64)}


def lz_decompress_from_base64(data: str) -> str | None:
    data = re.sub(r"\s+", "", data)
    if not data:
        return ""
    length = len(data)

    def next_value(i: int) -> int:
        return _B64_REV.get(data[i], 0) if i < length else 0

    reset = 32
    dictionary: dict[int, str] = {}
    enlarge_in, dict_size, num_bits = 4, 4, 3
    result: list[str] = []
    state = {"val": next_value(0), "pos": reset, "idx": 1}

    def read_bits(n: int) -> int:
        bits, power = 0, 1
        maxpower = 1 << n
        while power != maxpower:
            resb = state["val"] & state["pos"]
            state["pos"] >>= 1
            if state["pos"] == 0:
                state["pos"] = reset
                state["val"] = next_value(state["idx"])
                state["idx"] += 1
            if resb > 0:
                bits |= power
            power <<= 1
        return bits

    first = read_bits(2)
    if first == 0:
        c = chr(read_bits(8))
    elif first == 1:
        c = chr(read_bits(16))
    else:
        return ""
    dictionary[3] = c
    w = c
    result.append(c)

    while True:
        if state["idx"] > length:
            return ""
        code = read_bits(num_bits)
        if code in (0, 1):
            dictionary[dict_size] = chr(read_bits(8 if code == 0 else 16))
            dict_size += 1
            code = dict_size - 1
            enlarge_in -= 1
        elif code == 2:
            return "".join(result)
        if enlarge_in == 0:
            enlarge_in = 1 << num_bits
            num_bits += 1
        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:
            entry = w + w[0]
        else:
            return None
        result.append(entry)
        dictionary[dict_size] = w + entry[0]
        dict_size += 1
        enlarge_in -= 1
        w = entry
        if enlarge_in == 0:
            enlarge_in = 1 << num_bits
            num_bits += 1


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


def load_scene(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix != ".md":
        return json.loads(text)

    m = re.search(r"```compressed-json\s*\n(.*?)```", text, re.S)
    if m:
        raw = lz_decompress_from_base64(m.group(1))
        if not raw:
            sys.exit(f"error: could not decompress the scene in {path}")
        return json.loads(raw)
    m = re.search(r"```json\s*\n(.*?)```", text, re.S)
    if m:
        return json.loads(m.group(1))
    sys.exit(f"error: no Excalidraw scene found in {path}")


# --------------------------------------------------------------------------
# new
# --------------------------------------------------------------------------


def _base(el_type: str, x: float, y: float, w: float, h: float, **extra) -> dict:
    now = int(time.time() * 1000)
    el = {
        "id": "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=16)),
        "type": el_type,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": random.randint(1, 2**31 - 1),
        "version": 1,
        "versionNonce": random.randint(1, 2**31 - 1),
        "isDeleted": False,
        "boundElements": None,
        "updated": now,
        "link": None,
        "locked": False,
    }
    el.update(extra)
    return el


def _text(x: float, y: float, s: str, size: int, color: str = "#1e1e1e") -> dict:
    lines = s.split("\n")
    w = max(len(line) for line in lines) * size * 0.55
    h = len(lines) * size * 1.25
    return _base(
        "text", x, y, w, h,
        strokeColor=color,
        text=s, originalText=s, fontSize=size, fontFamily=5,
        textAlign="left", verticalAlign="top", containerId=None,
        lineHeight=1.25, autoResize=True,
    )


def starter_elements(title: str, prompt: str | None) -> list[dict]:
    els = [_text(0, 0, title, 28)]
    hint = prompt or "Draw below. Tell the agent when you're done."
    els.append(_text(0, 48, hint, 16, "#757575"))
    return els


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "diagram"


def cmd_new(args: argparse.Namespace) -> None:
    out_dir = Path(args.dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    elements = [] if args.blank else starter_elements(args.title, args.prompt)
    app_state = {"gridSize": None, "viewBackgroundColor": "#ffffff"}

    if args.format == "obsidian":
        stamp = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        safe_title = re.sub(r'[\\/:*?"<>|#^\[\]]', "-", args.title).strip()
        path = out_dir / f"{safe_title} {stamp}.excalidraw.md"
        scene = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
            "elements": elements,
            "appState": app_state,
            "files": {},
        }
        text_lines = "\n\n".join(
            f"{e['text']} ^{e['id']}" for e in elements if e["type"] == "text"
        )
        body = (
            "---\nexcalidraw-plugin: parsed\ntags: [excalidraw]\n---\n"
            "==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==\n\n"
            "# Excalidraw Data\n\n## Text Elements\n"
            f"{text_lines}\n\n%%\n## Drawing\n```json\n"
            f"{json.dumps(scene, ensure_ascii=False, indent=1)}\n```\n%%\n"
        )
    else:
        path = out_dir / f"{slugify(args.title)}.excalidraw"
        if path.exists() and not args.force:
            path = out_dir / f"{slugify(args.title)}-{datetime.now():%Y%m%d-%H%M%S}.excalidraw"
        scene = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": elements,
            "appState": app_state,
            "files": {},
        }
        body = json.dumps(scene, ensure_ascii=False, indent=2) + "\n"

    if path.exists() and not args.force:
        sys.exit(f"error: {path} already exists (pass --force to overwrite)")
    path.write_text(body, encoding="utf-8")
    print(path)


# --------------------------------------------------------------------------
# read
# --------------------------------------------------------------------------

SHAPES = {"rectangle", "ellipse", "diamond", "image", "embeddable", "iframe"}


def _label(el: dict, by_id: dict) -> str:
    for b in el.get("boundElements") or []:
        t = by_id.get(b.get("id"))
        if t and t["type"] == "text":
            return (t.get("text") or t.get("originalText") or "").replace("\n", " ")
    return ""


def _name(el: dict | None, by_id: dict) -> str:
    if el is None:
        return "(nothing)"
    if el["type"] == "text":
        return f'"{el.get("text", "").strip()}"'
    lab = _label(el, by_id) or el.get("name") or ""
    return f'{el["type"]} "{lab}"' if lab else f'{el["type"]} #{el["id"][:6]}'


def _box(el: dict) -> str:
    return f'@({round(el["x"])},{round(el["y"])} {round(abs(el["width"]))}x{round(abs(el["height"]))})'


def _nearest_shape(pt: tuple[float, float], shapes: list[dict], slack: float = 40) -> dict | None:
    px, py = pt
    best, best_d = None, slack
    for s in shapes:
        x0, y0 = s["x"], s["y"]
        x1, y1 = x0 + s["width"], y0 + s["height"]
        dx = max(x0 - px, 0, px - x1)
        dy = max(y0 - py, 0, py - y1)
        d = (dx * dx + dy * dy) ** 0.5
        if d <= best_d:
            best, best_d = s, d
    return best


def cmd_read(args: argparse.Namespace) -> None:
    path = Path(args.path).expanduser()
    scene = load_scene(path)
    els = [e for e in scene.get("elements", []) if not e.get("isDeleted")]
    if args.json:
        print(json.dumps(els, ensure_ascii=False, indent=1))
        return

    by_id = {e["id"]: e for e in els}
    shapes = [e for e in els if e["type"] in SHAPES]
    frames = [e for e in els if e["type"] in ("frame", "magicframe")]
    texts = [e for e in els if e["type"] == "text" and not e.get("containerId")]
    connectors = [e for e in els if e["type"] in ("arrow", "line")]
    freedraw = [e for e in els if e["type"] == "freedraw"]

    out: list[str] = [f"# {path.name}", f"{len(els)} elements"]

    if frames:
        out.append("\n## Frames")
        for f in frames:
            members = [e for e in els if e.get("frameId") == f["id"]]
            out.append(f'- "{f.get("name") or "Frame"}" {_box(f)}: {len(members)} elements')

    if shapes:
        out.append("\n## Shapes (top-to-bottom, left-to-right)")
        for s in sorted(shapes, key=lambda e: (round(e["y"] / 40), e["x"])):
            lab = _label(s, by_id)
            fill = s.get("backgroundColor")
            fill = f" fill={fill}" if fill and fill != "transparent" else ""
            dashed = " dashed" if s.get("strokeStyle") != "solid" else ""
            out.append(f'- {s["type"]} {_box(s)}{fill}{dashed}: {lab or "(no label)"}')

    if texts:
        out.append("\n## Free text")
        for t in sorted(texts, key=lambda e: (round(e["y"] / 40), e["x"])):
            out.append(f'- {_box(t)} size={t.get("fontSize")}: {t.get("text", "").strip()}')

    if connectors:
        out.append("\n## Arrows and lines")
        for a in connectors:
            pts = a.get("points") or [[0, 0]]
            start = (a["x"] + pts[0][0], a["y"] + pts[0][1])
            end = (a["x"] + pts[-1][0], a["y"] + pts[-1][1])
            sb = (a.get("startBinding") or {}).get("elementId")
            eb = (a.get("endBinding") or {}).get("elementId")
            src = by_id.get(sb) if sb else _nearest_shape(start, shapes + texts)
            dst = by_id.get(eb) if eb else _nearest_shape(end, shapes + texts)
            guessed = "" if (sb and eb) else " (unbound; endpoints matched by proximity)"
            head = "->" if a.get("endArrowhead") else "--"
            if a.get("startArrowhead") and a.get("endArrowhead"):
                head = "<->"
            lab = _label(a, by_id)
            lab = f' [{lab}]' if lab else ""
            out.append(f"- {_name(src, by_id)} {head} {_name(dst, by_id)}{lab}{guessed}")

    groups: dict[str, list[str]] = {}
    for e in els:
        for g in e.get("groupIds") or []:
            groups.setdefault(g, []).append(_name(e, by_id))
    if groups:
        out.append("\n## Groups")
        for g, names in groups.items():
            out.append(f"- {g[:6]}: {', '.join(names)}")

    if freedraw:
        out.append("\n## Freehand strokes")
        out.append(
            f"{len(freedraw)} pen strokes; their meaning can't be read from data. "
            "Ask the user, or check which shapes/text they sit near:"
        )
        for f in freedraw[:20]:
            near = _nearest_shape((f["x"] + f["width"] / 2, f["y"] + f["height"] / 2), shapes + texts, 120)
            out.append(f"- stroke {_box(f)} near {_name(near, by_id)}")
        if len(freedraw) > 20:
            out.append(f"- ... {len(freedraw) - 20} more")

    files = scene.get("files") or {}
    if files:
        out.append(f"\n## Embedded images\n{len(files)} image file(s) embedded.")

    print("\n".join(out))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="create a starter drawing and print its path")
    n.add_argument("--title", required=True)
    n.add_argument("--dir", default=".")
    n.add_argument("--format", choices=["excalidraw", "obsidian"], default="excalidraw")
    n.add_argument("--prompt", help="hint text placed under the title")
    n.add_argument("--blank", action="store_true", help="no title or hint elements")
    n.add_argument("--force", action="store_true", help="overwrite an existing file")
    n.set_defaults(func=cmd_new)

    r = sub.add_parser("read", help="summarize a drawing")
    r.add_argument("path")
    r.add_argument("--json", action="store_true", help="dump raw elements")
    r.set_defaults(func=cmd_read)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
