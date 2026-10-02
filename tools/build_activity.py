"""Draws the Activity section from public GitHub data.

Runs daily in .github/workflows/activity.yml. Locally:  python tools/build_activity.py
"""
import json
import os
import re
import sys as _sys
import urllib.request
from datetime import date
from pathlib import Path

from design import HEADER_H, THEMES, header, svg, text

USER = os.environ.get("GITHUB_USER", "SasiruVirajith")
OUT = Path(__file__).resolve().parent.parent / "assets"


def fetch(url):
    headers = {"User-Agent": "profile-activity"}
    if os.environ.get("GITHUB_TOKEN") and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return r.read().decode()


def contributions():
    """Returns {(row, col): (date, level, count)} from the public contribution calendar."""
    html = fetch(f"https://github.com/users/{USER}/contributions")
    days = {}
    for m in re.finditer(r'<td[^>]*?data-date="([\d-]+)"[^>]*?id="contribution-day-component-(\d+)-(\d+)"[^>]*?data-level="(\d)"', html):
        d, row, col, level = m.groups()
        days[f"contribution-day-component-{row}-{col}"] = [date.fromisoformat(d), int(row), int(col), int(level), 0]
    for m in re.finditer(r'<tool-tip[^>]*for="(contribution-day-component-\d+-\d+)"[^>]*>(\d+) contributions? on', html):
        if m.group(1) in days:
            days[m.group(1)][4] = int(m.group(2))
    if not days:
        raise SystemExit("No contribution data found; GitHub may have changed the page.")
    return sorted(days.values())


def streaks(days):
    counts = [c for *_, c in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current, i = 0, len(counts) - 1
    if counts and counts[-1] == 0:  # today may simply not have activity yet
        i -= 1
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    return current, longest


def stars():
    repos = json.loads(fetch(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner"))
    return sum(r["stargazers_count"] for r in repos if not r["fork"])


def render(t, days, metrics):
    W = 1200
    top = HEADER_H
    pad = 44
    heat_top = top + 210
    cols = max(col for _, _, col, _, _ in days) + 1
    pitch = (W - 2 * pad) / cols
    cell = pitch - 4.5
    H = heat_top + 7 * pitch + 78

    out = [header("GitHub", "Activity.", t, right="Updated daily"),
           f'<rect x="0" y="{top}" width="{W}" height="{H - top}" rx="36" fill="{t["tile"]}"/>']

    col_w = (W - 2 * pad) / len(metrics)
    for i, (value, unit, label) in enumerate(metrics):
        x = pad + i * col_w
        if i:
            out.append(f'<line x1="{x - 24:.1f}" x2="{x - 24:.1f}" y1="{top + 44}" y2="{top + 132}" stroke="{t["separator"]}"/>')
        color = t["accent"] if i == 0 else t["label"]
        out.append(f'<text x="{x:.1f}" y="{top + 96}" font-size="52" font-weight="700" letter-spacing="-1.6" fill="{color}">{value}'
                   f'<tspan font-size="22" font-weight="600" letter-spacing="0" fill="{t["secondary"]}" dx="6">{unit}</tspan></text>')
        out.append(text(f"{x:.1f}", top + 128, label, 18, t["secondary"], 500))

    # Month labels above the first week that starts in each month.
    seen = set()
    for d, row, col, _, _ in days:
        if row == 0 and d.day <= 7 and d.month not in seen and col < cols - 2:
            seen.add(d.month)
            out.append(text(f"{pad + col * pitch:.1f}", heat_top - 14, d.strftime("%b"), 15, t["tertiary"], 500))

    opacity = {1: 0.28, 2: 0.5, 3: 0.75, 4: 1.0}
    for d, row, col, level, count in days:
        x, y = pad + col * pitch, heat_top + row * pitch
        fill = f'fill="{t["empty"]}"' if level == 0 else f'fill="{t["accent"]}" fill-opacity="{opacity[level]}"'
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="{cell * 0.28:.1f}" {fill}/>')

    # Legend.
    ly = heat_top + 7 * pitch + 30
    lx = W - pad - 5 * (cell + 5) - 44
    out.append(text(f"{lx - 12:.1f}", f"{ly + cell * 0.72:.1f}", "Less", 15, t["tertiary"], 500, 0, "end"))
    for i in range(5):
        fill = f'fill="{t["empty"]}"' if i == 0 else f'fill="{t["accent"]}" fill-opacity="{opacity[i]}"'
        out.append(f'<rect x="{lx + i * (cell + 5):.1f}" y="{ly:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="{cell * 0.28:.1f}" {fill}/>')
    out.append(text(f"{lx + 5 * (cell + 5) + 7:.1f}", f"{ly + cell * 0.72:.1f}", "More", 15, t["tertiary"], 500))
    out.append(text(pad, f"{ly + cell * 0.72:.1f}", f"{days[0][0]:%B %Y} – {days[-1][0]:%B %Y}", 15, t["tertiary"], 500))

    alt = "Activity. " + ", ".join(f"{l}: {v} {u}".strip() for v, u, l in metrics) + "."
    return svg(W, round(H), alt, "".join(out))


def main():
    days = contributions()
    current, longest = streaks(days)
    total = sum(c for *_, c in days)
    try:
        star_count = stars()
    except Exception as e:  # rate limits shouldn't break the whole section
        print(f"stars unavailable: {e}", file=_sys.stderr)
        star_count = None
    day = lambda n: "day" if n == 1 else "days"
    metrics = [(f"{total:,}", "", "Contributions in the last year"),
               (f"{current}", day(current), "Current streak"),
               (f"{longest}", day(longest), "Longest streak")]
    if star_count is not None:
        metrics.append((f"{star_count}", "", "Stars earned"))
    for name, t in THEMES.items():
        (OUT / f"activity-{name}.svg").write_text(render(t, days, metrics), encoding="utf-8")
    print(f"{total} contributions, streak {current}/{longest}, stars {star_count}")


if __name__ == "__main__":
    main()
