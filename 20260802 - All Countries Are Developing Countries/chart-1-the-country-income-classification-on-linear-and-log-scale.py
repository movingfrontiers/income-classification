"""v6: raised panel titles, tightened top gap, fixed ranges (90k / 140k),
two-column legend block (income groups left, population size key right),
trimmed note."""
import pandas as pd, numpy as np, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Ellipse

plt.rcParams.update({'font.family':'DejaVu Sans',
    'axes.edgecolor':'#888','axes.linewidth':1.0,
    'figure.facecolor':'white','axes.facecolor':'white'})

COL = {'L':'#C62828','LM':'#F9A825','UM':'#00897B','H':'#283593'}
LEG = {'H':'High-income economies','UM':'Upper-middle-income economies',
       'LM':'Lower-middle-income economies','L':'Low-income economies'}
TH = (1175,4635,14375)                     # FY27 thresholds, 2025 GNI per capita
GRP = {'Low income':'L','Lower middle income':'LM',
       'Upper middle income':'UM','High income':'H'}
d = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
      'chart-1-the-country-income-classification-on-linear-and-log-scale.csv'))
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
g['xj'] = rng.uniform(0.06,0.94,len(g))
SIDE = {'China':'right','India':'right','United States':'right','Indonesia':'eleven',
        'Nigeria':'right','Pakistan':'left','Brazil':'right','Japan':'right',
        'Congo, Dem. Rep.':'right'}
PINX = {'China':0.58,'India':0.42,'United States':0.52,'Indonesia':0.70,
        'Nigeria':0.56,'Pakistan':0.36,'Brazil':0.30,'Japan':0.30,
        'Congo, Dem. Rep.':0.42}
g.loc[g['name'].isin(PINX),'xj'] = g.loc[g['name'].isin(PINX),'name'].map(PINX)

FIGW, FIGH = 8, 10.6
fig, axes = plt.subplots(1,2,figsize=(FIGW,FIGH))
BLW = 2.4*4
L_TOP, R_TOP = 90000, 140000
CUT = g[g['base']>L_TOP].sort_values('base',ascending=False)['name'].tolist()
print('cut off on the left panel:',CUT)
assert CUT == ['Bermuda','Liechtenstein','Switzerland','Norway','Luxembourg']
seg_specs=[]; panel_titles=[]
for ax, scale in zip(axes,['linear','log']):
    if scale=='linear':
        lo,hi = 0,L_TOP; edge_x = 0.02
    else:
        lo,hi = 200,R_TOP; ax.set_yscale('log'); edge_x = 0.98
    ax.set_ylim(lo,hi); ax.set_xlim(0,1)
    seg_specs.append((ax,edge_x,[lo,TH[0],TH[1],TH[2],hi]))
    sub = g if scale=='log' else g[g['base']<=L_TOP]
    sub = sub.assign(_a=sub['pop'].apply(area)).sort_values('_a',ascending=False)
    print('%s panel: %d economies, of which L: %d' %
          (scale, len(sub), (sub['cls']=='L').sum()))
    for _,r in sub.iterrows():
        ax.scatter(r['xj'],r['base'],s=area(r['pop']),facecolor=COL[r['cls']],
                   alpha=0.45,edgecolor='white',lw=0.5,zorder=3,clip_on=False)
    if scale=='log':
        SHOW={'United States':'US','Congo, Dem. Rep.':'DR Congo'}
        for _,r in g[g['name'].isin(SIDE)].iterrows():
            nm = SHOW.get(r['name'],r['name'])
            side = SIDE[r['name']]
            rad = np.sqrt(area(r['pop']))/2
            if side=='eleven':
                dx,dy,ha,va = -0.72*rad-2, 0.72*rad+2, 'right','bottom'
            else:
                off = 3 + rad
                dx = off if side=='right' else -off
                dy = -10 if r['name']=='China' else 0
                ha = 'left' if side=='right' else 'right'; va='center'
            ax.annotate(nm,(r['xj'],r['base']),xytext=(dx,dy),
                textcoords='offset points',ha=ha,va=va,
                fontsize=8.6,fontweight='bold',color='#555',zorder=6)
        ax.set_yticks([1175,4635,14375,R_TOP])
        ax.set_yticklabels(['$1,175','$4,635','$14,375','$140,000'],fontsize=10)
        ax.minorticks_off(); ax.yaxis.tick_right()
        panel_lbl='Log scale:\nequal heights are equal ratios'
    else:
        ax.set_yticks([1175,4635,14375,L_TOP])
        ax.set_yticklabels(['$1,175','$4,635','$14,375','$90,000'],fontsize=10)
        panel_lbl='Linear scale:\nequal heights are equal dollars'
    ax.set_xticks([])
    for s in ['top','right','left','bottom']: ax.spines[s].set_visible(False)
    ax.tick_params(axis='y',length=0,pad=6)
    panel_titles.append(ax.text(0.0,1.012,panel_lbl,transform=ax.transAxes,
        fontsize=11.5,fontweight='bold',color='#444',va='bottom',linespacing=1.3))

# ---------------- bottom stack ----------------
FS = 7.0
H_OUT = FIGH*200
lh_fig = 22.0/H_OUT
ch_fig = (FS*200/72)/H_OUT
y0 = 0.008

cap_lines=[
 'Source: World Bank OGHIST classification and income thresholds, 1 July 2026 (FY27, 2025 GNI per capita, Atlas method, current',
 'US$); GNI per capita and population from World Bank WDI, July 2026 release.',
 'Note: Each bubble is one of the 207 classified economies with a reported income level, positioned by its latest GNI per capita.',
 'Colored edges mark the four income groups at the FY27 thresholds of $1,175, $4,635 and $14,375; the high-income group has no',
 'upper bound. The left panel is truncated at $90,000: Bermuda, Liechtenstein, Switzerland, Norway and Luxembourg lie above it and',
 'appear only in the right panel. Argentina and Turkiye, upper-middle income in the FY27 classification, already report 2025 income',
 'above the threshold and sit above the high-income line.']

fig.canvas.draw(); ren=fig.canvas.get_renderer()
CW,CH = fig.canvas.get_width_height()
def fx(v): return v/CW
probe=fig.text(0.5,0.5,'n'*20,fontsize=FS); fig.canvas.draw()
cw = fx(probe.get_window_extent(ren).width)/20; probe.remove()
wm=fig.text(1-95/1600,y0,'movingfrontiers.substack.com',fontsize=FS,color='#999',
            ha='right',va='bottom')
fig.canvas.draw(); wm_x0f=fx(wm.get_window_extent(ren).x0)
limit_f=wm_x0f-4*cw

last=cap_lines.pop(); words=last.split(); head=[]
for w in words:
    t=fig.text(0.012,0.5,' '.join(head+[w]),fontsize=FS); fig.canvas.draw()
    wf=fx(t.get_window_extent(ren).width); t.remove()
    if 0.012+wf<=limit_f: head.append(w)
    else: break
split_binding = len(head) < len(words)
cap_lines.append(' '.join(head))
if split_binding:
    cap_lines.append(' '.join(words[len(head):]))

arts=[]; n=len(cap_lines)
for i,ln in enumerate(cap_lines):
    arts.append(fig.text(0.012,y0+(n-1-i)*lh_fig,ln,fontsize=FS,color='#666',
                         ha='left',va='bottom',linespacing=1.13))
if split_binding:
    wm.set_position((1-95/1600, y0+lh_fig-0.5*ch_fig))
cap_top = y0 + n*lh_fig

# legend column (left, high to low) and population size key (right)
handles=[Patch(facecolor=COL[grp],edgecolor='none',label=LEG[grp])
         for grp in ['H','UM','LM','L']]
key=[(1450,'1.4bn'),(500,'500m'),(100,'100m'),(10,'10m')]   # large to small
def r_fig(a):
    r_px=np.sqrt(a/np.pi)*200/72
    return r_px/(FIGW*200), r_px/H_OUT
rh_max=r_fig(area(1450))[1]
lab_h=0.011
GAP_COLS=0.035
keyW=sum(2*r_fig(area(p))[0] for p,_ in key)+0.024*(len(key))
prov = cap_top + 1.5*lh_fig + 0.02
leg = fig.legend(handles=handles,loc='lower left',bbox_to_anchor=(0.08,prov),
    ncol=1,frameon=False,fontsize=10.5,handlelength=1.6,handleheight=1.1,
    labelspacing=0.55)
fig.canvas.draw()
lb=leg.get_window_extent(ren)
legH=(lb.y1-lb.y0)/CH; legW=(lb.x1-lb.x0)/CW
undershoot = max(0.0,(rh_max+0.007+lab_h)-legH/2)
lb0 = cap_top + 1.5*lh_fig + undershoot - ch_fig      # one caption char lower
x_left = 0.5 - (legW+GAP_COLS+keyW)/2                 # centre the whole block
leg.set_bbox_to_anchor((x_left,lb0))
fig.canvas.draw()
lb=leg.get_window_extent(ren)
ky=(lb.y0+lb.y1)/2/CH
kx=lb.x1/CW + GAP_COLS
for pop,lab in key:
    rw,rh=r_fig(area(pop)); kx+=rw+0.012
    fig.add_artist(Ellipse((kx,ky),2*rw,2*rh,facecolor='#BBB',alpha=0.6,
                   edgecolor='white',lw=0.5))
    fig.text(kx,ky-rh-0.007,lab,fontsize=8.6,color='#555',ha='center',va='top')
    kx+=rw+0.012
block_top = max(lb.y1/CH, ky+rh_max)

fig.tight_layout(rect=[0.02,block_top+0.012,0.98,0.972]); fig.subplots_adjust(wspace=0.08)
fig.canvas.draw()

# panel titles: one character height higher; halve the top whitespace
tb0 = max(t.get_window_extent(ren).y1 for t in panel_titles)
w0 = CH - tb0                                   # current whitespace above titles
ch_t = 11.5*fig.dpi/72                          # panel-title character height, live px
for t,ax in zip(panel_titles,axes):
    axh = ax.get_window_extent(ren).height
    x,y = t.get_position()
    t.set_position((x, y + ch_t/axh))
target = w0/2
rect_top = 0.972
for _ in range(4):
    fig.tight_layout(rect=[0.02,block_top+0.012,0.98,min(0.996,rect_top)])
    fig.subplots_adjust(wspace=0.08)
    fig.canvas.draw()
    tb1 = max(t.get_window_extent(ren).y1 for t in panel_titles)
    err = (CH - tb1) - target
    if abs(err) < 1.2: break
    rect_top += err/CH
print('top whitespace: %.1f -> %.1f px (target %.1f)' % (w0, CH-tb1, target))
assert abs((CH-tb1)-target) < 2.5

# colored edge segments with half-character gaps at internal boundaries
half_gap = 0.5*FS*fig.dpi/72
for ax,edge_x,edges in seg_specs:
    tr=ax.transData; inv=tr.inverted()
    for k,(a0,a1,grp) in enumerate(zip(edges[:-1],edges[1:],['L','LM','UM','H'])):
        p0=tr.transform((0,a0))[1]+(half_gap/2 if k>0 else 0)
        p1=tr.transform((0,a1))[1]-(half_gap/2 if k<3 else 0)
        d0=inv.transform((0,p0))[1]; d1=inv.transform((0,p1))[1]
        ax.plot([edge_x,edge_x],[d0,d1],color=COL[grp],lw=BLW,
                solid_capstyle='butt',zorder=2,clip_on=False)
fig.canvas.draw()

# ---- checks ----
wmb=wm.get_window_extent(ren); lastb=arts[-1].get_window_extent(ren)
ref=arts[-2] if split_binding else arts[-1]
gapc=(wmb.x0-ref.get_window_extent(ren).x1)/CW/cw
print('caption-to-watermark clearance: %.2f chars (binding split: %s)' % (gapc,split_binding))
assert gapc>3.8 and fx(lastb.x1)<fx(wmb.x0)
key_lab_bottom=ky-rh_max-0.007-lab_h
assert key_lab_bottom > cap_top + lh_fig*0.4
assert lb.y0/CH > cap_top + lh_fig*0.4
ax0=axes[0].get_window_extent(ren)
assert ax0.y0 > max(lb.y1, (ky+rh_max)*CH), 'axes overlap legend block'
texts=[t for t in axes[1].texts if t.get_fontweight()=='bold' and t.get_fontsize()==8.6]
import itertools
for a,b in itertools.combinations(texts,2):
    ba,bb=a.get_window_extent(ren),b.get_window_extent(ren)
    ox=max(0,min(ba.x1,bb.x1)-max(ba.x0,bb.x0)); oy=max(0,min(ba.y1,bb.y1)-max(ba.y0,bb.y0))
    assert ox*oy==0, 'label overlap %s/%s'%(a.get_text(),b.get_text())
china=[t for t in texts if t.get_text()=='China'][0].get_window_extent(ren)
yline=axes[1].transData.transform((0,14375))[1]
assert china.y1 < yline-1
print('all label checks pass')

OUT='chart-1-the-country-income-classification-on-linear-and-log-scale.png'
fig.savefig(OUT,dpi=200)
plt.close(fig)

# ---- PIL title band ----
from PIL import Image, ImageDraw, ImageFont

FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title="The World Bank's country income classification"
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

# lower the watermark by half a character (published format)
im=Image.open(OUT).convert('RGB')
import numpy as np
a=np.array(im).astype(int); H2,W2,_=a.shape
reg=a[int(H2*0.88):H2, W2-560:W2]
core=((np.abs(reg[:,:,0]-153)<=12)&(np.abs(reg[:,:,1]-153)<=12)&(np.abs(reg[:,:,2]-153)<=12))
dark=(reg.max(axis=2)<135); dd=dark.copy()
for sh in (1,2):
    for axn in (0,1): dd=dd|np.roll(dark,sh,axn)|np.roll(dark,-sh,axn)
n4=(np.roll(core&~dd,1,0).astype(int)+np.roll(core&~dd,-1,0)
    +np.roll(core&~dd,1,1)+np.roll(core&~dd,-1,1))
solid=(core&~dd)&(n4>=2)
ys,xs=np.where(solid)
y0=int(H2*0.88)+ys.min(); y1=int(H2*0.88)+ys.max()
x0=W2-560+xs.min(); x1=W2-560+xs.max()
delta=max(1,round(0.5*(y1-y0+1))); pad=4
patch=im.crop((x0-pad,y0-pad,x1+pad+1,y1+pad+1))
canvas=Image.new('RGB',(W2,H2+delta),'white'); canvas.paste(im,(0,0))
canvas.paste(Image.new('RGB',(x1-x0+2*pad+1,y1-y0+2*pad+1),'white'),(x0-pad,y0-pad))
canvas.paste(patch,(x0-pad,y0-pad+delta))
canvas.save(OUT,optimize=True)
print('done',canvas.size)
