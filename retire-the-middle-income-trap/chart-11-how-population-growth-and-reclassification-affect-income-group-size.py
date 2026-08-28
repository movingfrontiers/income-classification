"""
chart-11-how-population-growth-and-reclassification-affect-income-group-size
============================================================================

Builds the composition bar chart and its companion CSV.

    python3 chart-11-how-population-growth-and-reclassification-affect-income-group-size.py

Input : income-classification-2050.xlsx  (sheets "Classification", "Population")
Output: chart-11-...-income-group-size.png
        chart-11-...-income-group-size.csv

Method
------
Each bar is the population of one income group in the year shown, split by where
those people came from over the preceding 25 years:

  already in the group   what the economies already there held at the start
  arrived by upward
    reclassification     what the economies that climbed in held in the year
                         they moved, so it carries their growth up to that point
  population growth      everything after that: growth of the economies that
                         stayed, growth of new members from the year they
                         arrived, and economies entering the classification

An economy reclassified downward into a group is counted with those already
there. There is one such case, Syria into low income, worth 0.02 billion.

The three parts sum to the bar exactly. A negative share means the members lost
population, which is what high income does after China joins in 2026: its two
positive parts exceed the group total and the difference is shown below the axis,
with a rule marking the true level.
"""
import csv
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SRC = 'income-classification-2050.xlsx'
STEM = ('chart-11-how-population-growth-and-reclassification-'
        'affect-income-group-size')
DPI = 200

GROUPS = ['LIC', 'MIC', 'HIC']
GNAME = {'LIC': 'Low income', 'MIC': 'Middle income', 'HIC': 'High income'}
G3 = {'L': 'LIC', 'LM': 'MIC', 'UM': 'MIC', 'H': 'HIC'}
SEGC = {'inc': '#C62828', 'recl': '#F9A825', 'grow': '#283593'}
SEGT = {'inc': 'white', 'recl': '#5A3D00', 'grow': 'white'}
SEGD = {'inc': '#C62828', 'recl': '#5A3D00', 'grow': '#283593'}
SEG = [('inc', 'solid'), ('recl', 'light'), ('grow', 'hatch')]
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
    rib, gin = {}, {}
    for i in G.index:
        gs, ps = G.loc[i], P.loc[i]
        o = gs[t0] if isinstance(gs[t0], str) else None
        d = gs[T] if isinstance(gs[T], str) else None
        if o is None and d is None:
            continue
        if o is None:
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
        r = rib.setdefault((o, d), dict(base=0.0, n=0,
                                        growth={g: 0.0 for g in GROUPS}))
        r['base'] += ps[t0]
        r['n'] += 1
        for g in GROUPS:
            r['growth'][g] += credits[g]
    return rib, gin


G, P, names = load()
D, CSVROWS = {}, []
for t0, T in ((2000, 2025), (2025, 2050)):
    rib, gin = cohorts(G, P, names, t0, T)
    for g in GROUPS:
        stay = [k for k in rib if k[0] == g and k[1] == g]
        up = [k for k in rib if k[1] == g and GROUPS.index(k[0]) < GROUPS.index(g)]
        dn = [k for k in rib if k[1] == g and GROUPS.index(k[0]) > GROUPS.index(g)]

        inc = sum(rib[k]['base'] for k in stay)
        inc_gr = sum(sum(rib[k]['growth'].values()) for k in stay) + gin.get(g, 0)
        arr_base = sum(rib[k]['base'] for k in up)
        arr_pre = sum(rib[k]['growth'][k[0]] for k in up)
        arr_post = sum(sum(w for k2, w in rib[k]['growth'].items() if k2 != k[0])
                       for k in up)
        # a group can also gain members from above; counted with those already in
        dn_at_move = sum(rib[k]['base'] + rib[k]['growth'][k[0]] for k in dn)
        dn_post = sum(sum(w for k2, w in rib[k]['growth'].items() if k2 != k[0])
                      for k in dn)

        already = inc + dn_at_move
        arrived = arr_base + arr_pre
        growth = inc_gr + arr_post + dn_post
        tot = levels(G, P, T)[g]
        assert abs(already + arrived + growth - tot) < 1e-6, (T, g)

        D[(T, g)] = dict(inc=already / 1000, recl=arrived / 1000,
                         grow=growth / 1000, tot=tot / 1000, t0=t0)
        r = lambda v: round(v / 1000, 4)
        pc = lambda v: round(v / tot * 100, 1)
        CSVROWS.append(dict(
            year=T, built_from=t0, group=g, group_name=GNAME[g],
            group_population_bn=r(tot),
            already_in_group_bn=r(already), already_in_group_pct=pc(already),
            arrived_by_upward_reclassification_bn=r(arrived),
            arrived_by_upward_reclassification_pct=pc(arrived),
            population_growth_bn=r(growth), population_growth_pct=pc(growth),
            economies_already_in_group=sum(rib[k]['n'] for k in stay + dn),
            economies_arrived_upward=sum(rib[k]['n'] for k in up),
            memo_incumbents_at_start_bn=r(inc),
            memo_incumbent_growth_bn=r(inc_gr),
            memo_arrivals_at_start_bn=r(arr_base),
            memo_arrivals_growth_before_move_bn=r(arr_pre),
            memo_arrivals_growth_after_move_bn=r(arr_post),
            memo_downward_arrivals_at_move_bn=r(dn_at_move),
            memo_downward_arrivals_growth_bn=r(dn_post)))


# -------------------------------------------------------------------- chart
BW = 0.62
CH13 = 13 / 72 / 8                              # one character height, headings
CH_SUB = 13.5 / 72 / 8                          # one character height, subtitle
HEAD_PAD = 0.035 * 0.520 + CH13                 # axes top to cluster heading
XP = {(2025, 'LIC'): 0.0, (2025, 'MIC'): 1.0, (2025, 'HIC'): 2.0,
      (2050, 'LIC'): 3.5, (2050, 'MIC'): 4.5, (2050, 'HIC'): 5.5}

fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes([0.105, 0.235, 0.868, 0.520])
ax.axhline(0, color='#2d2d2d', lw=1.1, zorder=1)

for (yr, g), x in XP.items():
    d = D[(yr, g)]
    up = dn = 0.0
    for key, kind in SEG:
        val = d[key]
        if abs(val) < 1e-9:
            continue
        if val >= 0:
            y0, up = up, up + val
        else:
            y0, dn = dn + val, dn + val
        ax.add_patch(Rectangle((x - BW / 2, y0), BW, abs(val), zorder=3,
                               fc=SEGC[key], ec='none'))
        txt = f'{val / d["tot"] * 100:.0f}%'.replace('-', '\u2212')
        mid = y0 + abs(val) / 2
        if abs(val) > 0.24:
            ax.text(x, mid, txt, ha='center', va='center',
                    fontsize=10.5 if abs(val) > 0.42 else 9.0,
                    fontweight='bold', zorder=5, color=SEGT[key])
        elif val >= 0:
            ax.text(x + BW / 2 + 0.07, mid, txt, ha='left', va='center',
                    fontsize=9.5, fontweight='bold', color=SEGD[key], zorder=5)
        else:
            ax.text(x + BW / 2 + 0.07, y0 - 0.05, txt, ha='left', va='top',
                    fontsize=9.5, fontweight='bold', color=SEGD[key], zorder=5)
    ax.plot([x - BW / 2, x + BW / 2], [d['tot'], d['tot']], color='#2d2d2d',
            lw=1.8, solid_capstyle='butt', zorder=6)
    ax.text(x, max(d['tot'], up) + 0.10, f'{d["tot"]:.2f}', ha='center',
            va='bottom', fontsize=12, fontweight='bold', color='#2d2d2d', zorder=7)
    ax.text(x, -0.34, g, ha='center', va='top', fontsize=12, fontweight='bold',
            color='#2d2d2d')

ax.set_xlim(-0.70, 6.20)
ax.set_ylim(-0.34, 6.10)
ax.set_yticks(np.arange(0, 6.01, 1.0))
ax.set_yticklabels([f'{int(v)}' for v in np.arange(0, 6.01, 1.0)], fontsize=10,
                   color='#646464')
ax.set_xticks([])
for s in ('top', 'right', 'bottom'):
    ax.spines[s].set_visible(False)
ax.spines['left'].set_color('#BBBBBB')
ax.set_ylabel('Population, billions', fontsize=11.5, color='#2d2d2d', labelpad=8)
ax.plot([2.75, 2.75], [-0.34, 6.10], color='#CCCCCC', lw=1.0, zorder=1)

# title, then subtitle and axes placed off its measured baseline
ttl = fig.text(0.030, 0.972,
               'How population growth and reclassification\naffect income group size',
               fontsize=19, fontweight='bold', color='#2d2d2d', va='top',
               linespacing=1.22)
fig.canvas.draw()
r0 = fig.canvas.get_renderer()
tb = ttl.get_window_extent(r0).y0 / fig.bbox.height
sub = fig.text(0.030, tb - 0.19 / 8,
               'Population of each group in billions, split by where its people came\n'
               'from over the preceding 25 years',
               fontsize=13.5, color='#646464', va='top', linespacing=1.30)
fig.canvas.draw()
sb = sub.get_window_extent(r0).y0 / fig.bbox.height
top = sb - (0.021 + CH_SUB) - 13 * 1.25 / 72 / 8 - HEAD_PAD
p = ax.get_position()
ax.set_position([p.x0, p.y0, p.width, top - p.y0])
hy = 1 + HEAD_PAD / ax.get_position().height
ax.text(0.20, hy, 'In 2025, built from 2000', transform=ax.transAxes,
        ha='center', va='bottom', fontsize=13, fontweight='bold', color='#2d2d2d')
ax.text(0.755, hy, 'In 2050, projected from 2025', transform=ax.transAxes,
        ha='center', va='bottom', fontsize=13, fontweight='bold', color='#2d2d2d')

hs = [Rectangle((0, 0), 1, 1, fc=SEGC['inc'], ec='white'),
      Rectangle((0, 0), 1, 1, fc=SEGC['recl'], ec='white'),
      Rectangle((0, 0), 1, 1, fc=SEGC['grow'], ec='white')]
lb = ['Already in the group', 'Arrived by upward reclassification',
      'Population growth']
fig.legend(hs, lb, loc='lower center', bbox_to_anchor=(0.5, 0.148), ncol=3,
           frameon=False, fontsize=10.4, handlelength=1.6, handleheight=1.05,
           columnspacing=1.6)

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
        for i, para in enumerate(paragraphs):
            last = i == len(paragraphs) - 1
            out += _wrap(fig, (para + ' ' + extra).strip() if last else para,
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
    rr = fig.canvas.get_renderer()
    gap = ((wm.get_window_extent(rr).x0 - objs[-1].get_window_extent(rr).x1)
           / fig.bbox.width)
    assert gap >= _w(fig, 'movi', WM_SIZE) * 0.95, f'watermark gap {gap:.4f}'
    assert abs(wm.get_window_extent(rr).y0 - objs[-1].get_window_extent(rr).y0
               ) / fig.bbox.height < 0.0015
    assert y_last > 0.004, f'caption bottom {y_last:.4f}'


PARAS = [
    "Source: World Bank OGHIST (July 2026) and WDI population; UN World Population Prospects 2024 medium variant; author's calculations and projections.",
    "Note: LIC = low-income countries, MIC = lower-middle and upper-middle-income countries taken together, HIC = high-income countries. Each bar is the "
    "population of the group in the year shown, and the three parts say where those people came from over the previous 25 years. Already in the group is "
    "what the economies that were there at the start held at the start. Arrived by upward reclassification is what the economies that climbed into it held "
    "in the year they moved, so it carries their growth up to that moment. Population growth is everything after that: the growth of the economies that "
    "stayed, plus the growth of the new members from the year they arrived, plus 0.02 billion of economies that enter the classification. Low income also "
    "gains 0.02 billion from the one economy reclassified downward into it, Syria, which is counted with those already in the group. Percentages are shares "
    "of the bar. A negative share means the members lost population, which is what high income does after China joins in 2026. Population is mid-year.",
]
draw_caption(fig, PARAS, top=0.128, closers=[
    'Figures are rounded to two decimals.',
    'All three groups share one population basis.',
    'All figures are rounded to two decimals.'])

fig.savefig(f'{STEM}.png', dpi=DPI, facecolor='white')

COLS = ['year', 'built_from', 'group', 'group_name', 'group_population_bn',
        'already_in_group_bn', 'already_in_group_pct',
        'arrived_by_upward_reclassification_bn',
        'arrived_by_upward_reclassification_pct',
        'population_growth_bn', 'population_growth_pct',
        'economies_already_in_group', 'economies_arrived_upward',
        'memo_incumbents_at_start_bn', 'memo_incumbent_growth_bn',
        'memo_arrivals_at_start_bn', 'memo_arrivals_growth_before_move_bn',
        'memo_arrivals_growth_after_move_bn',
        'memo_downward_arrivals_at_move_bn', 'memo_downward_arrivals_growth_bn']
with open(f'{STEM}.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(CSVROWS)
print(f'wrote {STEM}.png and {STEM}.csv')
