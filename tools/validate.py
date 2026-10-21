#!/usr/bin/env python3
"""Validates every themes/*.json the same way the Beatraxus app does, then rewrites index.json.

Usage:  python3 tools/validate.py          (validate + rebuild index.json)
        python3 tools/validate.py --check  (validate only; fails if index.json is out of date)
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")
COLOR = re.compile(r"^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
PALETTES = {"solar_flare", "aurora_dusk", "cyber_pop", "rose_gold", "glacier", "verdant"}
SEEKBARS = {"BEATRAXUS_PULSE", "BEATRAXUS_THREAD", "BEATRAXUS_PRISM", "BEATRAXUS_MATRIX",
            "BEATRAXUS_COMET", "WAVEFORM", "SPECTRUM_TIMELINE", "LIVE_WAVEFORM"}
BG_MODES = {"BLACK", "SOLID", "BLUR"}
MAX_BYTES = 16 * 1024


def check(path):
    errors = []
    raw = path.read_text(encoding="utf-8")
    if len(raw.encode()) > MAX_BYTES:
        return None, ["larger than 16 KB"]
    try:
        d = json.loads(raw)
    except ValueError as e:
        return None, [f"invalid JSON: {e}"]
    if d.get("schema", 1) != 1: errors.append("schema must be 1")
    if not ID.match(str(d.get("id", ""))): errors.append("bad id")
    if d.get("id") != path.stem: errors.append("id must match the file name")
    if not str(d.get("name", "")).strip(): errors.append("missing name")
    if d.get("mode", "dark") not in ("dark", "light"): errors.append("mode must be dark or light")
    c = d.get("colors") or {}
    if not COLOR.match(str(c.get("accent", ""))): errors.append("colors.accent must be #RRGGBB")
    if "accentSecondary" in c and not COLOR.match(str(c["accentSecondary"])): errors.append("bad colors.accentSecondary")
    prev = c.get("preview")
    if prev is not None and not (2 <= len(prev) <= 5 and all(COLOR.match(str(x)) for x in prev)):
        errors.append("colors.preview must be 2-5 colours")
    dsp = d.get("dsp") or {}
    if "palette" in dsp:
        if dsp["palette"] not in PALETTES: errors.append("unknown dsp.palette")
    elif not (COLOR.match(str(dsp.get("primary", ""))) and COLOR.match(str(dsp.get("secondary", "")))):
        errors.append("dsp needs a palette id or primary+secondary colours")
    if "seekbar" in d and d["seekbar"] not in SEEKBARS: errors.append("unknown seekbar")
    bg = d.get("background") or {}
    if "mode" in bg and bg["mode"] not in BG_MODES: errors.append("unknown background.mode")
    return d, errors


def main():
    bad = False
    index = []
    for path in sorted((ROOT / "themes").glob("*.json")):
        d, errors = check(path)
        if errors:
            bad = True
            print(f"FAIL {path.name}: " + "; ".join(errors))
            continue
        c = d["colors"]
        index.append({"id": d["id"], "name": d["name"], "author": d.get("author", "Unknown"),
                      "version": d.get("version", 1), "file": f"themes/{path.name}",
                      "mode": d.get("mode", "dark"),
                      "preview": c.get("preview") or [c["accent"], c.get("accentSecondary", c["accent"])]})
        print(f"ok   {path.name}")
    out = json.dumps({"schema": 1, "themes": index}, indent=2) + "\n"
    target = ROOT / "index.json"
    if "--check" in sys.argv:
        if not target.exists() or target.read_text() != out:
            print("index.json is out of date: run python3 tools/validate.py"); bad = True
    elif not bad:
        target.write_text(out)
    sys.exit(1 if bad else 0)


main()
