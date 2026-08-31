
"""
chart-2-actual-vs-benchmark-fdi-to-gdp.py
Sri Lanka: actual versus benchmark-predicted net FDI inflows, 1996-2024.

Self-contained: the data are embedded below, so this script runs on its own.
The companion file chart-2-actual-vs-benchmark-fdi-to-gdp.csv holds the same numbers.

The benchmark is a leave-one-out prediction. A pooled OLS model of net FDI
inflows (% of GDP, winsorised at the 1st/99th percentiles) on log GDP, log GDP
per capita, GDP growth, trade openness, inflation, log surrounding market
potential and government effectiveness, with year fixed effects, is estimated
on 130+ economies EXCLUDING Sri Lanka. Those coefficients are then applied to
Sri Lanka's own observed characteristics, year by year.

Run:  python chart-2-actual-vs-benchmark-fdi-to-gdp.py
Out:  chart-2-actual-vs-benchmark-fdi-to-gdp.png
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

# ── data: year, actual FDI (% GDP), leave-one-out benchmark (% GDP) ──
DATA = [
    (1996, 0.862546, 2.899000),
    (1998, 1.227252, 3.779941),
    (2000, 1.042074, 4.408311),
    (2002, 1.188278, 3.935718),
    (2003, 1.211327, 3.577504),
    (2004, 1.126677, 3.663997),
    (2005, 1.116129, 4.496472),
    (2006, 1.697007, 4.942277),
    (2007, 1.863974, 5.675264),
    (2008, 1.847530, 4.707731),
    (2009, 0.960390, 3.233808),
    (2015, 0.798746, 2.336155),
    (2016, 1.019372, 2.679952),
    (2017, 1.454628, 2.336736),
    (2018, 1.708887, 1.427744),
    (2019, 0.835367, 1.639303),
    (2020, 0.514701, 1.100664),
    (2021, 0.668826, 2.133964),
    (2022, 1.192493, 0.828090),
    (2023, 0.848017, 1.198479),
    (2024, 0.764078, 1.735785),
]
YEARS     = np.array([d[0] for d in DATA])
ACTUAL    = np.array([d[1] for d in DATA])
BENCHMARK = np.array([d[2] for d in DATA])

WAR_START, WAR_END = 1995.5, 2009.5   # UCDP/PRIO: conflict ends May 2009

TITLE    = "Sri Lanka has attracted less FDI than its fundamentals would predict"
SUBTITLE = "Actual versus benchmark-predicted net FDI inflows, percent of GDP, 1996-2024"
SOURCE   = ("World Bank World Development Indicators and Worldwide Governance Indicators; "
            "CEPII GeoDist; UCDP/PRIO Armed Conflict Dataset v26.1; author's calculations.")
NOTE     = ("The benchmark is the fitted value from a pooled OLS regression of net FDI inflows "
            "(percent of GDP, winsorised at the 1st and 99th percentiles) on log GDP, log GDP per "
            "capita, GDP growth, trade openness, inflation, log surrounding market potential and "
            "government effectiveness, plus year fixed effects, estimated on 130 or more economies "
            "excluding Sri Lanka and offshore financial centers, 1996 to 2024. Shaded region marks "
            "Sri Lanka's civil war (UCDP/PRIO, war-intensity conflict, ended May 2009). Adding "
            "conflict controls (war dummy, battle deaths, years since conflict) does not close the "
            "post-war gap.")

OUT = "chart-2-actual-vs-benchmark-fdi-to-gdp.png"

# ── build ──
H_IN  = 8.0
below = caption_block_px(SOURCE, NOTE)

fig, ax = plt.subplots(figsize=(8, H_IN), dpi=DPI)

ax.axvspan(WAR_START, WAR_END, color="#F5E6E0", alpha=0.6, zorder=0)
ax.text(2002.5, 6.05, "Civil war",      ha="center", fontsize=12, color="#8B4A3A", style="italic")
ax.text(2016.7, 6.05, "Post-war peace", ha="center", fontsize=12, color="#3A6B4A", style="italic")

ax.plot(YEARS, BENCHMARK, color=C_BLUE, lw=2.5, marker="o", ms=5,
        label="Cross-country benchmark")
ax.plot(YEARS, ACTUAL,    color=C_RED,  lw=2.5, marker="o", ms=5,
        label="Actual net FDI inflows")
ax.fill_between(YEARS, ACTUAL, BENCHMARK, where=BENCHMARK >= ACTUAL,
                color=C_LBLU, alpha=0.35, label="Underperformance gap")
ax.axvline(2009.4, color="#555555", lw=1.3, ls=":")

ax.set_ylabel("Net FDI inflows, percent of GDP")
# deliberately no x-axis label: the year ticks speak for themselves
ax.set_ylim(0, 6.6)
ax.set_xlim(1995.2, 2024.8)
ax.set_xticks([1996, 2000, 2005, 2010, 2015, 2020, 2024])
style_ax(ax)
leg = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.065), ncol=2, frameon=False)

plt.tight_layout(rect=[0, below / (H_IN * DPI), 1, 1])
place_caption(fig, SOURCE, NOTE, lowest_px(fig, [leg]))   # anchored to legend bottom
plt.savefig(OUT, dpi=DPI, facecolor="white")
plt.close()
add_title_band(OUT, TITLE, SUBTITLE)
print("wrote", OUT)
