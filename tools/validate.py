#!/usr/bin/env python3
"""Validates every themes/*.json the same way the Beatraxus app does, then rewrites index.json.

Usage:  python3 tools/validate.py          (validate + rebuild index.json)
        python3 tools/validate.py --check  (validate only; fails if index.json is out of date)
"""
import json, re, struct, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")
COLOR = re.compile(r"^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
PALETTES = {"solar_flare", "aurora_dusk", "cyber_pop", "rose_gold", "glacier", "verdant"}
SEEKBARS = {"BEATRAXUS_PULSE", "BEATRAXUS_THREAD", "BEATRAXUS_PRISM", "BEATRAXUS_MATRIX",
            "BEATRAXUS_COMET", "WAVEFORM", "SPECTRUM_TIMELINE", "LIVE_WAVEFORM"}
BG_MODES = {"BLACK", "SOLID", "BLUR"}
MAX_BYTES = 16 * 1024

# Optional sections (mirror ThemeCodec in the app)
ALBUM_ART = {"NONE", "SOFT_FADE", "SLIDE", "DEPTH", "POP"}
QUALITY_BADGES = {"NONE", "GOLDEN_SHIMMER", "MINIMAL_OUTLINE", "GLASSMORPHIC", "NEON_PULSE"}
MINI_STYLES = {"PILL", "CLASSIC"}
SURROUND_ROOMS = {"dark", "studio", "living"}
SURROUND_VISUALIZERS = {"wave", "spectrum", "circle"}
ICON_KEYS = {"play", "pause", "next", "previous", "shuffle", "repeat", "repeat_one", "favorite",
             "favorite_border", "home", "search", "settings", "queue", "more", "back", "add", "close",
             "equalizer", "library", "playlist", "album", "artist", "folder", "share", "download",
             "volume", "lyrics"}
ICON_FILE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}\.(png|webp)$")
MAX_ICON_BYTES = 32 * 1024
MAX_ICON_PIXELS = 512
MAX_PACK_ICONS = 40


def num_in(d, key, lo, hi, errors, label):
    if key in d:
        v = d[key]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not (lo <= v <= hi):
            errors.append(f"{label}.{key} must be a number from {lo} to {hi}")


def bool_in(d, key, errors, label):
    if key in d and not isinstance(d[key], bool):
        errors.append(f"{label}.{key} must be true or false")


def check_icon_file(theme_id, key, name, errors):
    f = ROOT / "icons" / theme_id / name
    if not f.is_file():
        errors.append(f"icons.pack.{key}: missing file icons/{theme_id}/{name}")
        return
    data = f.read_bytes()
    if len(data) > MAX_ICON_BYTES:
        errors.append(f"icons/{theme_id}/{name} is larger than 32 KB")
    if name.endswith(".png"):
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            errors.append(f"icons/{theme_id}/{name} is not a PNG")
        else:
            w, h = struct.unpack(">II", data[16:24])
            if w > MAX_ICON_PIXELS or h > MAX_ICON_PIXELS:
                errors.append(f"icons/{theme_id}/{name} is {w}x{h}; max is {MAX_ICON_PIXELS}x{MAX_ICON_PIXELS}")
    elif data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        errors.append(f"icons/{theme_id}/{name} is not a WebP")


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

    for k in ("background", "surface", "text"):
        if k in c and not COLOR.match(str(c[k])): errors.append(f"bad colors.{k}")

    shape = d.get("shape")
    if shape is not None:
        if not isinstance(shape, dict): errors.append("shape must be an object")
        else: num_in(shape, "cornerScale", 0.2, 2, errors, "shape")

    p = d.get("player")
    if p is not None:
        if not isinstance(p, dict): errors.append("player must be an object")
        else:
            for key, allowed in (("albumArt", ALBUM_ART), ("qualityBadge", QUALITY_BADGES), ("miniStyle", MINI_STYLES)):
                if key in p and str(p[key]).upper() not in allowed: errors.append(f"unknown player.{key}")
            num_in(p, "miniHeight", 56, 120, errors, "player")
            num_in(p, "miniCorner", 8, 60, errors, "player")
            num_in(p, "miniArtCorner", 0, 40, errors, "player")
            for key in ("miniProgressRing", "miniShowTime", "miniTintFromArt"): bool_in(p, key, errors, "player")

    sr = d.get("surround")
    if sr is not None:
        if not isinstance(sr, dict): errors.append("surround must be an object")
        else:
            if "room" in sr and sr["room"] not in SURROUND_ROOMS: errors.append("unknown surround.room")
            if "visualizer" in sr and sr["visualizer"] not in SURROUND_VISUALIZERS: errors.append("unknown surround.visualizer")
            for key in ("visualizerEnabled", "speakerIcons", "labels", "beams", "animated", "arcs", "screen"):
                bool_in(sr, key, errors, "surround")

    ic = d.get("icons")
    if ic is not None:
        if not isinstance(ic, dict): errors.append("icons must be an object")
        else:
            if "color" in ic and not COLOR.match(str(ic["color"])): errors.append("bad icons.color")
            num_in(ic, "scale", 0.7, 1.4, errors, "icons")
            bool_in(ic, "packTint", errors, "icons")
            pack = ic.get("pack") or {}
            if not isinstance(pack, dict): errors.append("icons.pack must be an object")
            else:
                if len(pack) > MAX_PACK_ICONS: errors.append(f"icons.pack has more than {MAX_PACK_ICONS} icons")
                for key, name in pack.items():
                    if key not in ICON_KEYS: errors.append(f"unknown icon key '{key}'")
                    elif not ICON_FILE.match(str(name)): errors.append(f"icons.pack.{key}: bad file name")
                    else: check_icon_file(path.stem, key, str(name), errors)
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
