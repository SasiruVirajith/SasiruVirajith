"""Builds the static light/dark SVGs used by README.md.

Edit the content below, then run:  python tools/build_assets.py
"""
import base64
import json
import math
import re
from html import escape
from pathlib import Path

from design import HEADER_H, THEMES, header, lines, svg, sys, text, text_width, wrap

OUT = Path(__file__).resolve().parent.parent / "assets"

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
NAME = "Sasiru Virajith"
HELLO = "Hello, I'm"
HEADLINE = "Software. Data. AI."
LENS_WORD = "Data."  # the word the Liquid Glass lens magnifies
TAGLINE = "Software that feels simple. Engineering that isn't."
META = "Colombo, Sri Lanka  ·  University of Westminster"

EMAIL = "virajithsasiru@gmail.com"
FOOTER_EYEBROW = "Got an idea?"
FOOTER_LEAD, FOOTER_ACCENT = "Let's build", "something."  # the accent word is drawn in gradient
FOOTER_LINE = "Always up for a conversation about FinTech, data and AI."

# The About section: a two-tone headline (styled runs: "label" = full contrast, None = gray),
# then a short bio where the "ink" run is drawn in the hero's gradient.
ABOUT_HEADLINE = [
    ("I build software end to end.", "label"),
    (" From the interface people touch to the models and infrastructure behind it.", None),
]
ABOUT_BODY = [
    ("I'm a 19-year-old Software Engineering student at the University of Westminster and "
     "co-founder of Opti5 Labs, based in Colombo. Right now my focus is ", None),
    ("FinTech, AI, data science and MLOps.", "ink"),
]

OPTI5 = dict(
    name="Opti5 Labs.", role="Co-founder", logo="logos/opti5labs.png",
    url="https://www.opti5labs.com/", domain="opti5labs.com",
    body="A technology consultancy building enterprise software, AI integrations and web platforms for international clients.",
    stats=[("25+", "Projects delivered"), ("6", "Service areas")],
)

LINKS = [  # (file slug, label, glyph, primary)
    ("email", "Email", "mail", True),
    ("linkedin", "LinkedIn", "linkedin", False),
    ("x", "X", "x", False),
    ("instagram", "Instagram", "instagram", False),
]

SPECS = [  # (category, glyph, gradient colors, tools). Every tool needs an entry in tools/fetch_icons.py.
    ("Languages", "code", ("blue", "indigo"), ["Python", "TypeScript", "JavaScript", "Java", "Kotlin", "C", "C++", "Dart", "Swift", "Bash"]),
    ("Frontend & Mobile", "window", ("cyan", "blue"), ["React", "Next.js", "Vue", "Tailwind CSS", "Vite", "Redux", "Three.js", "Flutter", "Android"]),
    ("Backend & APIs", "server", ("indigo", "purple"), ["Node.js", "Express", "FastAPI", "Django", "Flask", "Spring Boot", "GraphQL", "Socket.IO"]),
    ("Data Science", "chart", ("orange", "pink"), ["pandas", "NumPy", "SciPy", "Polars", "Matplotlib", "Seaborn", "Plotly", "Jupyter", "Power BI"]),
    ("Machine Learning", "sparkle", ("purple", "pink"), ["PyTorch", "TensorFlow", "Keras", "scikit-learn", "XGBoost", "LightGBM", "Hugging Face", "OpenCV", "LangChain"]),
    ("MLOps", "loop", ("pink", "orange"), ["MLflow", "DVC", "Airflow", "Kubeflow", "Weights & Biases", "BentoML", "ONNX"]),
    ("Databases", "cylinder", ("green", "teal"), ["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Supabase", "Firebase", "Prisma"]),
    ("Cloud & DevOps", "cloud", ("cyan", "teal"), ["AWS", "Google Cloud", "Azure", "Vercel", "Cloudflare", "Docker", "Kubernetes", "GitHub Actions", "Linux"]),
    ("Tools", "sliders", ("gray", "gray2"), ["Git", "GitHub", "VS Code", "IntelliJ IDEA", "Postman", "Figma", "Notion"]),
]
ICONS = json.loads((Path(__file__).with_name("icons.json")).read_text(encoding="utf-8"))

FEATURED = dict(
    slug="world-cup-predictor", colors=("green", "teal"),
    eyebrow="Machine Learning  ·  Sports Analytics",
    title=["FIFA World Cup 2026", "Predictor."],
    body="A Gradient Boosting match model, simulated across the entire tournament with Monte Carlo, plus Golden Boot, Glove and Ball predictions.",
    stats=[("25,000+", "Fixtures trained on"), ("Monte Carlo", "Full-tournament sim"), ("3", "Award predictions")],
)

PROJECTS = [
    dict(slug="optilearn", logo="logos/optilearn.png", color="blue",
         website="https://opti-learn.com/", domain="opti-learn.com", repo="OptiLearn",
         eyebrow="EdTech  ·  On-device AI", title="OptiLearn.",
         body="An offline-first, multilingual learning platform for underserved classrooms. One teacher laptop becomes a local AI learning server.",
         features=["Works with no internet", "Multilingual tutoring and translation", "Powered by Gemma 4"]),
    dict(slug="opticonvo", logo="logos/opticonvo.png", color="green",
         website="https://opticonvo.vercel.app/", domain="opticonvo.vercel.app", repo="OptiConvo",
         eyebrow="Conversational AI", title="OptiConvo.",
         body="Rehearse high-stakes conversations with real-time, photorealistic AI avatars, from job interviews to investor pitches.",
         features=["Live avatars with voice and lip-sync", "30+ languages", "14 built-in personas"]),
]

# ---------------------------------------------------------------------------
# Glyphs (24px grid, drawn in currentColor-style via the fill argument)
# ---------------------------------------------------------------------------
X_PATH = ("M714.163 519.284 1160.89 0h-105.86L667.137 450.887 357.328 0H0l468.492 681.821L0 1226.37h105.866"
          "l409.625-476.152 327.181 476.152H1200L714.137 519.284h.026ZM569.165 687.828l-47.468-67.894-377.686"
          "-540.24h162.604l304.797 435.991 47.468 67.894 396.2 566.721H892.476L569.165 687.854v-.026Z")


def glyph(kind, color, bg="none"):
    sw = 'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'.format(c=color)
    if kind == "code":
        return f'<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M13.5 4.5l-3 15" {sw}/>'
    if kind == "window":
        return (f'<rect x="2.5" y="4" width="19" height="16" rx="3.5" {sw}/><path d="M2.5 9h19" {sw}/>'
                f'<circle cx="5.6" cy="6.6" r="0.9" fill="{color}"/><circle cx="8.3" cy="6.6" r="0.9" fill="{color}"/>')
    if kind == "server":
        return (f'<rect x="3" y="3.5" width="18" height="7" rx="2.5" {sw}/><rect x="3" y="13.5" width="18" height="7" rx="2.5" {sw}/>'
                f'<circle cx="7" cy="7" r="1.1" fill="{color}"/><circle cx="7" cy="17" r="1.1" fill="{color}"/>')
    if kind == "chart":
        return (f'<rect x="3.5" y="12" width="4" height="8.5" rx="1.4" fill="{color}"/><rect x="10" y="7" width="4" height="13.5" rx="1.4" fill="{color}"/>'
                f'<rect x="16.5" y="3.5" width="4" height="17" rx="1.4" fill="{color}"/>')
    if kind == "sparkle":
        return (f'<path d="M10 2.5c.6 4.6 2.9 6.9 7.5 7.5-4.6.6-6.9 2.9-7.5 7.5-.6-4.6-2.9-6.9-7.5-7.5 4.6-.6 6.9-2.9 7.5-7.5z" fill="{color}"/>'
                f'<path d="M18 14c.3 2.3 1.4 3.4 3.7 3.7-2.3.3-3.4 1.4-3.7 3.7-.3-2.3-1.4-3.4-3.7-3.7 2.3-.3 3.4-1.4 3.7-3.7z" fill="{color}"/>')
    if kind == "loop":
        return (f'<path d="M20 12a8 8 0 0 1-14.3 4.9M4 12A8 8 0 0 1 18.3 7.1" {sw}/>'
                f'<path d="M18.8 3.2v4.3h-4.3M5.2 20.8v-4.3h4.3" {sw}/>')
    if kind == "cylinder":
        return (f'<ellipse cx="12" cy="5.5" rx="8" ry="3" {sw}/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13" {sw}/>'
                f'<path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" {sw}/>')
    if kind == "cloud":
        return f'<path d="M7 19a4.5 4.5 0 0 1-.6-9 6 6 0 0 1 11.5 1.3A3.9 3.9 0 0 1 17.5 19z" fill="{color}"/>'
    if kind == "sliders":
        return (f'<path d="M4 7h16M4 17h16" {sw}/><circle cx="9" cy="7" r="2.6" fill="{color}"/>'
                f'<circle cx="15.5" cy="17" r="2.6" fill="{color}"/>')
    if kind == "mail":
        return (f'<rect x="2" y="4.5" width="20" height="15" rx="3.5" fill="none" stroke="{color}" stroke-width="2"/>'
                f'<path d="M3.5 7l8.5 6 8.5-6" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    if kind == "linkedin":
        return (f'<rect x="2.5" y="2.5" width="19" height="19" rx="5" fill="none" stroke="{color}" stroke-width="2"/>'
                f'<path d="M8 10.5V17M12 17v-6.5M12 13.4c0-1.8 1.1-2.9 2.6-2.9s2.4 1 2.4 2.9V17" fill="none" stroke="{color}" '
                f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="8" cy="7.4" r="1.25" fill="{color}"/>')
    if kind == "x":
        return (f'<path transform="translate(2.6 2.8) scale(0.0157)" fill="{color}" stroke="{color}" '
                f'stroke-width="40" stroke-linejoin="round" d="{X_PATH}"/>')
    if kind == "instagram":
        return (f'<rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="{color}" stroke-width="2"/>'
                f'<circle cx="12" cy="12" r="4.3" fill="none" stroke="{color}" stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.3" fill="{color}"/>')
    raise ValueError(kind)


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------
def hero(t):
    """Keynote typography on a plain canvas, with one Liquid Glass lens magnifying the content
    beneath it: brighter, slightly larger, with a hint of chromatic dispersion at the edges."""
    W, H = 1200, 580
    dark = t["name"] == "dark"
    bg = "#000000" if dark else "#FFFFFF"
    ai = [sys("blue", t), sys("purple", t), sys("pink", t), sys("orange", t)]
    stops = "".join(f'<stop offset="{i / 3:.2f}" stop-color="{c}"/>' for i, c in enumerate(ai))
    # Lay the headline out word by word so the lens can be centred on LENS_WORD exactly:
    # that word is drawn with text-anchor="middle" at the lens centre, so estimate errors
    # (system fonts differ) only nudge the spacing, never the lens alignment.
    k = 0.86  # estimate-to-rendered ratio for bold display sizes
    space = 26
    words, x = [], 76
    for wd in HEADLINE.split(" "):
        w = text_width(wd, 96, 700) * k
        clear = (w * 0.2 + 64) / 2 + 22 if wd == LENS_WORD else 0  # keep neighbours out from under the glass
        x += clear - (space if clear and words else 0) if clear else 0
        words.append((wd, x, w))
        x += w + (clear if clear else space)
    lens_word = next(w for w in words if w[0] == LENS_WORD)
    word_mid = lens_word[1] + lens_word[2] / 2
    lw, lh = lens_word[2] * 1.2 + 64, 128
    lx, ly = word_mid - lw / 2, 290
    headline = "".join(
        text(f"{word_mid:.1f}", 380, wd, 96, "url(#ink)", 700, -3.8, "middle") if wd == LENS_WORD
        else text(f"{wx:.1f}", 380, wd, 96, "url(#ink)", 700, -3.8)
        for wd, wx, _ in words)
    cx, cy = lx + lw / 2, ly + lh / 2
    mag = f"translate({cx} {cy}) scale(1.2) translate({-cx} {-cy})"

    def tint(hex_):
        r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
        return f"0 0 0 0 {r:.3f}  0 0 0 0 {g:.3f}  0 0 0 0 {b:.3f}  0 0 0 1 0"

    defs = f"""
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="80" y1="0" x2="980" y2="0">{stops}</linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="40"/></clipPath>
  <clipPath id="lens"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="{lh / 2}"/></clipPath>
  <filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="55"/></filter>
  <filter id="rim" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="7"/></filter>
  <filter id="lift" x="-30%" y="-40%" width="160%" height="200%"><feDropShadow dx="0" dy="18" stdDeviation="22" flood-color="#000" flood-opacity="{0.6 if dark else 0.16}"/></filter>
  <filter id="blue" x="0" y="0" width="100%" height="100%"><feColorMatrix type="matrix" values="{tint(sys('blue', t))}"/></filter>
  <filter id="pink" x="0" y="0" width="100%" height="100%"><feColorMatrix type="matrix" values="{tint(sys('pink', t))}"/></filter>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="0.3" stop-color="#fff" stop-opacity="0.15"/>
    <stop offset="0.7" stop-color="#fff" stop-opacity="0.05"/><stop offset="1" stop-color="#fff" stop-opacity="0.75"/>
  </linearGradient>
  <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="{0.1 if dark else 0.55}"/><stop offset="0.5" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="top" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="{0.7 if dark else 0.9}"/><stop offset="0.3" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.85" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="{0.25 if dark else 0.4}"/>
  </linearGradient>
  <g id="glowfield" filter="url(#glow)">
    <circle cx="{cx - 70}" cy="{cy + 30}" r="110" fill="{ai[0]}"/>
    <circle cx="{cx + 80}" cy="{cy - 20}" r="100" fill="{ai[1]}"/>
    <circle cx="{cx + 20}" cy="{cy + 80}" r="80" fill="{ai[2]}"/>
  </g>
  <g id="type">
    {text(80, 138, HELLO, 34, t['secondary'], 600, -0.5)}
    {text(74, 254, NAME + '.', 124, t['label'], 700, -5)}
    {headline}
  </g>"""
    body = f"""
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{bg}"/>
  <use href="#glowfield" opacity="{0.2 if dark else 0.16}"/>
  <use href="#type"/>
  <!-- TAGLINE: edit the line below (and in the other theme's file), or change TAGLINE in tools/build_assets.py -->
  {text(80, 452, TAGLINE, 28, t['secondary'], 500, -0.4)}
  {text(80, 500, META, 20, t['tertiary'], 500)}

  <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="{lh / 2}" fill="{bg}" filter="url(#lift)"/>
  <g clip-path="url(#lens)">
    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="{bg}"/>
    <use href="#glowfield" transform="{mag}" opacity="{0.2 if dark else 0.3}"/>
    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="#fff" fill-opacity="{0.06 if dark else 0}"/>
    <g transform="{mag}">
      <use href="#type" filter="url(#blue)" opacity="{0.28 if dark else 0.5}" x="{-2 if dark else -3}"/>
      <use href="#type" filter="url(#pink)" opacity="{0.28 if dark else 0.5}" x="{2 if dark else 3}"/>
      <use href="#type"/>
    </g>
    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="url(#sheen)"/>
    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="{lh / 2}" fill="none" stroke="#fff" stroke-opacity="{0.14 if dark else 0.85}" stroke-width="{12 if dark else 16}" filter="url(#rim)"/>
  </g>
  <rect x="{lx + 1.5}" y="{ly + 1.5}" width="{lw - 3}" height="{lh - 3}" rx="{lh / 2 - 1.5}" fill="none" stroke="url(#top)" stroke-width="1.5"/>
  <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="{lh / 2}" fill="none" stroke="url(#edge)" stroke-width="{1.5 if dark else 2}"/>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="39.5" fill="none" stroke="{t['separator']}" stroke-opacity="0.8"/>
"""
    alt = f"{HELLO} {NAME}. {HEADLINE} {TAGLINE} {META}"
    return svg(W, H, alt, body, defs)


def rich_lines(runs, size, weight, max_width, k=0.88):
    """Wraps styled runs [(text, style)] into rows of words; a word may mix styles
    ("cloud" + ","). An "ink" (gradient) run never breaks across lines."""
    words, current = [], []
    for content, style in runs:
        if style == "ink":
            content = content.replace(" ", " ")
        for piece in re.findall(r"[^ ]+| +", content):  # split on plain spaces only
            if piece.startswith(" "):
                if current:
                    words.append(current)
                    current = []
            else:
                current.append((piece, style))
    if current:
        words.append(current)
    space = text_width(" ", size, weight) * k
    rows, row, width = [], [], 0.0
    for word in words:
        w = sum(text_width(s, size, weight) * k for s, _ in word)
        if row and width + space + w > max_width:
            rows.append(row)
            row, width = [], 0.0
        width += (space if row else 0) + w
        row.append(word)
    rows.append(row)
    return rows


def rich_text(rows, x, y, size, weight, leading, tracking, fills):
    out = []
    for row in rows:
        spans = []
        for i, word in enumerate(row):
            for j, (s, style) in enumerate(word):
                lead = " " if i and j == 0 else ""
                spans.append(f'<tspan fill="{fills[style]}">{escape(lead + s)}</tspan>')
        out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" letter-spacing="{tracking}" '
                   f'style="white-space: pre">{"".join(spans)}</text>')
        y += leading
    return "".join(out), y - leading


def about(t):
    """Apple's two-tone statement: the point in full contrast, the rest in gray,
    then a short bio with the focus areas in the hero's gradient."""
    W = 1200
    ai = [sys("blue", t), sys("purple", t), sys("pink", t), sys("orange", t)]
    stops = "".join(f'<stop offset="{i / 3:.2f}" stop-color="{c}"/>' for i, c in enumerate(ai))
    fills = {"label": t["label"], None: t["tertiary"], "ink": "url(#ink)", "body": t["secondary"]}

    head_rows = rich_lines(ABOUT_HEADLINE, 50, 700, W - 40)
    head, y = rich_text(head_rows, 0, 128, 50, 700, 62, -1.6, fills)
    body_runs = [(s, st or "body") for s, st in ABOUT_BODY]
    body_rows = rich_lines(body_runs, 26, 500, 940)
    body, y = rich_text(body_rows, 0, y + 70, 26, 500, 40, -0.3, fills)

    # The gradient spans the line the focus phrase lands on.
    defs = f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="940" y2="0">{stops}</linearGradient>'
    out = [text(0, 46, "ABOUT", 17, t["tertiary"], 600, 2.4), head, body]
    plain = "".join(s for s, _ in ABOUT_HEADLINE) + " " + "".join(s for s, _ in ABOUT_BODY)
    return svg(W, round(y + 26), plain, "".join(out), defs)


def company_card(t):
    """Opti5 Labs: logo, role, one line on what the company does, and its track record."""
    W, H = 1200, 310
    c = OPTI5
    logo = base64.b64encode((OUT / c["logo"]).read_bytes()).decode()
    orange = sys("orange", t)
    out = [f'<rect width="{W}" height="{H}" rx="36" fill="{t["tile"]}"/>',
           f'<rect x="44" y="49" width="212" height="212" rx="40" fill="#000000"/>',  # the mark is drawn for a dark ground
           f'<image href="data:image/png;base64,{logo}" x="72" y="69" width="156" height="170" preserveAspectRatio="xMidYMid meet"/>',
           text(304, 92, c["role"].upper(), 15, orange, 700, 1.8),
           text(302, 150, c["name"], 48, t["label"], 700, -1.6)]
    body = wrap(c["body"], 21, 600)
    out.append(lines(304, 196, body, 21, 31, t["secondary"]))
    out.append(text(304, 196 + 31 * (len(body) - 1) + 46, c["domain"] + "  ↗", 19, t["accent"], 600))
    out.append(f'<line x1="880" x2="880" y1="69" y2="241" stroke="{t["separator"]}"/>')
    for i, (value, label) in enumerate(c["stats"]):
        y = 132 + i * 96
        out.append(text(920, y, value, 44, t["label"], 700, -1.4))
        out.append(text(920, y + 28, label, 17, t["tertiary"], 500))
    alt = f'{c["role"]}, {c["name"]}. {c["body"]} ' + " ".join(f"{v} {l}." for v, l in c["stats"])
    return svg(W, H, alt, "".join(out))


def button(label, kind, primary, t):
    """HIG capsule button: drawn 56 tall so it displays at 44pt (the minimum tap target),
    label near 17pt on screen, symbol and label optically centred with equal side padding."""
    H, size, icon, pad, gap = 56, 21, 23, 24, 10
    w = pad + icon + gap + text_width(label, size, 600) * 0.9 + pad
    bg = "#0071E3" if primary else t["fill"]  # Apple's button blue: 4.6:1 with white in both themes
    fg = "#FFFFFF" if primary else t["label"]
    s = icon / 24
    body = (f'<rect width="{w:.0f}" height="{H}" rx="{H / 2}" fill="{bg}"/>'
            f'<g transform="translate({pad} {(H - icon) / 2}) scale({s:.3f})">{glyph(kind, fg, bg)}</g>'
            + text(pad + icon + gap, H / 2 + size * 0.36, label, size, fg, 600, -0.2))
    return svg(round(w), H, label, body)


def section_header(eyebrow_s, title, t, right=""):
    return svg(1200, HEADER_H - 10, title, header(eyebrow_s, title, t, right))


def pitch_ball_icon(x, y, size):
    """iOS 26-style app icon: a vivid pitch-green tile with faint markings, and a single
    SF Symbol-like soccer ball rendered as a frosted glass layer with a specular rim."""
    S = size
    cx, cy = x + S / 2, y + S / 2
    R = S * 0.3
    rx = S * 0.2257
    deep = "#0A8F4E"

    def pentagon(px, py, r, rot):
        pts = " ".join(f"{px + r * math.cos(math.radians(rot + 72 * k)):.2f},{py + r * math.sin(math.radians(rot + 72 * k)):.2f}"
                       for k in range(5))
        return f'<polygon points="{pts}" stroke-linejoin="round"/>'

    panels, seams = [pentagon(cx, cy, R * 0.32, -90)], []
    for k in range(5):
        a = -90 + 72 * k
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        d, r = R * 1.0, R * 0.36
        panels.append(pentagon(cx + d * ca, cy + d * sa, r, a + 180))
        seams.append(f'<line x1="{cx + R * 0.32 * ca:.2f}" y1="{cy + R * 0.32 * sa:.2f}" '
                     f'x2="{cx + (d - r) * ca:.2f}" y2="{cy + (d - r) * sa:.2f}"/>')
    return f"""
<defs>
  <linearGradient id="pitch" x1="0.15" y1="0" x2="0.85" y2="1">
    <stop offset="0" stop-color="#5BE37D"/><stop offset="0.55" stop-color="#1FB85F"/><stop offset="1" stop-color="#078A63"/>
  </linearGradient>
  <linearGradient id="frost" x1="0.2" y1="0" x2="0.8" y2="1">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.98"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0.78"/>
  </linearGradient>
  <linearGradient id="spec" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="0.45" stop-color="#fff" stop-opacity="0.2"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0.7"/>
  </linearGradient>
  <linearGradient id="tileEdge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0.6"/><stop offset="0.4" stop-color="#fff" stop-opacity="0.08"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0.25"/>
  </linearGradient>
  <clipPath id="tile"><rect x="{x}" y="{y}" width="{S}" height="{S}" rx="{rx:.1f}"/></clipPath>
  <clipPath id="ball"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}"/></clipPath>
  <filter id="depth" x="-40%" y="-40%" width="180%" height="190%"><feDropShadow dx="0" dy="{S * 0.04:.1f}" stdDeviation="{S * 0.045:.1f}" flood-color="#00331C" flood-opacity="0.45"/></filter>
  <filter id="iconLift" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="14" stdDeviation="16" flood-color="#00331C" flood-opacity="0.3"/></filter>
</defs>
<rect x="{x}" y="{y}" width="{S}" height="{S}" rx="{rx:.1f}" fill="url(#pitch)" filter="url(#iconLift)"/>
<g clip-path="url(#tile)" fill="none" stroke="#FFFFFF" stroke-opacity="0.16" stroke-width="{S * 0.014:.1f}">
  <line x1="{cx:.1f}" y1="{y}" x2="{cx:.1f}" y2="{y + S}"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{S * 0.42:.1f}"/>
</g>
<rect x="{x + 0.75}" y="{y + 0.75}" width="{S - 1.5}" height="{S - 1.5}" rx="{rx - 0.75:.1f}" fill="none" stroke="url(#tileEdge)" stroke-width="1.5"/>
<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="url(#frost)" filter="url(#depth)"/>
<g clip-path="url(#ball)">
  <g fill="{deep}" fill-opacity="0.9" stroke="{deep}" stroke-opacity="0.9" stroke-width="{S * 0.012:.1f}">{''.join(panels)}</g>
  <g stroke="{deep}" stroke-opacity="0.75" stroke-width="{S * 0.016:.1f}" stroke-linecap="round">{''.join(seams)}</g>
</g>
<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R - 0.8:.1f}" fill="none" stroke="url(#spec)" stroke-width="1.6"/>
"""

def featured_card(p, t):
    W, H = 1200, 520
    out = [f'<rect width="{W}" height="{H}" rx="36" fill="{t["tile"]}"/>']
    # Decorative simulation field on the right: dots fading out from a bright core.
    c1, c2 = sys(p["colors"][0], t), sys(p["colors"][1], t)
    out.append(f'<defs><radialGradient id="field" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{c1}" stop-opacity="0.9"/>'
               f'<stop offset="0.6" stop-color="{c2}" stop-opacity="0.35"/><stop offset="1" stop-color="{c2}" stop-opacity="0"/></radialGradient>'
               f'<mask id="dots"><rect width="{W}" height="{H}" fill="#000"/>')
    for row in range(17):
        for col in range(17):
            out.append(f'<circle cx="{690 + col * 27}" cy="{44 + row * 27}" r="7.5" fill="#fff"/>')
    out.append('</mask></defs>')
    out.append('<rect x="660" y="10" width="500" height="500" fill="url(#field)" mask="url(#dots)"/>')
    out.append(pitch_ball_icon(860, 180, 160))

    out.append(text(56, 92, p["eyebrow"].upper(), 15, t["tertiary"], 600, 1.8))
    out.append(lines(56, 158, p["title"], 54, 60, t["label"], 700, -1.8))
    out.append(lines(56, 268, wrap(p["body"], 21, 540), 21, 31, t["secondary"]))
    sx = 56
    for value, label in p["stats"]:
        out.append(text(sx, 420, value, 30, t["label"], 700, -0.6))
        out.append(text(sx, 448, label, 16, t["tertiary"], 500))
        sx += max(text_width(value, 30, 700), text_width(label, 16)) + 44
    out.append(text(56, 486, "View on GitHub  ›", 19, t["accent"], 600))
    alt = " ".join(p["title"]) + " " + p["body"]
    return svg(W, H, alt, "".join(out))


# The two half-width cards and the four link pills below them sit edge to edge in the
# README (each image exactly 50% / 25% wide, no whitespace), so the gutters are drawn
# inside the images. Everything then lines up with the full-width card above at any width.
GUTTER = 32  # matches the vertical gap GitHub puts between stacked images
CELL = 600


def project_card(p, t, side):
    W, H = CELL - GUTTER / 2, 540
    ox = 0 if side == 0 else GUTTER / 2
    logo = base64.b64encode((OUT / p["logo"]).read_bytes()).decode()
    out = [f'<rect width="{W}" height="{H}" rx="36" fill="{t["tile"]}"/>',
           f'<image href="data:image/png;base64,{logo}" x="34" y="30" width="112" height="112"/>',
           text(W - 44, 74, p["domain"], 16, t["tertiary"], 500, 0, "end")]
    out.append(text(48, 186, p["eyebrow"].upper(), 15, t["tertiary"], 600, 1.8))
    out.append(text(48, 242, p["title"], 46, t["label"], 700, -1.4))
    body = wrap(p["body"], 21, W - 96)
    out.append(lines(48, 294, body, 21, 31, t["secondary"]))
    y = 294 + 31 * (len(body) - 1) + 54
    color = sys(p["color"], t)
    for f in p["features"]:
        out.append(f'<circle cx="56" cy="{y - 6}" r="4" fill="{color}"/>')
        out.append(text(74, y, f, 19, t["label"], 500))
        y += 33
    return svg(CELL, H, p["title"] + " " + p["body"], f'<g transform="translate({ox} 0)">{"".join(out)}</g>')


def link_pill(label, kind, t, slot):
    """One of four controls under the two half cards. `slot` 0-3 is its quarter of the row;
    each card's width is split into two pills with a gutter between them."""
    cell, H = CELL / 2, 64
    W = (CELL - GUTTER / 2 - GUTTER) / 2                     # two pills + one gutter = a card's width
    card_x = 0 if slot < 2 else CELL + GUTTER / 2            # where this pill's card starts in the row
    x = card_x + (slot % 2) * (W + GUTTER) - slot * cell     # convert row position to this cell
    color = t["accent"] if kind == "web" else t["label"]
    icon = (f'<circle cx="12" cy="12" r="9" fill="none" stroke="{color}" stroke-width="1.8"/>'
            f'<path d="M3 12h18M12 3c2.6 2.6 3.8 5.6 3.8 9s-1.2 6.4-3.8 9c-2.6-2.6-3.8-5.6-3.8-9S9.4 5.6 12 3z" fill="none" stroke="{color}" stroke-width="1.8"/>'
            if kind == "web" else f'<path fill="{color}" d="{ICONS["GitHub"]["path"]}"/>')
    tw = 24 + 10 + text_width(label, 19, 600) * 0.9
    x0 = x + (W - tw) / 2
    body = (f'<rect x="{x:.1f}" width="{W:.1f}" height="{H}" rx="{H / 2}" fill="{t["tile"]}"/>'
            f'<g transform="translate({x0:.1f} 20)">{icon}</g>'
            + text(f"{x0 + 34:.1f}", H / 2 + 7, label, 19, color, 600, -0.1))
    return svg(cell, H, label, body)


def _lum(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def bubble(name, bx, by, size, t):
    """One watch-style app bubble: brand-colored circle, white (or dark) logo, soft top sheen."""
    icon = ICONS[name]
    fill = "#" + icon["hex"]
    if t["name"] == "dark" and _lum(icon["hex"]) < 0.06:
        fill = "#3A3A3C"
    ink = "#1D1D1F" if _lum(icon["hex"]) > 0.6 else "#FFFFFF"
    out = [f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{size / 2:.1f}" fill="{fill}"/>']
    if "path" in icon:
        g = size * 0.54
        out.append(f'<path transform="translate({bx - g / 2:.1f} {by - g / 2:.1f}) scale({g / 24:.3f})" fill="{ink}" d="{icon["path"]}"/>')
    else:
        fs = size * (0.36 if len(icon["monogram"]) > 2 else 0.42)
        out.append(text(f"{bx:.1f}", f"{by + fs * 0.36:.1f}", icon["monogram"], f"{fs:.1f}", ink, 700, -0.3, "middle"))
    out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{size / 2:.1f}" fill="url(#shine)"/>')
    return "".join(out)


def specs(t):
    """Nine Apple Watch-style clusters: the category icon in the middle, its tools orbiting it,
    and the tool names written underneath so nothing depends on recognising a logo."""
    W, cols, gap = 1200, 3, 20
    tile_w = (W - gap * (cols - 1)) / cols
    d = 60                                     # tool bubble diameter
    most = max(len(items) for _, _, _, items in SPECS)
    orbit = most * (d + 12) / (2 * math.pi)    # same orbit for every tile, sized for the fullest one
    core = orbit - d / 2 - 12
    reach = orbit + d / 2

    total = sum(len(items) for *_, items in SPECS)
    out = [header("Toolbox", "Tech stack.", t, right=f"{total} tools"),
           '<defs><radialGradient id="shine" cx="0.5" cy="0.12" r="0.85">'
           '<stop offset="0" stop-color="#fff" stop-opacity="0.4"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.06"/>'
           '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>']

    y = HEADER_H
    for r in range(0, len(SPECS), cols):
        row = SPECS[r:r + cols]
        wrapped = []
        for *_, items in row:
            joined = "  ·  ".join(i.replace(" ", " ") for i in items)
            wrapped.append([x.rstrip(" ·") for x in wrap(joined, 20, tile_w - 56)])
        cluster_top = 36
        title_y = cluster_top + 2 * reach + 52
        tile_h = title_y + 22 + 30 * max(len(w) for w in wrapped) + 22
        for c, ((title, glyph_kind, colors, items), names) in enumerate(zip(row, wrapped)):
            x = c * (tile_w + gap)
            cx, cy = x + tile_w / 2, y + cluster_top + reach
            gid = f"core{r + c}"
            a, b = sys(colors[0], t), sys(colors[1], t)
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{tile_w:.1f}" height="{tile_h:.0f}" rx="30" fill="{t["tile"]}"/>')
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{orbit:.1f}" fill="none" stroke="{a}" stroke-opacity="0.22" stroke-width="2"/>')
            out.append(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/>'
                       f'<stop offset="1" stop-color="{b}"/></linearGradient></defs>'
                       f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{core:.1f}" fill="url(#{gid})"/>'
                       f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{core:.1f}" fill="url(#shine)"/>')
            gs = core * 0.95
            out.append(f'<g transform="translate({cx - gs / 2:.1f} {cy - gs / 2:.1f}) scale({gs / 24:.3f})">{glyph(glyph_kind, "#FFFFFF", a)}</g>')
            for i, name in enumerate(items):
                ang = -math.pi / 2 + 2 * math.pi * i / len(items)
                out.append(bubble(name, cx + orbit * math.cos(ang), cy + orbit * math.sin(ang), d, t))
            out.append(text(f"{cx:.1f}", y + title_y, title, 26, t["label"], 700, -0.5, "middle"))
            spans = "".join(f'<tspan x="{cx:.1f}" dy="{0 if k == 0 else 30}">{escape(n)}</tspan>' for k, n in enumerate(names))
            out.append(f'<text x="{cx:.1f}" y="{y + title_y + 38}" font-size="20" font-weight="500" '
                       f'text-anchor="middle" fill="{t["secondary"]}">{spans}</text>')
        y += tile_h + gap
    alt = "Tech stack. " + " ".join(f"{a}: {', '.join(i)}." for a, _, _, i in SPECS)
    return svg(W, round(y - gap + 4), alt, "".join(out))


def footer(t):
    """Bookends the hero: same canvas and type, with the email as a Liquid Glass button."""
    W, H = 1200, 490
    dark = t["name"] == "dark"
    bg = "#000000" if dark else "#FFFFFF"
    ai = [sys("blue", t), sys("purple", t), sys("pink", t), sys("orange", t)]
    stops = "".join(f'<stop offset="{i / 3:.2f}" stop-color="{c}"/>' for i, c in enumerate(ai))

    label = EMAIL
    size = 28
    bw = 34 + 26 + 16 + text_width(label, size, 600) * 0.9 + 30 + 34
    bh = 84
    bx, by = 80, 326
    cx, cy = bx + bw / 2, by + bh / 2
    mag = f"translate({cx} {cy}) scale(1.15) translate({-cx} {-cy})"
    lead = text_width(FOOTER_LEAD + " ", 100, 700) * 0.86 + 6

    defs = f"""
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{80 + lead:.0f}" y1="0" x2="{80 + lead + 500:.0f}" y2="0">{stops}</linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="40"/></clipPath>
  <clipPath id="btn"><rect x="{bx}" y="{by}" width="{bw:.1f}" height="{bh}" rx="{bh / 2}"/></clipPath>
  <filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="50"/></filter>
  <filter id="rim" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="lift" x="-30%" y="-40%" width="160%" height="200%"><feDropShadow dx="0" dy="16" stdDeviation="20" flood-color="#000" flood-opacity="{0.6 if dark else 0.14}"/></filter>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="0.3" stop-color="#fff" stop-opacity="0.15"/>
    <stop offset="0.7" stop-color="#fff" stop-opacity="0.05"/><stop offset="1" stop-color="#fff" stop-opacity="0.75"/>
  </linearGradient>
  <linearGradient id="top" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="{0.4 if dark else 0.9}"/><stop offset="0.3" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.85" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="{0.25 if dark else 0.4}"/>
  </linearGradient>
  <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="{0.035 if dark else 0.55}"/><stop offset="0.5" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <g id="glowfield" filter="url(#glow)">
    <circle cx="{bx + bw * 0.25:.0f}" cy="{cy + 20:.0f}" r="100" fill="{ai[0]}"/>
    <circle cx="{bx + bw * 0.6:.0f}" cy="{cy - 10:.0f}" r="95" fill="{ai[1]}"/>
    <circle cx="{bx + bw * 0.9:.0f}" cy="{cy + 30:.0f}" r="80" fill="{ai[2]}"/>
  </g>"""

    icon = f'<g transform="translate({bx + 34} {cy - 13}) scale(1.08)">{glyph("mail", t["label"])}</g>'
    body = f"""
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{bg}"/>
  <use href="#glowfield" opacity="{0.22 if dark else 0.14}"/>
  {text(80, 112, FOOTER_EYEBROW, 34, t['secondary'], 600, -0.5)}
  <text x="74" y="222" font-size="100" font-weight="700" letter-spacing="-4">
    <tspan fill="{t['label']}">{escape(FOOTER_LEAD)} </tspan><tspan fill="url(#ink)">{escape(FOOTER_ACCENT)}</tspan>
  </text>
  {text(80, 282, FOOTER_LINE, 26, t['secondary'], 500, -0.3)}

  <rect x="{bx}" y="{by}" width="{bw:.1f}" height="{bh}" rx="{bh / 2}" fill="{bg}" filter="url(#lift)"/>
  <g clip-path="url(#btn)">
    <rect x="{bx}" y="{by}" width="{bw:.1f}" height="{bh}" fill="{bg}"/>
    <use href="#glowfield" transform="{mag}" opacity="{0.38 if dark else 0.3}"/>
    <rect x="{bx}" y="{by}" width="{bw:.1f}" height="{bh}" fill="#fff" fill-opacity="{0.015 if dark else 0.35}"/>
    <rect x="{bx}" y="{by}" width="{bw:.1f}" height="{bh}" fill="url(#sheen)"/>
    <rect x="{bx}" y="{by}" width="{bw:.1f}" height="{bh}" rx="{bh / 2}" fill="none" stroke="#fff" stroke-opacity="{0.05 if dark else 0.85}" stroke-width="{10 if dark else 16}" filter="url(#rim)"/>
  </g>
  <rect x="{bx + 1.5}" y="{by + 1.5}" width="{bw - 3:.1f}" height="{bh - 3}" rx="{bh / 2 - 1.5}" fill="none" stroke="url(#top)" stroke-width="1.5"/>
  <rect x="{bx}" y="{by}" width="{bw:.1f}" height="{bh}" rx="{bh / 2}" fill="none" stroke="url(#edge)" stroke-width="{1.5 if dark else 2}" stroke-opacity="{0.55 if dark else 1}"/>
  {icon}
  {text(bx + 34 + 26 + 16, cy + size * 0.36, label, size, t['label'], 600, -0.4)}
  {text(f"{bx + bw - 34:.1f}", cy + size * 0.36, '›', size + 4, t['secondary'], 500, 0, 'end')}
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="39.5" fill="none" stroke="{t['separator']}" stroke-opacity="0.8"/>
"""
    alt = f"{FOOTER_EYEBROW} {FOOTER_LEAD} {FOOTER_ACCENT} {FOOTER_LINE} Email {EMAIL}"
    return svg(W, H, alt, body, defs)


def main():
    (OUT / "buttons").mkdir(parents=True, exist_ok=True)
    (OUT / "projects").mkdir(parents=True, exist_ok=True)
    for name, t in THEMES.items():
        files = {
            f"hero-{name}.svg": hero(t),
            f"about-{name}.svg": about(t),
            f"opti5-{name}.svg": company_card(t),
            f"featured-header-{name}.svg": section_header("Projects", "Featured work.", t),
            f"company-header-{name}.svg": section_header("Company", "What I'm building.", t),
            f"projects/{FEATURED['slug']}-{name}.svg": featured_card(FEATURED, t),
            f"specs-{name}.svg": specs(t),
            f"footer-{name}.svg": footer(t),
        }
        for side, p in enumerate(PROJECTS):
            files[f"projects/{p['slug']}-{name}.svg"] = project_card(p, t, side)
            files[f"buttons/{p['slug']}-website-{name}.svg"] = link_pill("Visit website", "web", t, side * 2)
            files[f"buttons/{p['slug']}-github-{name}.svg"] = link_pill("GitHub", "github", t, side * 2 + 1)
        for slug, label, kind, primary in LINKS:
            files[f"buttons/{slug}-{name}.svg"] = button(label, kind, primary, t)
        for path, content in files.items():
            (OUT / path).write_text(content, encoding="utf-8")
    print(f"Wrote assets to {OUT}")


if __name__ == "__main__":
    main()
