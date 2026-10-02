"""Shared design tokens and SVG helpers for the profile assets.

Every image in the README is drawn from these tokens, so type, color and spacing
stay consistent across sections and across light and dark mode.
"""
from html import escape

FONT = ("-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Inter', "
        "'Segoe UI Variable Display', 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif")

# Apple's system palette. Light values on the left, dark on the right.
SYSTEM = {
    "blue": ("#007AFF", "#0A84FF"),
    "indigo": ("#5856D6", "#5E5CE6"),
    "purple": ("#AF52DE", "#BF5AF2"),
    "pink": ("#FF2D55", "#FF375F"),
    "orange": ("#FF9500", "#FF9F0A"),
    "green": ("#34C759", "#30D158"),
    "teal": ("#30B0C7", "#40C8E0"),
    "cyan": ("#32ADE6", "#64D2FF"),
    "gray": ("#8E8E93", "#98989D"),
    "gray2": ("#636366", "#48484A"),
}

THEMES = {
    "light": dict(
        name="light", hero="#F5F5F7", tile="#F5F5F7", fill="#E8E8ED", label="#1D1D1F",
        secondary="#6E6E73", tertiary="#86868B", separator="#D2D2D7", accent="#0071E3",
        on_accent="#FFFFFF", glow_opacity="0.55", wash_opacity="0.10", empty="#E3E3E8",
    ),
    "dark": dict(
        name="dark", hero="#000000", tile="#1C1C1E", fill="#2C2C2E", label="#F5F5F7",
        secondary="#A1A1A6", tertiary="#8E8E93", separator="#38383A", accent="#2997FF",
        on_accent="#FFFFFF", glow_opacity="0.75", wash_opacity="0.22", empty="#2C2C2E",
    ),
}


def sys(color, t):
    return SYSTEM[color][0 if t["name"] == "light" else 1]


# Rough per-character advance widths (fraction of an em) for a neo-grotesque
# system face. Good enough to wrap text and size pills without a font engine.
_NARROW = set("il.,:;'|!ìíjI")
_SEMI = set("frt()[]-/  ")
_WIDE = set("mwMW@")


def text_width(text, size, weight=400):
    w = 0.0
    for ch in text:
        if ch in _NARROW:
            w += 0.26
        elif ch in _SEMI:
            w += 0.34
        elif ch in _WIDE:
            w += 0.84
        elif ch.isupper():
            w += 0.66
        elif ch.isdigit():
            w += 0.57
        else:
            w += 0.54
    return w * size * (1.06 if weight >= 600 else 1.0)


def wrap(text, size, max_width, weight=400):
    lines, line = [], ""
    for word in text.split(" "):  # not split(): non-breaking spaces must hold
        if not word:
            continue
        trial = f"{line} {word}" if line else word
        if text_width(trial, size, weight) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def text(x, y, content, size, fill, weight=400, tracking=0.0, anchor="start", cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<text{c} x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{tracking}" text-anchor="{anchor}" fill="{fill}"{extra}>{escape(content)}</text>')


def lines(x, y, rows, size, leading, fill, weight=400, tracking=0.0):
    spans = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else leading}">{escape(r)}</tspan>' for i, r in enumerate(rows))
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{tracking}" fill="{fill}">{spans}</text>')


# Section header shared by every content block: small eyebrow, then a large
# headline with tight tracking (negative tracking grows with size).
HEADER_H = 150


def header(eyebrow, title, t, right=""):
    out = [text(0, 46, eyebrow.upper(), 17, t["tertiary"], 600, 2.4),
           text(0, 112, title, 56, t["label"], 700, -1.8)]
    if right:
        out.append(text(1200, 112, right, 19, t["tertiary"], 500, 0, "end"))
    return "".join(out)




def svg(width, height, label, body, defs="", style=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<defs>{defs}</defs>
<style>text {{ font-family: {FONT}; }}{style}</style>
{body}
</svg>
"""
