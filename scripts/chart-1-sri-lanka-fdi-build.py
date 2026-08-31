# =============================================================================
# Chart: Sri Lanka FDI as share of GDP, 1970-2024
#
# Provenance, frozen vintage. Nothing is read from disk or the network.
#   Data: World Bank WDI, series BX.KLT.DINV.WD.GD.ZS
#         (Foreign direct investment, net inflows, % of GDP), July 2026 release.
#   Country: Sri Lanka
#   Vintage freeze date: August 2026.
# =============================================================================
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

SRC = ("Source: World Bank World Development Indicators (BX.KLT.DINV.WD.GD.ZS), July 2026 release." + chr(10))
NOTE = ("Note: FDI net inflows as a share of GDP, Sri Lanka, 1970\u20132024. "
        "The dashed line is the 1970\u20132024 average (0.91% of GDP). "
        "Peak inflows of 2.8% of GDP were recorded in 1997. "
        "Negative values in 1970\u201378 reflect near-zero or net-outflow years.")

TITLE = "Sri Lanka\u2019s FDI inflows have remained persistently low"
SUB   = "Foreign direct investment, net inflows as a share of GDP, percent, 1970\u20132024"

# ---- embedded data, frozen from FDI.csv (World Bank WDI, July 2026) ----
DATA = {
    1970: -0.01306, 1971: 0.01266, 1972: 0.01175, 1973: 0.01739, 1974: 0.03917,
    1975: 0.00376,  1976: 0.00003, 1977: -0.02969, 1978: 0.05394, 1979: 1.39427,
    1980: 1.06868,  1981: 1.11563, 1982: 1.33300,  1983: 0.73103, 1984: 0.53963,
    1985: 0.43761,  1986: 0.46405, 1987: 0.89049,  1988: 0.65520, 1989: 0.28253,
    1990: 0.53974,  1991: 0.53719, 1992: 1.26379,  1993: 1.88108, 1994: 1.42020,
    1995: 0.42975,  1996: 0.86255, 1997: 2.84958,  1998: 1.22725, 1999: 1.12278,
    2000: 1.04207,  2001: 1.09075, 2002: 1.18828,  2003: 1.21133, 2004: 1.12668,
    2005: 1.11613,  2006: 1.69701, 2007: 1.86397,  2008: 1.84753, 2009: 0.96039,
    2010: 0.81445,  2011: 1.41088, 2012: 1.33592,  2013: 1.21148, 2014: 1.08278,
    2015: 0.79875,  2016: 1.01937, 2017: 1.45463,  2018: 1.70889, 2019: 0.83537,
    2020: 0.51470,  2021: 0.66883, 2022: 1.19249,  2023: 0.84802, 2024: 0.76408,
}

years = sorted(DATA.keys())
vals  = [DATA[y] for y in years]
avg   = float(np.mean(vals))

# ---- assertions: numbers stated in caption must follow from the data ----
assert round(avg, 2) == 0.91, 'caption states 1970-2024 average is 0.91%'
peak_yr  = max(DATA, key=DATA.get)
peak_val = DATA[peak_yr]
assert peak_yr == 1997,         'caption states peak in 1997'
assert round(peak_val, 1) == 2.8, 'caption states peak 2.8%'

INDIGO = '#283593'
RED    = '#C62828'

# ---------------------------------------------------------------- shared helpers

def caption(fig, ax, cap, fs=7.8, gap_lines=2.0):
    """Moving Frontiers caption block: every line runs full width except the last two,
    which stop short so the watermark can sit on the baseline of the last line,
    with half a character of vertical space above it."""
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    Wpx  = fig.get_figwidth() * fig.dpi
    bots = [t.get_window_extent(r).y0 for t in ax.get_xticklabels() if t.get_text()]
    xb   = fig.transFigure.inverted().transform((0, min(bots)))[1]
    for lg in fig.legends:
        lb = lg.get_window_extent(r).transformed(fig.transFigure.inverted())
        if lb.y1 < xb: xb = min(xb, lb.y0)
    LH = fs * 1.2 / (72 * fig.get_figheight())
    pr = fig.text(0, 0, '0', fontsize=fs); fig.canvas.draw()
    CW = pr.get_window_extent(fig.canvas.get_renderer()).width / Wpx; pr.remove()
    def w(t, size=fs):
        tt = fig.text(0, 0, t, fontsize=size); fig.canvas.draw()
        v  = tt.get_window_extent(fig.canvas.get_renderer()).width / Wpx; tt.remove(); return v
    URL   = 'movingfrontiers.substack.com'; UFS = fs * 1.2
    x0    = 0.012; right = 1.0 - 70.0 / Wpx
    full  = right - x0
    lastmax = right - w(URL, UFS) - 2.0 * CW - x0
    lines = []
    for para in cap.split(chr(10)):
        cur = ''
        for word in para.split():
            z = (cur + ' ' + word).strip()
            if w(z) <= full or not cur: cur = z
            else: lines.append(cur); cur = word
        lines.append(cur)
    for _ in range(400):
        if w(lines[-1]) > lastmax and ' ' in lines[-1]:
            h, _, t = lines[-1].rpartition(' '); lines[-1] = h; lines.append(t); continue
        if len(lines) >= 2 and w(lines[-2]) > lastmax and ' ' in lines[-2]:
            h, _, t = lines[-2].rpartition(' ')
            lines[-2] = h; lines[-1] = (t + ' ' + lines[-1]).strip(); continue
        break
    if len(lines) >= 2:
        while ' ' in lines[-2]:
            h, _, t = lines[-2].rpartition(' ')
            cand = (t + ' ' + lines[-1]).strip()
            if w(cand) > lastmax: break
            if abs(w(cand) - w(h)) >= abs(w(lines[-1]) - w(lines[-2])): break
            lines[-2] = h; lines[-1] = cand
    top  = xb - gap_lines * LH
    objs = [fig.text(x0, top - i * LH, ln, fontsize=fs, color='#666', va='top')
            for i, ln in enumerate(lines)]
    fig.canvas.draw()
    lb = objs[-1].get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
    # watermark sits on the same baseline as the last caption line
    fig.text(right, lb.y0, URL, ha='right', va='bottom', fontsize=UFS, color='#999')
    assert lb.y0 > 0.004, 'caption runs off the canvas'
    print('  caption %d lines' % len(lines))


def title_band(path, title, sub, tf=0.0285, sf=0.0168):
    import os as _os
    from matplotlib import font_manager as _fm
    def _dejavu(stem):
        p = _os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf', stem)
        if _os.path.exists(p): return p
        try:
            q = _fm.findfont(_fm.FontProperties(family='DejaVu Sans',
                weight=('bold' if 'Bold' in stem else 'normal')), fallback_to_default=False)
            if _os.path.basename(q) == stem and _os.path.exists(q): return q
        except Exception: pass
        p = _os.path.join('/usr/share/fonts/truetype/dejavu', stem)
        if _os.path.exists(p): return p
        raise FileNotFoundError('DejaVu font not found: ' + stem)
    FB = _dejavu('DejaVuSans-Bold.ttf'); FR = _dejavu('DejaVuSans.ttf')
    assert _os.path.exists(FB) and _os.path.exists(FR), 'resolved DejaVu font files must exist'
    im = Image.open(path).convert('RGB')
    a  = np.array(im.convert('L')); rr = np.where((a < 250).sum(axis=1) > 0)[0]
    im = im.crop((0, 0, im.size[0], min(im.size[1], int(rr.max()) + 13)))
    W, H = im.size
    fs  = int(W * tf); f1 = ImageFont.truetype(FB, fs)
    fss = int(W * sf); f2 = ImageFont.truetype(FR, fss)
    dd  = ImageDraw.Draw(im); M = int(W * 0.03); LIM = W - 2 * M
    def wrap(t, f):
        o = []; cur = ''
        for x in t.split():
            z = (cur + ' ' + x).strip()
            if dd.textlength(z, font=f) <= LIM: cur = z
            else: o.append(cur); cur = x
        o.append(cur); return o
    tl  = wrap(title, f1); sl = wrap(sub, f2)
    lh  = int(fs * 1.25); lhs = int(fss * 1.35)
    bh  = int(fs * 0.85) + lh * len(tl) + int(fss * 0.55) + lhs * len(sl) + int(fs * 0.22)
    cv  = Image.new('RGB', (W, H + bh), 'white'); cv.paste(im, (0, bh))
    dr  = ImageDraw.Draw(cv); y = int(fs * 0.85) + 3
    for ln in tl: dr.text((M, y), ln, font=f1, fill=(45, 45, 45)); y += lh
    y  += int(fss * 0.4)
    for ln in sl: dr.text((M, y), ln, font=f2, fill=(100, 100, 100)); y += lhs
    cv.save(path, optimize=True)
    print('  wrote %s  %dx%d' % (path, cv.size[0], cv.size[1]))


# ------------------------------------------------------------------ build chart
PNG = 'chart-fdi-sri-lanka.png'

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 14,
                     'axes.edgecolor': '#888', 'axes.linewidth': 1.0,
                     'figure.facecolor': 'white',
                     'xtick.labelsize': 12, 'ytick.labelsize': 12})

fig, ax = plt.subplots(figsize=(9.6, 6.3), dpi=200)

# panel style (single panel, no projection band, no gridlines)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.set_xlim(1969, 2026)
ax.set_ylim(-0.3, 3.4)
ax.set_xticks([1970, 1980, 1990, 2000, 2010, 2020])
ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
ax.set_yticklabels(['0', '0.5', '1.0', '1.5', '2.0', '2.5', '3.0%'])
# no x-axis title, no y-axis title

# zero reference
ax.axhline(0, color='#aaa', lw=0.8, zorder=1)

# 1970-2024 average (dashed red)
ax.axhline(avg, color=RED, lw=1.3, ls=(0, (5, 3)), zorder=3)
ax.text(1970.3, avg + 0.07, '1970\u20132024\navg: %.2f%%' % avg,
        fontsize=10, color=RED, ha='left', va='bottom', zorder=7,
        fontweight='bold', linespacing=1.25)

# main line
ax.plot(years, vals, color=INDIGO, lw=2.9, zorder=5, solid_capstyle='round')

# peak marker: 1997
ax.plot([peak_yr], [peak_val], 'o', mfc='white', mec=INDIGO, mew=2.6, ms=13,
        zorder=30, clip_on=False)
ax.text(peak_yr + 0.8, peak_val + 0.06, '%.1f%%\n%d' % (peak_val, peak_yr),
        fontsize=10.5, fontweight='bold', color=INDIGO,
        ha='left', va='bottom', linespacing=1.25, zorder=9)

# 2024 endpoint — label below the dot, shifted right of it
ax.plot([2024], [DATA[2024]], 'o', mfc=INDIGO, mec=INDIGO, ms=9,
        zorder=30, clip_on=False)
ax.text(2024.6, DATA[2024] - 0.14, '%.1f%%\n%d' % (DATA[2024], 2024),
        fontsize=10.5, fontweight='bold', color=INDIGO,
        ha='left', va='top', linespacing=1.25, zorder=9)

fig.tight_layout(rect=[0, 0.300, 1, 0.985])
caption(fig, ax, SRC + NOTE, fs=7.8, gap_lines=2.0)
fig.savefig(PNG, dpi=200); plt.close(fig)
title_band(PNG, TITLE, SUB)
