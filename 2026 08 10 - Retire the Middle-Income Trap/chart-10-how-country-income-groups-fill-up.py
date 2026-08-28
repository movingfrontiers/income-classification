"""
chart-10-how-country-income-groups-fill-up
==========================================

Builds the cohort alluvial chart and its companion CSV.

    python3 chart-10-how-country-income-groups-fill-up.py

Input : income-classification-2050.xlsx  (sheets "Classification", "Population")
Output: chart-10-how-country-income-groups-fill-up.png
        chart-10-how-country-income-groups-fill-up.csv

Method
------
Each economy belongs to exactly one cohort per panel, defined by its group at the
start and its group at the end. A cohort leaves the left bar at its base
population, so the left bars carry no growth, and arrives at the right bar wider
by the growth of those members over the 25 years. Growth is credited to the group
the economy held at the start of each year, which splits it into growth before
the move and growth after it. Base plus growth-before is the population in the
year of the reclassification.

Cohorts net out reversals: an economy that lost high income and regained it
appears only as high income. Sixteen economies did that between 2000 and 2025.

Layout is measured, not eyeballed. Flow labels are placed by a two-pass collision
resolver against rendered bounding boxes, and the caption block is anchored to
the legend's measured bottom edge.
"""
import csv
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap

SRC = 'income-classification-2050.xlsx'
STEM = 'chart-10-how-country-income-groups-fill-up'
DPI = 200

COL = {'LIC': '#C62828', 'MIC': '#F9A825', 'HIC': '#283593'}
TXT = {'LIC': 'white', 'MIC': '#5A3D00', 'HIC': 'white'}
GROUPS = ['LIC', 'MIC', 'HIC']
RANK = {g: i for i, g in enumerate(GROUPS)}
G3 = {'L': 'LIC', 'LM': 'MIC', 'UM': 'MIC', 'H': 'HIC'}
SHORT = {'Russian Federation': 'Russia', 'Congo, Dem. Rep.': 'Congo DR',
         'Syrian Arab Republic': 'Syria'}
YEARS = [2000, 2025, 2050]
plt.rcParams['font.family'] = 'DejaVu Sans'


# --------------------------------------------------------------------- data
def load():
    cls = pd.read_excel(SRC, sheet_name='Classification', header=2)
    pop = pd.read_excel(SRC, sheet_name='Population', header=4)
    cls = cls[cls['Economy'].notna() & cls['Code'].notna()].copy()
    pop = pop[pop['Economy'].notna() & pop['Code'].notna()].copy()

    def yearcols(df):
        out = {}
        for c in df.columns:
            try:
                y = int(float(str(c).strip()))
            except ValueError:
                continue
            if 1980 <= y <= 2060:
                out[c] = y
        return out

    yc, yp = yearcols(cls), yearcols(pop)
    C = cls.set_index('Code')[list(yc)].rename(columns=yc)
    P = pop.set_index('Code')[list(yp)].rename(columns=yp).astype(float)
    years = list(range(1990, 2051))
    C, P = C.reindex(columns=years), P.reindex(columns=years)
    codes = sorted(set(C.index) & set(P.index))
    C, P = C.loc[codes], P.loc[codes]
    Gm = C.map(lambda v: G3.get(v) if isinstance(v, str) else np.nan)
    return Gm, P, cls.set_index('Code')['Economy'].reindex(codes)


def levels(G, P, year):
    return {g: P.loc[G[year] == g, year].sum() for g in GROUPS}


def cohorts(G, P, names, t0, T):
    """rib[(origin, destination)] and entrants to the classification."""
    rib, gin = {}, {}
    for i in G.index:
        gs, ps = G.loc[i], P.loc[i]
        o = gs[t0] if isinstance(gs[t0], str) else None
        d = gs[T] if isinstance(gs[T], str) else None
        if o is None and d is None:
            continue
        if o is None:                       # enters the classification
            gin[d] = gin.get(d, 0.0) + ps[T]
            continue
        assert d is not None, 'a departure would need its own band'
        credits = {g: 0.0 for g in GROUPS}
        last = o
        for t in range(t0 + 1, T + 1):
            here = gs[t - 1] if isinstance(gs[t - 1], str) else last
            credits[here] += ps[t] - ps[t - 1]
            if isinstance(gs[t - 1], str):
                last = gs[t - 1]
        assert abs(ps[t0] + sum(credits.values()) - ps[T]) < 1e-6, i
        r = rib.setdefault((o, d), dict(base=0.0, n=0, members=[],
                                        growth={g: 0.0 for g in GROUPS}))
        r['base'] += ps[t0]
        r['n'] += 1
        r['members'].append((str(names[i]), ps[T]))
        for g in GROUPS:
            r['growth'][g] += credits[g]
    return rib, gin


G, P, names = load()
lev = {y: {g: v / 1000 for g, v in levels(G, P, y).items()} for y in YEARS}
RIB, GIN = {}, {}
for t0, T in ((2000, 2025), (2025, 2050)):
    rib, gin = cohorts(G, P, names, t0, T)
    RIB[t0] = {k: dict(base=v['base'] / 1000, n=v['n'], members=v['members'],
                       growth={g: w / 1000 for g, w in v['growth'].items()})
               for k, v in rib.items()}
    GIN[t0] = {g: w / 1000 for g, w in gin.items()}

for t0 in RIB:                              # entrants ride the stay ribbon
    for g, w in GIN[t0].items():
        RIB[t0][(g, g)]['growth'][g] += w
    GIN[t0] = {}
    for v in RIB[t0].values():
        v['total'] = v['base'] + sum(v['growth'].values())


# ----------------------------------------------------------------- geometry
GAP, BW = 0.42, 0.072
X = {2000: 0.0, 2025: 1.0, 2050: 2.0}
slot, b = {}, None
for y in YEARS:
    b = 0.0
    for g in GROUPS:
        slot[(y, g)] = (b, b + lev[y][g])
        b += lev[y][g] + GAP
TOP = max(slot[(y, 'HIC')][1] for y in YEARS)


def out_stack(t0, g):
    it = [(d, v['base']) for (o, d), v in RIB[t0].items() if o == g]
    return sorted(it, key=lambda kv: RANK[kv[0]])


def in_stack(t0, g):
    it = [(o, v['total']) for (o, d), v in RIB[t0].items() if d == g]
    return sorted(it, key=lambda kv: RANK[kv[0]])


def band(t0, g, side, partner):
    y = t0 if side == 'out' else t0 + 25
    acc = slot[(y, g)][0]
    for k, w in (out_stack(t0, g) if side == 'out' else in_stack(t0, g)):
        if k == partner:
            return acc, w
        acc += w
    raise KeyError((t0, g, side, partner))


def smooth(n=240):
    t = np.linspace(0, 1, n)
    return t, 3 * t ** 2 - 2 * t ** 3


def ribbon(ax, x0, x1, a0, w0, a1, w1, c0, c1, z=2, hatch=None, alpha=0.92):
    t, s = smooth()
    x = x0 + (x1 - x0) * t
    lo = a0 + (a1 - a0) * s
    hi = (a0 + w0) + ((a1 + w1) - (a0 + w0)) * s
    verts = np.concatenate([np.column_stack([x, hi]),
                            np.column_stack([x[::-1], lo[::-1]])])
    if hatch is None:
        patch = PathPatch(Path(verts, closed=True), lw=0, fc='none', zorder=z)
        ax.add_patch(patch)
        if c0 == c1:
            patch.set_facecolor(c0)
            patch.set_alpha(alpha)
        else:
            cm = LinearSegmentedColormap.from_list('r', [c0, c1])
            im = ax.imshow(np.linspace(0, 1, 256).reshape(1, -1), cmap=cm,
                           extent=[x0, x1, lo.min(), hi.max()], aspect='auto',
                           origin='lower', alpha=alpha, zorder=z)
            im.set_clip_path(patch)
    else:
        fc, ec, al, hh = hatch
        ax.add_patch(PathPatch(Path(verts, closed=True), fc=fc, ec=ec, lw=0.0,
                               alpha=al, hatch=hh, zorder=z))
    return lambda f: (x0 + (x1 - x0) * f, np.interp(f, t, (lo + hi) / 2))


def extent(t, rend):
    p = t.get_bbox_patch()
    return (p.get_window_extent(rend) if p is not None
            else t.get_window_extent(rend))


# ------------------------------------------------------------------ caption
CAP_SIZE, CAP_LEFT, CAP_RIGHT_PX, CAP_PITCH_PX = 7.0, 0.012, 70.0, 22.0
WM, WM_COLOR, CAP_COLOR = 'movingfrontiers.substack.com', '#999999', '#666666'
WM_SIZE = CAP_SIZE * 1.2
_wcache = {}


def _w(fig, s, size):
    if (s, size) not in _wcache:
        t = fig.text(0, -1, s, fontsize=size)
        fig.canvas.draw()
        _wcache[(s, size)] = (t.get_window_extent(fig.canvas.get_renderer())
                              .width / fig.bbox.width)
        t.remove()
    return _wcache[(s, size)]


def _greedy(fig, words, limit):
    lines, cur = [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if cur and _w(fig, trial, CAP_SIZE) > limit:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _wrap(fig, text, full, tail):
    """All lines but the final two run full width; the last two clear the mark."""
    words = text.split()
    if tail >= full:
        return _greedy(fig, words, full)
    fallback = None
    for n_full in range(60):
        head, cur, i = [], '', 0
        while i < len(words) and len(head) < n_full:
            trial = (cur + ' ' + words[i]).strip()
            if cur and _w(fig, trial, CAP_SIZE) > full:
                head.append(cur)
                cur = ''
                continue
            cur = trial
            i += 1
        rest = ([cur] if cur else []) + words[i:]
        out = _greedy(fig, ' '.join(rest).split(), tail)
        if len(out) == 2:
            return head + out
        if len(out) < 2:
            fallback = head + out
            break
    return fallback or _greedy(fig, words, tail)


def draw_caption(fig, paragraphs, top, closers=()):
    wi, hi = fig.get_size_inches()
    W, H = wi * DPI, hi * DPI
    right = 1 - CAP_RIGHT_PX / W
    full = right - CAP_LEFT
    tail = full - _w(fig, WM, WM_SIZE) - _w(fig, 'movi', WM_SIZE)
    pitch = CAP_PITCH_PX / H

    def build(extra):
        out = []
        for i, p in enumerate(paragraphs):
            last = i == len(paragraphs) - 1
            out += _wrap(fig, (p + ' ' + extra).strip() if last else p,
                         full, tail if last else full)
        return out

    for c in ('',) + tuple(closers):
        lines = build(c)
        if (_w(fig, lines[-1], CAP_SIZE) <= tail
                and _w(fig, lines[-2], CAP_SIZE) <= tail):
            break
    y, objs = top, []
    for ln in lines:
        objs.append(fig.text(CAP_LEFT, y, ln, fontsize=CAP_SIZE,
                             color=CAP_COLOR, va='baseline'))
        y -= pitch
    y_last = y + pitch
    wm = fig.text(right, y_last, WM, fontsize=WM_SIZE, color=WM_COLOR,
                  ha='right', va='baseline')
    r = fig.canvas.get_renderer()
    gap = ((wm.get_window_extent(r).x0 - objs[-1].get_window_extent(r).x1)
           / fig.bbox.width)
    assert gap >= _w(fig, 'movi', WM_SIZE) * 0.95, f'watermark gap {gap:.4f}'
    assert abs(wm.get_window_extent(r).y0 - objs[-1].get_window_extent(r).y0
               ) / fig.bbox.height < 0.0015
    assert y_last > 0.004, f'caption bottom {y_last:.4f}'


# -------------------------------------------------------------------- chart
fig = plt.figure(figsize=(8, 10.6))
ax = fig.add_axes([0.052, 0.212, 0.912, 0.628])
ax.set_xlim(-0.20, 2.24)
ax.set_ylim(-0.32, TOP + 0.42)
ax.axis('off')
OBST, centre, YR = [], {}, {}

for t0 in (2000, 2025):
    x0, x1 = X[t0] + BW, X[t0 + 25] - BW
    for (o, d) in sorted(RIB[t0], key=lambda k: (RANK[k[0]], RANK[k[1]])):
        v = RIB[t0][(o, d)]
        a0, _ = band(t0, o, 'out', d)
        a1, _ = band(t0, d, 'in', o)
        net = v['total'] - v['base']
        hw = net if net >= 0.04 else 0.0     # a thinner band reads as a stray line
        centre[(t0, o, d)] = ribbon(ax, x0, x1, a0, v['base'],
                                    a1, v['total'] - hw,
                                    COL[o], COL[d], z=2 if o == d else 3)
        if hw > 0:
            ribbon(ax, x0, x1, a0 + v['base'], 0.0, a1 + v['total'] - hw, hw,
                   COL[d], COL[d], z=4, hatch=(COL[d], COL[d], 0.34, '///'))

for y in YEARS:
    for g in GROUPS:
        b, L = slot[(y, g)][0], lev[y][g]
        OBST.append(ax.add_patch(Rectangle((X[y] - BW, b), 2 * BW, L, fc=COL[g],
                                 ec='white', lw=1.1, zorder=6)))
        OBST.append(ax.text(X[y], b + L / 2, f'{L:.2f}', ha='center',
                    va='center', color=TXT[g], fontsize=11 if L < 0.9 else 12,
                    fontweight='bold', zorder=7, linespacing=1.28))
    YR[y] = ax.text(X[y], TOP + 0.30, str(y), ha='center', va='bottom',
                    fontsize=17, fontweight='bold', color='#2d2d2d')
    OBST.append(YR[y])

# ---------------------------------------------------------------- ribbon labels
BOX = dict(boxstyle='round,pad=0.26', fc='#F7F5F1', ec='none', lw=0)
FRAC0 = {('LIC', 'MIC'): 0.30, ('MIC', 'HIC'): 0.72, ('MIC', 'LIC'): 0.72,
         ('LIC', 'LIC'): 0.50, ('MIC', 'MIC'): 0.30, ('HIC', 'HIC'): 0.32}
CANDS = [0.0, 0.10, -0.10, 0.20, -0.20, 0.06, -0.06, 0.30, -0.30, 0.16, -0.16,
         0.38, -0.38, 0.44, -0.44]
NUDGE = {(2000, 'HIC', 'HIC'): 2.0, (2000, 'MIC', 'HIC'): 1.0,
         (2000, 'MIC', 'MIC'): 1.0, (2000, 'LIC', 'MIC'): 0.5,
         (2025, 'LIC', 'MIC'): 0.5}
CHAR_DOWN = {(2000, 'HIC', 'HIC'): 1.0}


def term(x, word=''):
    neg = x < -0.005
    val = -x if neg else max(x, 0.0)
    return (' \u2212 ' if neg else ' + ') + f'{val:.2f}' + (' ' + word if word else '')


fig.canvas.draw()
rend = fig.canvas.get_renderer()
obst = [extent(o, rend) if hasattr(o, 'get_bbox_patch')
        else o.get_window_extent(rend) for o in OBST]
labels = []
for t0 in (2000, 2025):
    for (o, d), v in sorted(RIB[t0].items(), key=lambda kv: -kv[1]['total']):
        if v['total'] < 0.18:
            continue
        lead = SHORT.get(max(v['members'], key=lambda m: m[1])[0],
                         max(v['members'], key=lambda m: m[1])[0])
        pre = v['growth'][o]
        post = sum(w for g2, w in v['growth'].items() if g2 != o)
        if o == d:
            head = f'{v["n"]} stay {o}'
            sub = f'{v["base"]:.2f}' + term(v['total'] - v['base'])
        else:
            share = (max(v['members'], key=lambda m: m[1])[1]
                     / sum(m[1] for m in v['members']))
            head = (f'{lead.upper()} + {v["n"] - 1} \u2192 {d}' if share > 0.30
                    else f'{v["n"]} \u2192 {d}')
            sub = f'{v["base"]:.2f}' + term(pre, 'before') + term(post, 'after')
        t = ax.text(0, 0, f'{head}\n{sub}', ha='center', va='center',
                    fontsize=7.8, fontweight='bold', color='#2d2d2d', bbox=BOX,
                    zorder=9, linespacing=1.30, multialignment='center')
        px0, px1 = X[t0] + BW, X[t0 + 25] - BW
        f0 = FRAC0[(o, d)]
        t.set_position(((px0 + px1) / 2, centre[(t0, o, d)](0.5)[1]))
        fig.canvas.draw()
        inv = ax.transData.inverted()
        hw2 = abs(inv.transform((extent(t, rend).width, 0))[0]
                  - inv.transform((0, 0))[0]) / 2
        span = px1 - px0
        f_lo = min(0.5, (hw2 + 0.01) / span)
        f_hi = max(0.5, 1 - (hw2 + 0.01) / span)
        placed = False
        for dd in CANDS:
            f = min(max(f0 + dd, f_lo), f_hi)
            t.set_position(centre[(t0, o, d)](f))
            fig.canvas.draw()
            bb = extent(t, rend)
            if not any(bb.overlaps(q) for q in obst
                       + [extent(l[0], rend) for l in labels]):
                placed = True
                break
        if not placed:
            t.set_position(centre[(t0, o, d)](min(max(f0, f_lo), f_hi)))
        t.set_position(((X[t0] + X[t0 + 25]) / 2, centre[(t0, o, d)](0.5)[1]))
        labels.append((t, t0, o, d))

fig.canvas.draw()
inv = ax.transData.inverted()
for t, t0, o, d in labels:                  # nudges in multiples of box height
    bb = extent(t, rend)
    h = abs(inv.transform((0, bb.height))[1] - inv.transform((0, 0))[1])
    ch = h / (t.get_text().count('\n') + 1)
    x, y = t.get_position()
    t.set_position((x, y + NUDGE.get((t0, o, d), 0.0) * h
                    - CHAR_DOWN.get((t0, o, d), 0.0) * ch))
labels = [l[0] for l in labels]

# ------------------------------------------------------------- titles, legend
fig.text(0.030, 0.972, 'How country income groups fill up', fontsize=19,
         fontweight='bold', color='#2d2d2d', va='top')
fig.text(0.030, 0.935,
         'Population in billions, with each ribbon showing its starting population\n'
         '(solid) and population growth (hatched), before and after reclassification',
         fontsize=13.5, color='#646464', va='top', linespacing=1.30)

hs = [Rectangle((0, 0), 1, 1, fc=COL['LIC'], ec='white'),
      Rectangle((0, 0), 1, 1, fc=COL['MIC'], ec='white'),
      Rectangle((0, 0), 1, 1, fc=COL['HIC'], ec='white'),
      Rectangle((0, 0), 1, 1, fc='white', ec='#555555', lw=0.9, hatch='///')]
lb = ['Low income', 'Middle income', 'High income',
      'Population growth before and after reclassification']
leg = fig.legend(hs, lb, loc='lower center', bbox_to_anchor=(0.5, 0.132), ncol=4,
                 frameon=False, fontsize=9.0, handlelength=1.5, handleheight=1.05,
                 columnspacing=1.1, labelspacing=0.62)

# projection note, one character clear of the plotted area
fig.canvas.draw()
r = fig.canvas.get_renderer()
probe = fig.text(0, -1, 'projection', fontsize=10.5, style='italic')
fig.canvas.draw()
CH = probe.get_window_extent(r).height / fig.bbox.height
probe.remove()
chart_bottom = (ax.get_position().y0 + (0 - ax.get_ylim()[0])
                / (ax.get_ylim()[1] - ax.get_ylim()[0]) * ax.get_position().height)
px = fig.transFigure.inverted().transform(
    ax.transData.transform((X[2025] + BW + 0.015, 0)))[0]
pnote = fig.text(px, chart_bottom - CH, 'projection from 2026 \u2192', ha='left',
                 va='top', fontsize=10.5, style='italic', color='#646464')
fig.canvas.draw()
pn = pnote.get_window_extent(r)
lgb = leg.get_window_extent(r)
leg.set_bbox_to_anchor((0.5, pn.y0 / fig.bbox.height - 1.5 * CH
                        - lgb.height / fig.bbox.height))
fig.canvas.draw()

# caption sits exactly 2.5 caption-character heights below the legend
_lg = leg.get_window_extent(r).y0 / fig.bbox.height
pr = fig.text(0, -1, 'Source', fontsize=CAP_SIZE)
fig.canvas.draw()
pb = pr.get_window_extent(r)
capch = pb.height / fig.bbox.height
ascent = pb.y1 / fig.bbox.height + 1.0
pr.remove()

PARAS = [
    "Source: World Bank OGHIST (July 2026) and WDI population; UN World Population Prospects 2024 medium variant; author's calculations and projections.",
    "Note: LIC = low-income countries, MIC = lower-middle and upper-middle-income countries taken together, HIC = high-income countries. Each economy "
    "belongs to one ribbon per panel, from its group at the start of the panel to its group at the end. A ribbon leaves the left bar at the population its "
    "members had in that year, so the left bars carry no growth, and arrives wider by their growth over the 25 years, shown as the hatched band. Each label "
    "reads starting population, then growth before reclassification, then growth after it, so solid plus the growth before is what these economies held in "
    "the year they were reclassified. A ribbon narrows where growth is negative, which is what high income does once China arrives. Cohorts net out "
    "reversals, so an economy that lost high income and regained it appears only as high income; 16 economies did that between 2000 and 2025. Counts are "
    "cohort members. Population is mid-year.",
]
draw_caption(fig, PARAS, top=_lg - 2.5 * capch - ascent, closers=[
    'Figures are rounded to two decimals.',
    'All three groups share one population basis.',
    'All figures are rounded to two decimals.'])

fig.canvas.draw()
allt = [extent(t, r) for t in labels]
assert not [(i, j) for i in range(len(allt)) for j in range(i + 1, len(allt))
            if allt[i].overlaps(allt[j])], 'label-label collision'
assert not [(i, k) for i, bb in enumerate(allt)
            for k, q in enumerate(obst) if bb.overlaps(q)], 'label-bar collision'
fig.savefig(f'{STEM}.png', dpi=DPI, facecolor='white')


# ---------------------------------------------------------------------- csv
rows = []
for y in YEARS:
    tot = sum(lev[y].values())
    for g in GROUPS:
        rows.append(dict(row_type='bar', year=y, group=g,
                         population_bn=round(lev[y][g], 4),
                         share_of_classified_pct=round(lev[y][g] / tot * 100, 1)))
for t0 in (2000, 2025):
    for (o, d) in sorted(RIB[t0], key=lambda k: (RANK[k[0]], RANK[k[1]])):
        v = RIB[t0][(o, d)]
        pre = v['growth'][o]
        post = sum(w for k, w in v['growth'].items() if k != o)
        lead = SHORT.get(max(v['members'], key=lambda m: m[1])[0],
                         max(v['members'], key=lambda m: m[1])[0])
        share = (max(v['members'], key=lambda m: m[1])[1]
                 / sum(m[1] for m in v['members']))
        if o == d:
            label = f'{v["n"]} stay {o}'
        elif v['n'] == 1:
            label = f'{lead.upper()} -> {d}'
        elif share > 0.30:
            label = f'{lead.upper()} + {v["n"] - 1} -> {d}'
        else:
            label = f'{v["n"]} -> {d}'
        rows.append(dict(
            row_type='ribbon', panel=f'{t0}-{t0 + 25}', origin=o, destination=d,
            economies=v['n'], chart_label=label,
            labelled_on_chart='yes' if v['total'] >= 0.18 else 'no',
            largest_member=lead,
            start_population_bn=round(v['base'], 4),
            growth_total_bn=round(pre + post, 4),
            growth_before_reclassification_bn=('' if o == d else round(pre, 4)),
            growth_after_reclassification_bn=('' if o == d else round(post, 4)),
            end_population_bn=round(v['total'], 4),
            population_at_reclassification_bn=('' if o == d
                                               else round(v['base'] + pre, 4)),
            notes=('growth includes economies entering the classification'
                   if o == d and o in ('LIC', 'MIC', 'HIC') and t0 == 2000 else '')))

COLS = ['row_type', 'panel', 'year', 'group', 'origin', 'destination',
        'economies', 'chart_label', 'labelled_on_chart', 'largest_member',
        'population_bn', 'share_of_classified_pct', 'start_population_bn',
        'growth_total_bn', 'growth_before_reclassification_bn',
        'growth_after_reclassification_bn', 'end_population_bn',
        'population_at_reclassification_bn', 'notes']
with open(f'{STEM}.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
    w.writeheader()
    for row in rows:
        w.writerow({c: row.get(c, '') for c in COLS})

# departures must equal the left bar and arrivals the right bar
for t0 in (2000, 2025):
    for g in GROUPS:
        out = sum(v['base'] for (o, d), v in RIB[t0].items() if o == g)
        inn = sum(v['total'] for (o, d), v in RIB[t0].items() if d == g)
        assert abs(out - lev[t0][g]) < 1e-6, (t0, g, 'departures')
        assert abs(inn - lev[t0 + 25][g]) < 1e-6, (t0, g, 'arrivals')
print(f'wrote {STEM}.png and {STEM}.csv')
