
"""
chart-4-fdi-attraction-efficiency-relative-to-peers.py
Sri Lanka's FDI-attraction efficiency against structural peers and regional comparators.

Self-contained: the data are embedded below, so this script runs on its own.
The companion CSV holds the same numbers plus each country's structural distance
from Sri Lanka.

Technical efficiency is the share of frontier FDI a country actually attains,
where the frontier is the maximum inflow observed for economies with the same
fundamentals. It comes from a stochastic frontier model (half-normal
inefficiency, log FDI/GDP) estimated on 124 economies over 2010-2024; war years
are excluded so the comparison reflects normal-time investment climate.

LEFT PANEL  - structural peers: the economies closest to Sri Lanka on five
              standardised characteristics (economy size, income per capita,
              government effectiveness, access to surrounding markets, trade
              openness), ranked by straight-line distance in that space.
RIGHT PANEL - regional comparators: the Asian economies policy discussion most
              often invokes. Several are structurally quite unlike Sri Lanka.

Run:  python chart-4-fdi-attraction-efficiency-relative-to-peers.py
Out:  chart-4-fdi-attraction-efficiency-relative-to-peers.png
"""

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

# widen caption wrap to suit the 11-inch two-panel canvas
FULL_W  = 152
SHORT_W = 112

C_TEAL = "#5B8C85"

# ── left panel: structural peers (name, efficiency) ──
STRUCT = [
    ("Costa Rica",     0.629), ("Dominican Rep.", 0.602), ("Peru",        0.545),
    ("Ghana",          0.538), ("Senegal",        0.461), ("Guatemala",   0.426),
    ("Philippines",    0.389), ("C\u00f4te d\u2019Ivoire", 0.290), ("Paraguay",  0.287),
    ("El Salvador",    0.279), ("Bolivia",        0.250), ("Sri Lanka",   0.237),
    ("Kenya",          0.216), ("Ecuador",        0.168),
]

# ── right panel: regional comparators (name, efficiency) ──
REGION = [
    ("Cambodia",   0.651), ("China",       0.524), ("Indonesia", 0.474),
    ("India",      0.427), ("Vietnam",     0.410), ("Philippines", 0.389),
    ("Malaysia",   0.305), ("Thailand",    0.288), ("Bangladesh", 0.249),
    ("Sri Lanka",  0.237), ("Pakistan",    0.228), ("Korea, Rep.", 0.196),
    ("Nepal",      0.095),
]

HIGHLIGHT = "Sri Lanka"

TITLE    = "Sri Lanka trails both its structural peers and its region"
SUBTITLE = "FDI-attraction efficiency relative to the peacetime frontier, percent, 2010-2024"
SOURCE   = ("World Bank WDI/WGI; CEPII GeoDist; UCDP/PRIO Armed Conflict Dataset v26.1; "
            "author's stochastic frontier estimates.")
NOTE     = ("Technical efficiency is the share of frontier FDI a country actually attains, where the frontier "
            "is the maximum inflow observed for economies with the same fundamentals. Estimated by a stochastic "
            "frontier model (half-normal inefficiency, log FDI/GDP) on 124 economies over 2010-2024; war years "
            "are excluded so that the comparison reflects normal-time investment climate. Structural peers in "
            "the left panel are the economies closest to Sri Lanka on five measured characteristics -- economy "
            "size, income per capita, government effectiveness, access to surrounding markets and trade "
            "openness -- each standardised, with closeness measured as straight-line distance from Sri Lanka in "
            "that five-dimensional space. They are therefore countries a model would expect to attract similar "
            "investment, irrespective of region: Ecuador, the closest of all, matches Sri Lanka on every "
            "dimension. The right panel shows regional comparators for context; several are structurally quite "
            "unlike Sri Lanka (Malaysia, Korea and Vietnam are among the least similar economies in the sample) "
            "but are the ones policy discussion most often invokes. Sri Lanka ranks 103rd of 124 economies "
            "overall.")

OUT = "chart-4-fdi-attraction-efficiency-relative-to-peers.png"

plt.rcParams.update({
    "font.size": 12, "axes.labelsize": 11.5,
    "xtick.labelsize": 11, "ytick.labelsize": 11.5,
})


def panel(ax, rows, heading):
    rows = sorted(rows, key=lambda r: r[1])          # ascending -> best on top
    labels = [r[0] for r in rows]
    vals   = [r[1] * 100 for r in rows]
    cols   = [C_RED if l == HIGHLIGHT else C_LBLU for l in labels]
    ax.barh(labels, vals, color=cols, edgecolor="none", height=0.66)
    for i, v in enumerate(vals):
        ax.text(v + 1.4, i, f"{v:.0f}%", va="center", fontsize=10.5, color="#333333")
    lk = [r[1] for r in rows if r[0] == HIGHLIGHT][0] * 100
    ax.axvline(lk, color=C_RED, lw=1.1, ls="--", alpha=0.45)
    ax.set_xlim(0, 78); ax.set_xticks([0, 20, 40, 60])
    ax.set_xlabel("Technical efficiency (% of frontier attained)", fontsize=11)
    ax.set_title(heading, fontsize=12.5, fontweight="bold", color="#333333", pad=10, loc="left")
    style_ax(ax)


H_IN  = 8.6
below = caption_block_px(SOURCE, NOTE)
Hpx   = H_IN * DPI

fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, H_IN), dpi=DPI,
                               gridspec_kw={"wspace": 0.42})
panel(axL, STRUCT, "Structural peers")
panel(axR, REGION, "Regional comparators")

# reserve the caption block, then make sure the axis labels clear it
fig.subplots_adjust(left=0.135, right=0.985, top=0.90, bottom=below / Hpx)
for _ in range(4):
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    y0 = min(axL.xaxis.label.get_window_extent(r).y0,
             axR.xaxis.label.get_window_extent(r).y0)
    if y0 >= below - 1:
        break
    fig.subplots_adjust(bottom=fig.subplotpars.bottom + (below - y0) / Hpx)

fig.canvas.draw(); r = fig.canvas.get_renderer()
anchor = min(axL.xaxis.label.get_window_extent(r).y0,
             axR.xaxis.label.get_window_extent(r).y0)
place_caption(fig, SOURCE, NOTE, anchor)
plt.savefig(OUT, dpi=DPI, facecolor="white")
plt.close()
add_title_band(OUT, TITLE, SUBTITLE)
print("wrote", OUT)
