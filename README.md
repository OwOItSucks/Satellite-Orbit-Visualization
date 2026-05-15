# HKUST × Musico & FYBB#1 — Satellite Orbit Visualization

A single-page 3D satellite orbit demo built with CesiumJS.  
Visualizes two satellites (Musico / CSS and FYBB#1) with real orbital data,
an imagery overlay for the FYBB#1 scene area in Hong Kong, and an interactive
control panel — no backend required.

---

## Live Demo

Open `demo2.html` via a local HTTP server (required for `fetch`):

```bash
python -m http.server 8080
# → http://localhost:8080/demo2.html
```

> ⚠️ Do **not** open via `file://` — `fetch()` will be blocked by the browser.

---

## Data Files

Place the following under `./data/` relative to `demo2.html`:

| File | Description |
|---|---|
| `data/CSS_OEM.dat` | Musico (CSS) orbit state vectors in CCSDS OEM format |
| `data/FYBB1.tle` | FYBB#1 TLE (optional — falls back to hardcoded TLE) |

If `CSS_OEM.dat` is missing, the viewer shows an error and stops.  
If `FYBB1.tle` is missing, a hardcoded fallback TLE is used automatically.

---

## Features

- **Dual-satellite rendering** — Musico (OEM / ECEF state vectors) + FYBB#1 (TLE propagation)
- **Animated orbit paths** — PolylineGlowMaterial with lead/trail time
- **Occlusion fade** — satellites behind Earth dim to 30% opacity
- **Lagrange interpolation** — 5th-degree, smooth position sampling between 6-hour OEM points
- **Timebar** — custom scrubber with play/pause, independent of Cesium's native timeline
- **Orbit density control** — rebuild orbit polyline for 1 / 3 / 7 day windows around current time
- **Right panel** — real-time ECI position (X/Y/Z km), geodetic lon/lat, altitude, velocity per satellite
- **Basemap switcher** — Esri WorldImagery / OpenStreetMap / CartoDB Dark; HK imagery overlay preserved on switch
- **HK scene overlay** — HKSAR government WMS tiles clipped to FYBB#1 imagery footprint (113.82–114.50°E)
- **Left panel** — collapsible; shows orbital metadata, statistics, layer toggles, speed control, satellite selector

---

## Tech Stack

| Layer | Library / API |
|---|---|
| 3D Globe & Entities | CesiumJS 1.114 (CDN) |
| TLE Propagation | satellite.js 5.0.0 (CDN) |
| Orbit Data | CCSDS OEM (state vectors) + Two-Line Element sets |
| Satellite Icons | Canvas 2D API (generated at runtime, no image files) |
| Basemap | Esri ArcGIS MapServer · OpenStreetMap · CartoDB · Natural Earth II |
| Imagery Overlay | HKSAR Lands Department WMS (EPSG:4326 tile scheme) |
| Runtime | Vanilla JS (ES2020+), no build step, no framework |

---

## Key Implementation Notes

**Basemap layer management** — The HK WMS overlay is tagged `.isSceneLayer = true`.
On basemap switch, all layers *except* scene layers are removed; the overlay is then
raised to top. This keeps the imagery footprint visible regardless of which basemap is active.

**OEM vs TLE dual-path** — Musico uses pre-computed ECEF state vectors (OEM).
FYBB#1 uses `satellite.twoline2satrec` + `satellite.propagate` to generate
1-minute ECEF samples for a configurable window (default 3 days) centred on
the current clock time.

**`ArcGisMapServerImageryProvider` async construction** — Cesium 1.103+ requires
`ArcGisMapServerImageryProvider.fromUrl(url)` (returns a Promise).
All basemap provider factories in this project are therefore `async`.

**No Ion token** — Natural Earth II uses `Cesium.buildModuleUrl('Assets/Textures/NaturalEarthII')`,
served directly from the Cesium CDN bundle. No Cesium Ion account is needed.

---

## Project Structure
demo2.html ← self-contained demo (HTML + CSS + JS, ~1600 lines)
data/   
CSS_OEM.dat ← Musico orbit data (CCSDS OEM)   
FYBB1.tle ← FYBB#1 TLE (optional)

text

---

## Credits

- Orbit data: space-track, cmse, HKUST Musico mission / FYBB#1 team  
- Basemap tiles: Esri, OpenStreetMap contributors, CARTO  
- HK imagery: Lands Department, HKSAR Government  
- 3D engine: [CesiumJS](https://cesium.com) (Apache 2.0)  
- TLE propagator: [satellite.js](https://github.com/shashwatak/satellite-js) (MIT)
