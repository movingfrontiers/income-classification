
"""
chart-3-fdi-shortfall-by-period.py
The Sri Lanka FDI gap before and after the civil war.

Self-contained: the data are embedded below, so this script runs on its own.
The companion file chart-3-fdi-shortfall-by-period.csv holds the same numbers.

Each estimate is the coefficient on a Sri Lanka indicator in a pooled OLS
regression of net FDI inflows (% of GDP) on log GDP, log GDP per capita, GDP
growth, trade openness, inflation, log surrounding market potential and
government effectiveness, with year fixed effects and standard errors clustered
by country. The three rows are separate regressions on different sub-periods.

Run:  python chart-3-fdi-shortfall-by-period.py
Out:  chart-3-fdi-shortfall-by-period.png
"""
import numpy as np

# ── Moving Frontiers chart template (embedded so each script is self-contained) ──
import textwrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

DPI      = 200
C_RED    = "#B2503B"   # Sri Lanka / actual
C_BLUE   = "#1F4E79"   # benchmark
C_LBLU   = "#7FA8C9"   # gap fill / peer bars
C_GOLD   = "#E0A458"
C_MUTE   = "#555555"

CAP_FS      = 8.5                          # Source/Note font size
WM_FS       = CAP_FS * 1.2                 # watermark is 1.2x the caption
WM_TXT      = "movingfrontiers.substack.com"
FULL_W      = 112                          # caption wrap width (chars)
SHORT_W     = 76                           # last line wrapped short for watermark
GAP_PX      = 20                           # content bottom -> caption top
WM_DROP_PX  = 3                            # watermark nudged below its baseline
BOT_MARGIN  = 16
LINESPACING = 1.32

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 13,
    "axes.labelsize": 13, "xtick.labelsize": 12, "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "axes.edgecolor": "#888888", "axes.linewidth": 1.0,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def wrap_caption(source, note):
    """Flush-left wrap, no continuation indent; last line short for the watermark."""
    lines  = textwrap.wrap(f"Source: {source}", width=FULL_W)
    lines += textwrap.wrap(f"Note: {note}",     width=FULL_W)
    if len(lines[-1]) > SHORT_W:
        lines = lines[:-1] + textwrap.wrap(lines[-1], width=SHORT_W)
    return lines


def caption_block_px(source, note, dpi=DPI):
    n  = len(wrap_caption(source, note))
    lh = CAP_FS * LINESPACING * dpi / 72.0
    return GAP_PX + n * lh + BOT_MARGIN


def lowest_px(fig, artists):
    """Bottom edge (px from figure bottom) of the lowest rendered element."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    return min(a.get_window_extent(r).y0 for a in artists)


def place_caption(fig, source, note, anchor_px):
    """Caption top sits GAP_PX below anchor; watermark baseline-aligned to last line."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    Hpx = fig.get_size_inches()[1] * fig.dpi
    lines = wrap_caption(source, note)
    lh = CAP_FS * LINESPACING * fig.dpi / 72.0
    probe = fig.text(0.5, 0.5, "Ag", fontsize=CAP_FS, va="baseline")
    bb = probe.get_window_extent(r)
    ascent = bb.height - (0.5 * Hpx - bb.y0)
    probe.remove()
    top_y = anchor_px - GAP_PX
    fig.text(0.012, top_y / Hpx, "\n".join(lines), fontsize=CAP_FS, color="#555555",
             ha="left", va="top", linespacing=LINESPACING)
    last_baseline = top_y - ascent - (len(lines) - 1) * lh - WM_DROP_PX
    fig.text(0.988, last_baseline / Hpx, WM_TXT, fontsize=WM_FS, color="#999999",
             ha="right", va="baseline")


def _wrap_px(words, font, maxw):
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def add_title_band(png_path, title, subtitle):
    """Bold title + gray subtitle band above the plot; title wraps if needed."""
    img = Image.open(png_path); W, H = img.size
    ts = int(W * 0.030); ss = int(ts * 0.58)
    try:
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", ts)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", ss)
    except Exception:
        ft = ImageFont.load_default(); fs = ImageFont.load_default()
    x = int(W * 0.025); maxw = W - 2 * x
    tl = _wrap_px(title.split(), ft, maxw)
    sl = _wrap_px(subtitle.split(), fs, maxw)
    pad = int(ts * 0.75); gap = int(ts * 0.35)
    tlh = int(ts * 1.22); slh = int(ss * 1.30)
    bh  = pad + len(tl) * tlh + gap + len(sl) * slh + pad
    canvas = Image.new("RGB", (W, H + bh), "white")
    canvas.paste(img, (0, bh))
    d = ImageDraw.Draw(canvas)
    y = pad
    for ln in tl:
        d.text((x, y), ln, fill=(45, 45, 45), font=ft); y += tlh
    y += gap - int(ts * 0.10)
    for ln in sl:
        d.text((x, y), ln, fill=(100, 100, 100), font=fs); y += slh
    canvas.save(png_path)


def style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# ── data: label, point estimate, 95% CI low, 95% CI high, N ──
ROWS = [
    ("Full period\n1996-2024", -1.847, -2.247, -1.448, 3097),
    ("War period\n1996-2009",  -2.270, -2.838, -1.702, 1268),
    ("Post-war\n2010-2024",    -1.058, -1.713, -0.402, 1829),
]
COLORS = [C_BLUE, C_RED, C_GOLD]

TITLE    = "The FDI gap shrank by half after the war"
SUBTITLE = "Conditional FDI shortfall, percentage points of GDP"
SOURCE   = ("World Bank World Development Indicators and Worldwide Governance Indicators; "
            "CEPII GeoDist; UCDP/PRIO Armed Conflict Dataset v26.1; author's calculations.")
NOTE     = ("Coefficient on a Sri Lanka indicator in pooled OLS regressions of net FDI inflows "
            "(percent of GDP) on log GDP, log GDP per capita, GDP growth, trade openness, inflation, "
            "log surrounding market potential and government effectiveness, with year fixed effects "
            "and standard errors clustered by country (95 percent confidence intervals shown). War "
            "period restricted to 1996-2009; post-war to 2010-2024. All three estimates are "
            "significant at the 1 percent level. Adding conflict controls to the post-war sample "
            "leaves the -1.06 estimate unchanged.")

OUT = "chart-3-fdi-shortfall-by-period.png"

# ── build ──
H_IN  = 5.6          # chart area deliberately shallow; three rows only
below = caption_block_px(SOURCE, NOTE)

fig, ax = plt.subplots(figsize=(8, H_IN), dpi=DPI)
ypos = np.arange(len(ROWS))[::-1]
ax.axvline(0, color="#888888", lw=1.0, ls="--")

for (label, coef, lo, hi, n), y, col in zip(ROWS, ypos, COLORS):
    ax.plot([lo, hi], [y, y], color=col, lw=4, solid_capstyle="round")
    ax.plot(coef, y, "o", color=col, ms=12)
    ax.text(coef, y + 0.26, f"{coef:+.2f} pp", ha="center", fontsize=12.5,
            color="#222222", fontweight="bold")
    ax.text(hi + 0.15, y, f"n={n:,}", va="center", fontsize=10.5, color="#888888")

ax.set_yticks(ypos)
ax.set_yticklabels([r[0] for r in ROWS])
ax.set_xlabel("Sri Lanka dummy, percentage points of GDP")
ax.set_xlim(-3.4, 1.6)
ax.set_ylim(-0.55, 2.75)
style_ax(ax)

plt.tight_layout(rect=[0, below / (H_IN * DPI), 1, 1])
place_caption(fig, SOURCE, NOTE, lowest_px(fig, [ax.xaxis.label]))
plt.savefig(OUT, dpi=DPI, facecolor="white")
plt.close()
add_title_band(OUT, TITLE, SUBTITLE)
print("wrote", OUT)
