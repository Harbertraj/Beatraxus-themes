# Beatraxus-themes

Official themes for the [Beatraxus](https://github.com/Harbertraj/Beatraxus) music player.
In the app: **Settings → Appearance → Themes → Browse**.

A theme is a small `.json` file that holds **data only, never code**: colours, a DSP palette,
a seekbar style, a font and background/blur settings. The app validates everything it downloads
and ignores anything it does not recognise.

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
  "background": { "mode": "BLUR", "blurScale": 1.0, "blurDarkness": 0.4, "solidIntensity": 0.6, "solidDarkness": 0.4 }
}
```

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

Files must be under 16 KB. Out-of-range numbers are clamped by the app.

## Sharing without the store

In the app, **Themes → Import → Share my current look** makes a `beatraxus://theme?data=…` link
or a `BTX1.…` code that a friend can paste into **Import**.
