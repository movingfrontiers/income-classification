"""Landscape version: linear and log panels stacked as rows, income on x.
Malaysia highlighted in both. No title band, no subtitle, no legend."""
import pandas as pd, numpy as np, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.family':'DejaVu Sans',
    'axes.edgecolor':'#888','axes.linewidth':1.0,
    'figure.facecolor':'white','axes.facecolor':'white'})

COL = {'L':'#C62828','LM':'#F9A825','UM':'#00897B','H':'#283593'}
TH = (1175,4635,14375)                     # FY27 thresholds, 2025 GNI per capita
GRP = {'Low income':'L','Lower middle income':'LM',
       'Upper middle income':'UM','High income':'H'}
d = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
      'chart-13-the-high-income-line-is-not-a-finish-line.csv'))
g = pd.DataFrame({'name':d['economy'],
                  'base':d['gni_per_capita_usd_atlas_2025'].astype(float),
                  'pop':d['population_millions_2025'],
                  'cls':d['income_group_fy27'].map(GRP)})

XM = np.log10(1450) - 1.0
def area(pop_m):
    if pop_m < 10: return 10
    x = (np.log10(pop_m) - 1.0) / XM
    return 10 + x**3.4 * 2200

rng = np.random.default_rng(7)
g['yj'] = rng.uniform(0.17,0.92,len(g))
SIDE = {'China':'right','India':'right','United States':'right','Indonesia':'eleven',
        'Nigeria':'right','Pakistan':'left','Brazil':'left','Japan':'right',
        'Congo, Dem. Rep.':'right','Malaysia':'right','Bermuda':'left'}
PINY = {'China':0.68,'India':0.42,'United States':0.52,'Indonesia':0.72,
        'Nigeria':0.56,'Pakistan':0.32,'Brazil':0.62,'Japan':0.30,
        'Congo, Dem. Rep.':0.42,'Malaysia':0.20,'Bermuda':0.80}
g.loc[g['name'].isin(PINY),'yj'] = g.loc[g['name'].isin(PINY),'name'].map(PINY)
SHOW={'United States':'US','Congo, Dem. Rep.':'DR Congo'}

FIGW, FIGH = 8, 6.6
L_TOP, R_TOP = 140000, 140000
assert g['base'].max() <= L_TOP, 'linear scale no longer covers the maximum'

fig, axes = plt.subplots(2,1,figsize=(FIGW,FIGH))
BLW = 2.4*4
seg_specs=[]; panel_titles=[]
for ax, scale in zip(axes,['linear','log']):
    if scale=='linear':
        lo,hi = 0,L_TOP
    else:
        lo,hi = 200,R_TOP; ax.set_xscale('log')
    ax.set_xlim(lo,hi); ax.set_ylim(0,1)
    seg_specs.append((ax,[lo,TH[0],TH[1],TH[2],hi]))
    sub = g if scale=='log' else g[g['base']<=L_TOP]
    sub = sub.assign(_a=sub['pop'].apply(area)).sort_values('_a',ascending=False)
    for _,r in sub.iterrows():
        ax.scatter(r['base'],r['yj'],s=area(r['pop']),
                   facecolor=COL[r['cls']],alpha=0.45,
                   edgecolor='white',lw=0.5,zorder=3,clip_on=False)
    # labels
    lab = SIDE if scale=='log' else {}
    for _,r in g[g['name'].isin(lab)].iterrows():
        if scale=='linear' and r['base']>L_TOP: continue
        nm = SHOW.get(r['name'],r['name'])
        side = lab[r['name']]
        rad = np.sqrt(area(r['pop']))/2
        if side=='eleven':
            dx,dy,ha,va = -0.72*rad-2, 0.72*rad+2, 'right','bottom'
        else:
            off = 3 + rad
            dx = off if side=='right' else -off
            dy = 0
            ha = 'left' if side=='right' else 'right'; va='center'
        ax.annotate(nm,(r['base'],r['yj']),xytext=(dx,dy),
            textcoords='offset points',ha=ha,va=va,
            fontsize=8.6,fontweight='bold',color='#555',zorder=7)
    if scale=='log':
        ax.set_xticks([1175,4635,14375,R_TOP])
        ax.set_xticklabels(['$1,175','$4,635','$14,375','$140,000'],fontsize=10)
        ax.minorticks_off()
        panel_lbl='Log scale: equal widths are equal ratios'
    else:
        ax.set_xticks([4635,14375,L_TOP])
        ax.set_xticklabels(['\n$4,635','$14,375','$140,000'],fontsize=10)
        panel_lbl='Linear scale: equal widths are equal dollars'
    ax.set_yticks([])
    for s in ['top','right','left','bottom']: ax.spines[s].set_visible(False)
    ax.tick_params(axis='x',length=0,pad=5)
    panel_titles.append(ax.text(0.0,1.03,panel_lbl,transform=ax.transAxes,
        fontsize=11.5,fontweight='bold',color='#444',va='bottom'))

# ---------------- caption / watermark, project-standard format ----------------
FS = 7.0                     # caption font size
WMFS = FS*1.2                # watermark = caption size x 1.2
H_OUT = FIGH*200; W_OUT = FIGW*200
lh_fig = 22.0/H_OUT          # caption line pitch, published standard

CAP_TEXT = ("Source: World Bank OGHIST classification and income thresholds, 1 July 2026 "
 "(FY27, 2025 GNI per capita, Atlas method, current US\$); GNI per capita and population "
 "from World Bank WDI, July 2026 release. Note: Each bubble is one of the 207 classified "
 "economies with a reported income level, positioned by its latest GNI per capita. "
 "Colored segments mark the four income groups at the FY27 thresholds "
 "of \$1,175, \$4,635 and \$14,375; the high-income group has no upper bound and both scales "
 "end at Bermuda (\$139,370), the highest observed income. Argentina and Turkiye, "
 "upper-middle income in the FY27 classification, already report 2025 income above the "
 "threshold and sit above the high-income line.")
CLOSERS = ["All values refer to the 2025 data year.",
           "Bubble areas are comparable across the two panels.",
           "The vertical position within each panel carries no information."]

fig.canvas.draw(); ren=fig.canvas.get_renderer()
CW,CH = fig.canvas.get_width_height()
_probe=fig.text(0.3,0.5,'',fontsize=FS)
_wcache={}
def wpx(t,fs):
    key=(t,fs)
    if key not in _wcache:
        _probe.set_text(t); _probe.set_fontsize(fs)
        _wcache[key]=_probe.get_window_extent(ren).width/CW
    return _wcache[key]
SPACE = wpx('n n',FS)-wpx('nn',FS)
X0 = 0.012
FULL = 1-70/1600                                # right margin 70 px
WM_X1 = 1-70/1600
wm_w = wpx('movingfrontiers.substack.com',WMFS)
MOVI = wpx('movi',WMFS)
SHORT = WM_X1 - wm_w - MOVI                     # last two lines stop one movi short

def greedy(words,limit):
    lines=[]; cur=[]; w=0.0
    for word in words:
        ww=wpx(word,FS)
        add=ww if not cur else ww+SPACE
        if X0+w+add<=limit or not cur:
            cur.append(word); w+=add
        else:
            lines.append(' '.join(cur)); cur=[word]; w=ww
    if cur: lines.append(' '.join(cur))
    return lines

text=CAP_TEXT; ci=0
while True:
    words=text.split()
    full_lines=greedy(words,FULL)
    lead, tail = full_lines[:-1], full_lines[-1]
    tail_lines=greedy(tail.split(),SHORT)
    if len(tail_lines)==2:
        pen_fill=(X0+ (wpx(tail_lines[0],FS))) >= X0+0.70*(SHORT-X0)
        if pen_fill: break
    if ci>=len(CLOSERS):
        break
    text=text+' '+CLOSERS[ci]; ci+=1
cap_lines=lead+tail_lines
n=len(cap_lines)

# vertical placement: caption top exactly 2.00 line-heights below the lowest axis element
cap_h = n*lh_fig
rect_bottom = 2*lh_fig + cap_h + 0.006
for attempt in range(4):
    fig.tight_layout(rect=[0.015,rect_bottom,0.985,0.975])
    fig.subplots_adjust(hspace=0.42)
    fig.canvas.draw()
    lows=[]
    for ax in axes:
        for a in list(ax.get_xticklabels())+list(ax.texts):
            bb=a.get_window_extent(ren)
            lows.append(bb.y0/CH)
        lows.append(ax.get_window_extent(ren).y0/CH)
    lowest=min(lows)
    cap_top = lowest - 2.0*lh_fig
    cap_bottom = cap_top - cap_h
    if cap_bottom > 0.004: break
    rect_bottom += (0.006 - cap_bottom)
assert cap_bottom > 0.004, 'caption does not fit'

_probe.remove()
arts=[]
for i,ln in enumerate(cap_lines):
    yb = cap_top - (i+1)*lh_fig + lh_fig*0.22        # baseline within the line box
    arts.append(fig.text(X0,yb,ln,fontsize=FS,color='#666',ha='left',va='baseline'))
wm = fig.text(WM_X1, cap_top - n*lh_fig + lh_fig*0.22,
              'movingfrontiers.substack.com',fontsize=WMFS,color='#999999',
              ha='right',va='baseline')
fig.canvas.draw()

# colored bottom-edge segments with half-character gaps, in display space
half_gap = 0.5*FS*fig.dpi/72
for ax,edges in seg_specs:
    tr=ax.transData; inv=tr.inverted()
    for k,(a0,a1,grp) in enumerate(zip(edges[:-1],edges[1:],['L','LM','UM','H'])):
        p0=tr.transform((a0,0))[0]+(half_gap/2 if k>0 else 0)
        p1=tr.transform((a1,0))[0]-(half_gap/2 if k<3 else 0)
        d0=inv.transform((p0,0))[0]; d1=inv.transform((p1,0))[0]
        ax.plot([d0,d1],[0.015,0.015],color=COL[grp],lw=BLW,
                solid_capstyle='butt',zorder=2,clip_on=False)
fig.canvas.draw()

# ---- project-standard watermark asserts ----
wmb=wm.get_window_extent(ren)
for ln_art in arts[-2:]:
    gap=(wmb.x0 - ln_art.get_window_extent(ren).x1)/CW
    assert gap >= MOVI*0.98, 'last-two-line gap below one movi width: %.4f'%gap
pen_w=(arts[-2].get_window_extent(ren).x1)/CW
assert pen_w >= X0+0.70*(SHORT-X0)*0.98, 'second-to-last line underfilled'
# same baseline: both drawn va=baseline at identical y
assert abs(wm.get_position()[1]-arts[-1].get_position()[1])<1e-9
print('caption lines: %d (closers appended: %d), gap(last)=%.4f movi=%.4f'%(
      n,ci,(wmb.x0-arts[-1].get_window_extent(ren).x1)/CW,MOVI))
print('caption bottom %.4f, top gap below axes = 2.00 lines by construction'%cap_bottom)

ax1=axes[1]
texts=[t for t in ax1.texts if t.get_fontweight()=='bold' and t.get_fontsize()==8.6]
texts+=[t for t in axes[0].texts if t.get_fontweight()=='bold' and t.get_fontsize()==8.6]
import itertools
for a,b in itertools.combinations(texts,2):
    if a.axes is not b.axes: continue
    ba,bb=a.get_window_extent(ren),b.get_window_extent(ren)
    ox=max(0,min(ba.x1,bb.x1)-max(ba.x0,bb.x0)); oy=max(0,min(ba.y1,bb.y1)-max(ba.y0,bb.y0))
    assert ox*oy==0, 'label overlap %s/%s'%(a.get_text(),b.get_text())
print('labels clean:',len(texts))

OUT='chart-1b-the-country-income-classification-landscape-titled.png'
fig.savefig(OUT,dpi=200)
plt.close(fig)
from PIL import Image, ImageDraw, ImageFont

FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title="The high-income line is not a finish line"
subtitle='Classified economies by GNI per capita against FY27 income thresholds, sized by population and on a linear and a logarithmic scale'
im=Image.open(OUT).convert('RGB'); W,H=im.size
fs=int(W*0.031); font=ImageFont.truetype(FB,fs)
fss=int(W*0.0225); fonts=ImageFont.truetype(FR,fss)
tmp=ImageDraw.Draw(im)
def wrap(text,f):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if tmp.textlength(t,font=f)<=W-2*int(W*0.03): cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
lines=wrap(title,font); slines=wrap(subtitle,fonts)
lh=int(fs*1.25); lhs=int(fss*1.3)
band=int(fs*0.85)+lh*len(lines)+int(fss*0.5)+lhs*len(slines)+int(fs*0.03)
canvas=Image.new('RGB',(W,H+band),'white'); canvas.paste(im,(0,band))
dr=ImageDraw.Draw(canvas); y=int(fs*0.85)
for ln in lines: dr.text((int(W*0.03),y),ln,font=font,fill=(45,45,45)); y+=lh
y+=int(fss*0.35)
for ln in slines: dr.text((int(W*0.03),y),ln,font=fonts,fill=(100,100,100)); y+=lhs
canvas.save(OUT,optimize=True)
print('done titled',canvas.size)
