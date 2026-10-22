# Beatraxus-themes

Official themes for the [Beatraxus](https://github.com/Harbertraj/Beatraxus) music player.
In the app: **Settings → Appearance → Themes → Browse**.

A theme is a small `.json` file that holds **data only, never code**: colours, a DSP palette,
a seekbar style, a font, background/blur settings, corner roundness, the mini player and quality badge,
the Surround screen look, and icons (recolour, resize, or your own icon images). The app validates
everything it downloads and ignores anything it does not recognise. The Themes screen draws a preview of
the real app (home, now playing, mini player, icons) from your file, so you can see the result before applying.

## Add a theme (pull request)

1. Copy `themes/aurora-night.json` to `themes/<your-id>.json`.
   The id uses `a-z`, `0-9`, `-`, `_` (max 48 characters) and **must match the file name**.
2. Edit the values (see the format below).
3. Run `python3 tools/validate.py`. It checks your file and rebuilds `index.json`.
4. Open a pull request with both files. CI re-runs the same check.

To update a theme, edit its file and raise `version`. The app then shows **Update** on it.

## Format

```json
{
  "schema": 1,
  "id": "aurora-night",
  "name": "Aurora Night",
  "author": "Harbertraj",
  "version": 1,
  "mode": "dark",
  "colors": {
    "accent": "#3CF2C0",
    "accentSecondary": "#8B5CF6",
    "preview": ["#0B0B14", "#3CF2C0", "#8B5CF6"]
  },
  "dsp": { "palette": "aurora_dusk" },
  "seekbar": "BEATRAXUS_MATRIX",
  "font": "outfit",
  "background": { "mode": "BLUR", "blurScale": 1.0, "blurDarkness": 0.4, "solidIntensity": 0.6, "solidDarkness": 0.4 },

  "shape":    { "cornerScale": 1.15 },
  "player":   { "albumArt": "DEPTH", "qualityBadge": "GLASSMORPHIC", "miniStyle": "PILL", "miniHeight": 68,
                "miniCorner": 40, "miniArtCorner": 20, "miniProgressRing": true, "miniShowTime": true, "miniTintFromArt": true },
  "surround": { "room": "dark", "visualizer": "wave", "beams": true, "animated": true, "arcs": true, "screen": true },
  "icons":    { "color": "#CFFFF1", "scale": 1.0, "packTint": true,
                "pack": { "play": "play.png", "pause": "pause.png", "next": "next.png" } }
}
```

Everything from `"shape"` down, and `colors.background/surface/text`, is **optional**. A theme that leaves
something out does not touch that setting, so the user's own choice stays.

| Field | Values |
|---|---|
| `colors.accent` / `accentSecondary` | `#RRGGBB` (or `#AARRGGBB`). Drives switches, sliders, progress and fields across the app |
| `colors.preview` | 2-5 colours shown as the gallery card, so no images are needed |
| `dsp.palette` | `solar_flare`, `aurora_dusk`, `cyber_pop`, `rose_gold`, `glacier`, `verdant`. Or use `"dsp": {"primary": "#RRGGBB", "secondary": "#RRGGBB"}` for a custom pair |
| `seekbar` | `BEATRAXUS_PULSE`, `BEATRAXUS_THREAD`, `BEATRAXUS_PRISM`, `BEATRAXUS_MATRIX`, `BEATRAXUS_COMET`, `WAVEFORM`, `SPECTRUM_TIMELINE`, `LIVE_WAVEFORM` |
| `font` | An id from the app's Fonts screen, e.g. `outfit`, `poppins`, `inter`, `orbitron`. Unknown ids fall back to the system font |
| `background.mode` | `BLACK`, `SOLID` or `BLUR`, applied to every screen |
| `background.blurScale` | 0.25 to 2. Multiplies each screen's own default blur, so screens keep their relative look |
| `blurDarkness`, `solidIntensity`, `solidDarkness` | 0 to 1 |

| `colors.background` / `surface` / `text` | Optional `#RRGGBB`. Colours for Material parts of the app: dialogs, sheets, menus, cards, text fields |
| `shape.cornerScale` | 0.2 to 2. Roundness of cards, dialogs, buttons and chips (1 = the app's default) |
| `player.albumArt` | `NONE`, `SOFT_FADE`, `SLIDE`, `DEPTH`, `POP` |
| `player.qualityBadge` | `NONE`, `GOLDEN_SHIMMER`, `MINIMAL_OUTLINE`, `GLASSMORPHIC`, `NEON_PULSE` |
| `player.miniStyle` | `PILL` or `CLASSIC` |
| `player.miniHeight` / `miniCorner` / `miniArtCorner` | Same ranges as the sliders in the app: 56-120, 8-60, 0-40 |
| `player.miniProgressRing` / `miniShowTime` / `miniTintFromArt` | `true` or `false` |
| `surround.room` | `dark`, `studio`, `living` |
| `surround.visualizer` | `wave`, `spectrum`, `circle` |
| `surround.visualizerEnabled`, `speakerIcons`, `labels`, `beams`, `animated`, `arcs`, `screen` | `true` or `false` |
| `icons.color` | `#RRGGBB`. Recolours every light (near-white) icon; red/green status icons keep their colour |
| `icons.scale` | 0.7 to 1.4. Resizes every icon |
| `icons.pack` | Your own icon images: `{ "<icon key>": "<file>.png" }`. See below |
| `icons.packTint` | `true` (default) = your images are single-colour glyphs and the app recolours them; `false` = drawn as they are |

Files must be under 16 KB. Out-of-range numbers are clamped by the app.

## Icon packs

Icons are not limited to the ones built into the app: a theme can bring its own images.

1. Put PNG (or WebP) files in `icons/<theme id>/`. Each file is at most **32 KB** and **512x512 px**;
   96x96 white glyphs on a transparent background work well (the app recolours them).
2. List them in the theme's `icons.pack`, mapping a key to the file name.
3. `python3 tools/validate.py` checks that every file exists, is a real PNG/WebP, and is small enough.

Keys you can replace: `play`, `pause`, `next`, `previous`, `shuffle`, `repeat`, `repeat_one`, `favorite`,
`favorite_border`, `home`, `search`, `settings`, `queue`, `more`, `back`, `add`, `close`, `equalizer`,
`library`, `playlist`, `album`, `artist`, `folder`, `share`, `download`, `volume`, `lyrics`.
Icons you do not list stay the app's own. `python3 tools/make_icons.py` (needs Pillow) redraws the packs
that ship with the official themes; copy and change it for your own.

## Sharing without the store

In the app, **Themes → Import → Share my current look** makes a `beatraxus://theme?data=…` link
or a `BTX1.…` code that a friend can paste into **Import**. A shared link carries the settings, not
image files, so custom icon images only appear for themes whose files are in this repo.
