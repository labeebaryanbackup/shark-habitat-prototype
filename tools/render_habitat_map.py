#!/usr/bin/env python3
"""Render a deterministic habitat-suitability heatmap from the prototype's scoring code."""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automatic_nasa_framework import AutomaticNASAFramework  # noqa: E402


OUTPUT = ROOT / "assets" / "habitat-suitability.svg"
GRID = 25
CELL = 15
HX, HY = 90, 140  # heatmap origin
MAP_SIZE = GRID * CELL
VIRIDIS = (
    (0.00, (68, 1, 84)),
    (0.25, (59, 82, 139)),
    (0.50, (33, 145, 140)),
    (0.75, (94, 201, 98)),
    (1.00, (253, 231, 37)),
)


def _viridis(t: float) -> str:
    t = max(0.0, min(1.0, t))
    for index in range(len(VIRIDIS) - 1):
        t0, c0 = VIRIDIS[index]
        t1, c1 = VIRIDIS[index + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            return "#" + "".join(f"{round(c0[k] + (c1[k] - c0[k]) * f):02x}" for k in range(3))
    return "#fde725"


def render() -> str:
    with contextlib.redirect_stdout(io.StringIO()):
        framework = AutomaticNASAFramework(species="great_white", seed=2339)
        env, _ = framework.auto_download_nasa_data(
            {"name": "California Coast", "bounds": [-125, 32, -115, 42]},
            ["2024-06-01", "2024-08-31"],
        )
        results = framework.advanced_habitat_prediction(env)

    hsi = results["hsi"]  # 25x25, row i = latitude 32..42N
    flat = [value for row in hsi for value in row]
    vmin, vmax = min(flat), max(flat)

    cells = []
    for i in range(GRID):
        for j in range(GRID):
            t = (hsi[i][j] - vmin) / (vmax - vmin) if vmax > vmin else 0.0
            x = HX + j * CELL
            y = HY + (GRID - 1 - i) * CELL  # north up
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{_viridis(t)}"/>')

    bar_x, bar_y, bar_w, bar_h = 520, HY, 26, MAP_SIZE
    steps = 40
    bar_blocks = []
    for k in range(steps):
        t = 1.0 - k / (steps - 1)
        y = bar_y + k * (bar_h / steps)
        bar_blocks.append(
            f'<rect x="{bar_x}" y="{y:.2f}" width="{bar_w}" height="{bar_h / steps + 0.5:.2f}" fill="{_viridis(t)}"/>'
        )

    cbar_ticks = []
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        value = vmin + (vmax - vmin) * frac
        y = bar_y + (1.0 - frac) * bar_h
        cbar_ticks.append(
            f'<path d="M{bar_x} {y:.2f} h{bar_w}" stroke="#7891a3"/>'
            f'<text x="{bar_x + bar_w + 10}" y="{y + 5:.2f}" class="axis">{value:.2f}</text>'
        )

    lat_ticks = []
    for lat in (32, 36, 40):
        i = (lat - 32) / 10 * (GRID - 1)
        y = HY + (GRID - 1 - i) * CELL
        lat_ticks.append(
            f'<path d="M{HX} {y:.2f} h-6" stroke="#7891a3"/>'
            f'<text x="{HX - 10}" y="{y + 5:.2f}" text-anchor="end" class="axis">{lat}°N</text>'
        )

    lon_ticks = []
    for lon in (-125, -120, -115):
        j = (lon + 125) / 10 * (GRID - 1)
        x = HX + j * CELL
        lon_ticks.append(
            f'<path d="M{x:.2f} {HY + MAP_SIZE} v6" stroke="#7891a3"/>'
            f'<text x="{x:.2f}" y="{HY + MAP_SIZE + 24}" text-anchor="middle" class="axis">{abs(lon)}°W</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640" role="img" aria-labelledby="title desc">
  <title id="title">Unvalidated great white shark habitat-suitability heatmap</title>
  <desc id="desc">Heatmap of the prototype habitat-suitability index over a generated 25x25 environmental grid. Software-behaviour visualization, not evidence of shark presence or ecological accuracy.</desc>
  <style>
    .title {{ font: 800 34px system-ui, sans-serif; fill: #11344a; }}
    .subtitle {{ font: 16px system-ui, sans-serif; fill: #547181; }}
    .axis {{ font: 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #547181; }}
    .axis-title {{ font: 700 15px system-ui, sans-serif; fill: #315b70; }}
    .panel-kicker {{ font: 800 13px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; letter-spacing: 2px; fill: #77d6c8; }}
    .panel-title {{ font: 750 21px system-ui, sans-serif; fill: #f1fbff; }}
    .note {{ font: 14px system-ui, sans-serif; fill: #bdd1d9; }}
  </style>
  <rect width="1280" height="640" rx="30" fill="#f3f9fb"/>
  <path d="M0 96 H1280" stroke="#c7dce5"/>
  <text x="56" y="50" class="title">HEURISTIC HABITAT SUITABILITY</text>
  <text x="56" y="78" class="subtitle">Great white shark · generated 25×25 prototype grid · software behaviour, not ecological validation</text>

  <g>
    {''.join(cells)}
    <rect x="{HX}" y="{HY}" width="{MAP_SIZE}" height="{MAP_SIZE}" fill="none" stroke="#7891a3" stroke-width="2"/>
    {''.join(lat_ticks)}
    {''.join(lon_ticks)}
    <text x="{HX + MAP_SIZE / 2:.0f}" y="{HY + MAP_SIZE + 52}" text-anchor="middle" class="axis-title">LONGITUDE</text>
    <text x="26" y="{HY + MAP_SIZE / 2:.0f}" text-anchor="middle" class="axis-title" transform="rotate(-90 26 {HY + MAP_SIZE / 2:.0f})">LATITUDE</text>
    <text x="{bar_x + bar_w / 2:.0f}" y="{bar_y - 12}" text-anchor="middle" class="axis-title">HSI</text>
    {''.join(bar_blocks)}
    {''.join(cbar_ticks)}
  </g>

  <g transform="translate(600 140)">
    <rect width="356" height="375" rx="24" fill="#10384b"/>
    <text x="32" y="43" class="panel-kicker">PROTOTYPE BOUNDARY</text>
    <text x="32" y="77" class="panel-title">What this map means</text>
    <path d="M32 112 H324" stroke="#315b70"/>
    <text x="32" y="146" class="note">✓ 25×25 deterministic grid</text>
    <text x="32" y="175" class="note">✓ current heuristic scoring path</text>
    <text x="32" y="204" class="note">✓ colours show relative HSI only</text>
    <text x="32" y="233" class="note">✕ satellite measurements</text>
    <text x="32" y="262" class="note">✕ evidence of shark presence</text>
    <text x="32" y="320" class="note">Absolute HSI range for this run:</text>
    <text x="32" y="348" class="note">{vmin:.3f} – {vmax:.3f}</text>
  </g>

  <rect x="56" y="600" width="1168" height="1" fill="#c7dce5"/>
  <text x="56" y="624" class="axis">HSI values are unvalidated model outputs. They must not be used for conservation, navigation, or wildlife claims.</text>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when the committed SVG is stale")
    args = parser.parse_args()
    expected = render()

    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale generated asset: {OUTPUT.relative_to(ROOT)}")
        print(f"up to date: {OUTPUT.relative_to(ROOT)}")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
