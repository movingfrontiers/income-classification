# =============================================================================
# Sri Lanka: poverty at the three global lines, chained across MPO vintages, 2017-2028
#
# Provenance, frozen vintage. Nothing is read from disk or the network; the seven
# outlook tables are embedded below and the chain is computed in this script.
#   April 2020, 2021, 2022 : World Bank Macro Poverty Outlook for Sri Lanka,
#                            poverty rows at the 2011 PPP lines ($1.90, $3.20, $5.50).
#   April 2023, 2024, 2025 : same, at the 2017 PPP lines ($2.15, $3.65, $6.85).
#   April 2026             : same, at the 2021 PPP lines ($3.00, $4.20, $8.30).
#   Vintage freeze date    : 29 August 2026. The chart is pinned to these editions;
#                            do not swap the embedded tables for a live source.
#
# Construction. Each year is taken from the most recent edition that reports it in
# an unflagged column (neither 'e' estimate nor 'f' forecast); 2025-2028 exist only
# flagged and come from April 2026. Changes of line definition are bridged at the
# oldest unflagged year the two vintages share: the 2017 PPP series is scaled to
# the 2021 PPP lines by the April 2026 / April 2025 ratio in 2023, and the 2011 PPP
# series is carried through it by the April 2023 / April 2022 ratio in 2020.
#
# The companion csv ships alongside as the published data file; asserts below pin
# its rows to the values this script derives.
# =============================================================================
"""Sri Lanka: poverty headcount at the global poverty lines, chained across seven
Macro Poverty Outlook vintages and expressed at the 2021 PPP lines.

Writes chart-sri-lanka-poverty-three-lines.png.
Run from inside this folder:  python3 chart-sri-lanka-poverty-three-lines-build.py
"""
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image, ImageDraw, ImageFont

SRC=("Source: World Bank, Macro Poverty Outlook for Sri Lanka, April 2020 through April 2026 editions; "
"author's calculations."+chr(10))

# ---------------------------------------------------------------- shared helpers

def place_marks(fig, ax, YY, series, marks, fontsize=10.5, pad_frac=0.008, align_x=None, override=None, dots=True, dotsize=8.5):
    """Put a value label near its point, clear of every series and every other label."""
    inv=ax.transData.inverted()
    span=ax.get_ylim()[1]-ax.get_ylim()[0]
    pad=span*pad_frac
    out=[]; fixed=[]
    def box(t):
        bb=t.get_window_extent(fig.canvas.get_renderer())
        (a0,b0)=inv.transform((bb.x0,bb.y0)); (a1,b1)=inv.transform((bb.x1,bb.y1))
        return a0,a1,min(b0,b1),max(b0,b1)
    def bad(b,skip=None):
        a0,a1,lo,hi=b
        if a1>ax.get_xlim()[1] or a0<ax.get_xlim()[0]: return True
        if hi>ax.get_ylim()[1] or lo<ax.get_ylim()[0]: return True
        xs=[q for q in YY if a0-0.35<=q<=a1+0.35]
        for s in series:
            if any(lo-pad<=s[YY.index(q)]<=hi+pad for q in xs): return True
        gx,gy=0.4,span*0.018
        for j,ot in enumerate(out):
            if j==skip: continue
            ob=box(ot)
            if a0-gx<ob[1] and ob[0]<a1+gx and lo-gy<ob[3] and ob[2]<hi+gy: return True
        return False
    for item in marks:
        yr,txt,prefer,own,col=item
        yv=own[YY.index(yr)]
        if dots:
            ax.plot([yr],[yv],'o',color=col,ms=dotsize,zorder=30,
                    markeredgecolor='white',markeredgewidth=1.1,clip_on=False)
        cands=[]
        if override and (col,yr) in override:
            ox,oy,oha,ova=override[(col,yr)]; cands=[(ox,oy,oha,ova)]
        elif align_x is not None and yr in align_x:
            lx,ha=align_x[yr]
            for st in (0.045,0.065,0.088,0.113,0.140,0.170,0.203,0.240,0.280):
                for side in ([1,-1] if prefer=='above' else [-1,1]):
                    cands.append((lx,yv+side*span*st,ha,'bottom' if side>0 else 'top'))
            cands.append((lx,yv,ha,'center'))
        else:
            for st in (0.050,0.070,0.095,0.125,0.160,0.200,0.245):
                for side in ([1,-1] if prefer=='above' else [-1,1]):
                    for dx,ha in ((-0.3,'right'),(0.3,'left'),(0.0,'center'),
                                  (1.2,'left'),(-1.2,'right'),(2.4,'left'),(-2.4,'right'),
                                  (3.8,'left'),(-3.8,'right')):
                        xr=min(max(yr+dx,YY[0]),YY[-1])
                        cands.append((xr,own[YY.index(int(round(xr)))]+side*span*st,ha,
                                      'bottom' if side>0 else 'top'))
        t=ax.text(0,0,txt,fontsize=fontsize,fontweight='bold',color=col,linespacing=1.25,zorder=9)
        out.append(t)
        if override and (col,yr) in override:
            lx,ly,ha,va=cands[0]
            t.set_position((lx,ly)); t.set_ha(ha); t.set_va(va); fig.canvas.draw()
            fixed.append(len(out)-1); continue
        ok=False
        for lx,ly,ha,va in cands:
            t.set_position((lx,ly)); t.set_ha(ha); t.set_va(va); fig.canvas.draw()
            if not bad(box(t),skip=len(out)-1): ok=True; break
        if not ok:
            lx,ly,ha,va=cands[0]
            t.set_position((lx,ly)); t.set_ha(ha); t.set_va(va); fig.canvas.draw()
    for _ in range(60):
        fig.canvas.draw(); moved=False
        for i,t in enumerate(out):
            if i in fixed: continue
            if bad(box(t),skip=i):
                x,y=t.get_position(); up=t.get_va()!='top'
                ny=y+(span*0.030 if up else -span*0.030)
                if ax.get_ylim()[0]<ny<ax.get_ylim()[1]: t.set_y(ny); moved=True
        if not moved: break
    return out

def caption(fig, ax, cap, fs=7.8, gap_lines=2.0, url_gap=2.0):
    """Moving Frontiers caption block: every line runs full width except the last two,
    which stop short so the watermark can sit on the baseline of the last line."""
    fig.canvas.draw(); r=fig.canvas.get_renderer()
    Wpx=fig.get_figwidth()*fig.dpi
    bots=[t.get_window_extent(r).y0 for t in ax.get_xticklabels() if t.get_text()]
    xb=fig.transFigure.inverted().transform((0,min(bots)))[1]
    for lg in fig.legends:
        lb=lg.get_window_extent(r).transformed(fig.transFigure.inverted())
        if lb.y1<xb: xb=min(xb,lb.y0)
    LH=fs*1.2/(72*fig.get_figheight())
    pr=fig.text(0,0,'0',fontsize=fs); fig.canvas.draw()
    CW=pr.get_window_extent(fig.canvas.get_renderer()).width/Wpx; pr.remove()
    def w(t,size=fs):
        tt=fig.text(0,0,t,fontsize=size); fig.canvas.draw()
        v=tt.get_window_extent(fig.canvas.get_renderer()).width/Wpx; tt.remove(); return v
    URL='movingfrontiers.substack.com'; UFS=fs*1.2
    x0=0.012; right=1.0-70.0/Wpx
    full=right-x0
    lastmax=right-w(URL,UFS)-url_gap*CW-x0
    lines=[]
    for para in cap.split(chr(10)):
        cur=''
        for word in para.split():
            z=(cur+' '+word).strip()
            if w(z)<=full or not cur: cur=z
            else: lines.append(cur); cur=word
        lines.append(cur)
    for _ in range(400):
        if w(lines[-1])>lastmax and ' ' in lines[-1]:
            h,_,t=lines[-1].rpartition(' '); lines[-1]=h; lines.append(t); continue
        if len(lines)>=2 and w(lines[-2])>lastmax and ' ' in lines[-2]:
            h,_,t=lines[-2].rpartition(' ')
            lines[-2]=h; lines[-1]=(t+' '+lines[-1]).strip(); continue
        break
    if len(lines)>=2:
        while ' ' in lines[-2]:
            h,_,t=lines[-2].rpartition(' ')
            cand=(t+' '+lines[-1]).strip()
            if w(cand)>lastmax: break
            if abs(w(cand)-w(h))>=abs(w(lines[-1])-w(lines[-2])): break
            lines[-2]=h; lines[-1]=cand
    top=xb-gap_lines*LH
    objs=[fig.text(x0,top-i*LH,ln,fontsize=fs,color='#666',va='top') for i,ln in enumerate(lines)]
    fig.canvas.draw()
    lb=objs[-1].get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
    fig.text(right,lb.y0,URL,ha='right',va='bottom',fontsize=UFS,color='#999')
    assert lb.y0>0.004,'caption runs off the canvas'
    print('  caption %d lines'%len(lines))

def title_band(path, title, sub, tf=0.0285, sf=0.0168):
    # ---- fonts: DejaVu from matplotlib's bundled ttf, system path only as a fallback ----
    import os as _os
    from matplotlib import font_manager as _fm
    def _dejavu(stem):
        p=_os.path.join(matplotlib.get_data_path(),'fonts','ttf',stem)
        if _os.path.exists(p): return p
        try:
            q=_fm.findfont(_fm.FontProperties(family='DejaVu Sans',
                weight=('bold' if 'Bold' in stem else 'normal')),fallback_to_default=False)
            if _os.path.basename(q)==stem and _os.path.exists(q): return q
        except Exception: pass
        p=_os.path.join('/usr/share/fonts/truetype/dejavu',stem)
        if _os.path.exists(p): return p
        raise FileNotFoundError('DejaVu font not found: '+stem)
    FB=_dejavu('DejaVuSans-Bold.ttf'); FR=_dejavu('DejaVuSans.ttf')
    assert _os.path.exists(FB) and _os.path.exists(FR), 'resolved DejaVu font files must exist'
    im=Image.open(path).convert('RGB')
    a=np.array(im.convert('L')); rr=np.where((a<250).sum(axis=1)>0)[0]
    im=im.crop((0,0,im.size[0],min(im.size[1],int(rr.max())+13)))
    W,H=im.size
    fs=int(W*tf); f1=ImageFont.truetype(FB,fs)
    fss=int(W*sf); f2=ImageFont.truetype(FR,fss)
    dd=ImageDraw.Draw(im); M=int(W*0.03); LIM=W-2*M
    def wrap(t,f):
        o=[];cur=''
        for x in t.split():
            z=(cur+' '+x).strip()
            if dd.textlength(z,font=f)<=LIM: cur=z
            else: o.append(cur); cur=x
        o.append(cur); return o
    tl=wrap(title,f1); sl=wrap(sub,f2)
    lh=int(fs*1.25); lhs=int(fss*1.35)
    bh=int(fs*0.85)+lh*len(tl)+int(fss*0.55)+lhs*len(sl)+int(fs*0.22)
    cv=Image.new('RGB',(W,H+bh),'white'); cv.paste(im,(0,bh))
    dr=ImageDraw.Draw(cv); y=int(fs*0.85)+3
    for ln in tl: dr.text((M,y),ln,font=f1,fill=(45,45,45)); y+=lh
    y+=int(fss*0.4)
    for ln in sl: dr.text((M,y),ln,font=f2,fill=(100,100,100)); y+=lhs
    cv.save(path,optimize=True)
    print('  wrote %s  %dx%d'%(path,cv.size[0],cv.size[1]))

# ---------------------------------------------------------------- embedded data

TITLE="After crisis surge, poverty is receding only slowly"
SUB=("Poverty rates at the $3.00 extreme poverty line, the $4.20 lower-middle-income line, and the $8.30 upper-middle-income "
"line (2021 PPP prices), percent")

# The poverty rows of each edition's Table 2, exactly as published. Flags follow the
# column headers: '' plain, 'e' estimate, 'f' forecast. Values are (low, mid, high)
# at that edition's line set.
LINESET={'apr2020':'2011 PPP','apr2021':'2011 PPP','apr2022':'2011 PPP',
         'apr2023':'2017 PPP','apr2024':'2017 PPP','apr2025':'2017 PPP',
         'apr2026':'2021 PPP'}
EDITIONS=['apr2020','apr2021','apr2022','apr2023','apr2024','apr2025','apr2026']
RAW={
 'apr2020':{2017:('',0.7,9.5,39.0),2018:('',0.6,8.9,37.6),2019:('e',0.5,8.5,36.5),
            2020:('f',1.2,11.3,41.7),2021:('f',1.0,11.0,41.1),2022:('f',0.9,10.2,39.7)},
 'apr2021':{2018:('',0.7,9.6,39.5),2019:('',0.6,9.2,38.6),2020:('e',1.2,11.7,42.3),
            2021:('f',1.1,10.9,40.7),2022:('f',1.0,10.4,39.7),2023:('f',0.9,10.0,38.9)},
 'apr2022':{2019:('',0.7,9.5,39.3),2020:('',1.2,11.7,42.3),2021:('e',1.0,10.9,40.9),
            2022:('f',1.0,10.8,40.8),2023:('f',1.0,10.8,40.7),2024:('f',1.0,10.7,40.6)},
 'apr2023':{2020:('',1.6,12.7,49.9),2021:('',1.5,13.1,51.1),2022:('e',5.8,25.0,65.0),
            2023:('f',6.6,27.4,67.2),2024:('f',6.4,26.9,66.9),2025:('f',6.1,26.1,66.0)},
 'apr2024':{2021:('',1.5,13.1,51.2),2022:('',4.1,22.7,64.4),2023:('e',5.2,25.9,66.6),
            2024:('f',4.7,24.8,65.8),2025:('f',4.1,23.2,65.6),2026:('f',3.8,22.2,64.4)},
 'apr2025':{2022:('',4.1,22.7,64.4),2023:('',5.4,27.1,68.0),2024:('e',4.6,24.5,65.9),
            2025:('f',3.9,22.7,65.0),2026:('f',3.7,21.9,64.1),2027:('f',3.5,21.2,63.2)},
 'apr2026':{2023:('',10.8,27.6,71.1),2024:('',9.3,25.0,69.3),2025:('e',7.9,22.1,66.7),
            2026:('f',6.9,20.1,65.4),2027:('f',6.5,19.5,64.5),2028:('f',6.2,18.9,63.4)},
}

# ---- construction: pick, bridge, chain ----
def pick(year):
    """Most recent edition with the year unflagged; else most recent edition with it at all."""
    for ed in reversed(EDITIONS):
        if year in RAW[ed] and RAW[ed][year][0]=='': return ed
    for ed in reversed(EDITIONS):
        if year in RAW[ed]: return ed
    raise KeyError(year)

# link factors at the oldest unflagged year the two line sets share
assert RAW['apr2026'][2023][0]=='' and RAW['apr2025'][2023][0]=='', 'the 2021/2017 PPP bridge year must be unflagged in both'
assert RAW['apr2023'][2020][0]=='' and RAW['apr2022'][2020][0]=='', 'the 2017/2011 PPP bridge year must be unflagged in both'
F1=tuple(a/b for a,b in zip(RAW['apr2026'][2023][1:],RAW['apr2025'][2023][1:]))   # 2021 PPP per 2017 PPP, at 2023
F2=tuple(a/b for a,b in zip(RAW['apr2023'][2020][1:],RAW['apr2022'][2020][1:]))   # 2017 PPP per 2011 PPP, at 2020
FACTOR={'2021 PPP':(1.0,1.0,1.0),'2017 PPP':F1,'2011 PPP':tuple(a*b for a,b in zip(F1,F2))}

YY=list(range(2017,2029))
KEYS=('P300','P420','P830')
S={k:[] for k in KEYS}; META=[]
for y in YY:
    ed=pick(y); flag=RAW[ed][y][0]; raw=RAW[ed][y][1:]; f=FACTOR[LINESET[ed]]
    v=tuple(round(a*b,1) for a,b in zip(raw,f))
    for k,x in zip(KEYS,v): S[k].append(x)
    META.append((y,ed,LINESET[ed],flag,raw,v))

# ---- the chart's stated numbers must follow from the embedded tables ----
assert [m[1] for m in META]==['apr2020','apr2021','apr2022','apr2023','apr2024','apr2025',
                              'apr2026','apr2026','apr2026','apr2026','apr2026','apr2026'], 'edition per year'
assert [m[3] for m in META]==['']*9+['f','f','f'] if False else True
assert [m[3] for m in META][:8]==['']*8 and [m[3] for m in META][8:]==['e','f','f','f'], 'flags per year'
for _y,_v in ((2017,(1.9,10.5,48.1)),(2021,(3.0,13.3,53.5)),(2023,(10.8,27.6,71.1)),(2028,(6.2,18.9,63.4))):
    _i=YY.index(_y)
    assert tuple(S[k][_i] for k in KEYS)==_v, 'labels at %d'%_y
# link factors as documented in the note
assert (round(F1[0],2),round(F1[1],3),round(F1[2],3))==(2.0,1.018,1.046), 'F1'
assert (round(F2[0],3),round(F2[1],3),round(F2[2],3))==(1.333,1.085,1.180), 'F2'
# the title's claim: at the $4.20 line poverty more than doubled into 2023 and the
# 2028 forecast remains above the pre-crisis level
assert S['P420'][YY.index(2023)]>2*S['P420'][YY.index(2021)], 'more than doubled'
assert S['P420'][YY.index(2028)]>S['P420'][YY.index(2021)], 'still above pre-crisis'

NH=YY.index(2024)+1            # solid through the last unflagged year
AMBER='#F9A825'; AMBERTXT='#B8860B'; RED='#C62828'; INDIGO='#283593'
COL={'P300':RED,'P420':AMBER,'P830':INDIGO}
TXT={'P300':RED,'P420':AMBERTXT,'P830':INDIGO}
NAME={'P300':'$3.00 a day','P420':'$4.20 a day','P830':'$8.30 a day'}

NOTE=("Note: As global poverty line definitions have changed over time, the numbers shown here are chained.")

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.edgecolor':'#888',
 'axes.linewidth':1.0,'figure.facecolor':'white','xtick.labelsize':12,'ytick.labelsize':12})
fig,ax=plt.subplots(figsize=(7.8,6.6),dpi=200)

YMAX=84
ax.axvspan(2025.5,2028.5,color='#F4F4F4',zorder=0)
ax.axvline(2025.5,ls=':',lw=1.4,color='#777',zorder=1)
ax.axvline(2024.5,ls=':',lw=1.2,color='#AAA',zorder=1)
ax.grid(axis='y',color='#E6E6E6',lw=0.8,zorder=0); ax.set_axisbelow(True)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.set_xlim(2016.5,2028.5); ax.set_xticks([2017,2019,2021,2023,2025,2027])
ax.set_ylim(0,YMAX); ax.set_yticks(range(0,81,20))

for k in KEYS:
    ax.plot(YY[:NH],S[k][:NH],color=COL[k],lw=2.9,zorder=5,solid_capstyle='round')
    ax.plot(YY[NH-1:],S[k][NH-1:],color=COL[k],lw=2.5,ls=(0,(4.5,2.2)),zorder=5)
    ax.plot(YY[:NH],S[k][:NH],'o',color=COL[k],ms=4.6,zorder=6,
            markeredgecolor='white',markeredgewidth=0.9)

ax.text(2025.0,YMAX*0.985,'estimate',fontsize=9.5,color='#777',style='italic',ha='center',va='top')
ax.text(2027.0,YMAX*0.985,'forecast',fontsize=10.5,color='#777',style='italic',ha='center',va='top')

# ---- fully explicit label overrides: x=year, y=value+offset, stacked clear of dots ----
# dot radius in data units ~ YMAX*0.034 ~ 2.9; offset of 4 clears the dot cleanly.
OFF=3.5   # upward offset from the series value (tight, just clears the dot)
OFF2=5.5  # slightly larger where lines are closer together (2023 P300/P420 gap only 16.8)
def lbl(yr,k): return '%.1f%%'%S[k][YY.index(yr)]
def yv(yr,k):  return S[k][YY.index(yr)]

# Exact y positions computed to clear the dot (radius ~2.5 data units) and stack
# labels without overlap (text height ~2.8 data units). All centre-aligned at x=year.
OVR={
  # 2017: P300 dot=1.9, P420 dot=10.5, P830 dot=48.1
  (RED,     2017): (2017.0,  4.4, 'center','bottom'),
  (AMBERTXT,2017): (2017.0, 13.0, 'center','bottom'),
  (INDIGO,  2017): (2017.0, 50.6, 'center','bottom'),
  # 2021: P300 dot=3.0, P420 dot=13.3, P830 dot=53.5
  (RED,     2021): (2020.85,  5.5, 'center','bottom'),
  (AMBERTXT,2021): (2020.85, 15.8, 'center','bottom'),
  (INDIGO,  2021): (2020.85, 56.0, 'center','bottom'),
  # 2023: P300 dot=10.8, P420 dot=27.6, P830 dot=71.1
  (RED,     2023): (2023.0, 13.3, 'center','bottom'),
  (AMBERTXT,2023): (2023.0, 30.1, 'center','bottom'),
  (INDIGO,  2023): (2023.0, 73.6, 'center','bottom'),
  # 2025: P300 dot=7.9, P420 dot=22.1, P830 dot=66.7
  (RED,     2025): (2025.0, 10.4, 'center','bottom'),
  (AMBERTXT,2025): (2025.0, 24.6, 'center','bottom'),
  (INDIGO,  2025): (2025.0, 69.2, 'center','bottom'),
  # 2028: P300 dot=6.2, P420 dot=18.9, P830 dot=63.4
  (RED,     2028): (2028.0,  8.7, 'center','bottom'),
  (AMBERTXT,2028): (2028.0, 21.4, 'center','bottom'),
  (INDIGO,  2028): (2028.0, 65.9, 'center','bottom'),
}
MK=[]
for k in KEYS:
    for yr in (2017,2021,2023,2025,2028):
        MK.append((yr,lbl(yr,k),'above',S[k],TXT[k]))
place_marks(fig,ax,YY,[S[k] for k in KEYS],MK,fontsize=10.0,align_x=None,override=OVR)

fig.legend(handles=[Line2D([],[],color=COL[k],lw=3.0,label=NAME[k]) for k in KEYS],
           loc='lower center',bbox_to_anchor=(0.5,0.272),ncol=3,frameon=False,fontsize=12,
           columnspacing=3.0,handlelength=2.2)
fig.tight_layout(rect=[0,0.335,1,0.985])

PNG='chart-sri-lanka-poverty-three-lines.png'
caption(fig,ax,SRC+NOTE,url_gap=9.0)
fig.savefig(PNG,dpi=200); plt.close(fig)
title_band(PNG,TITLE,SUB)

# ---- companion csv, pinned to the derived values ----
HDR=('# chart,"Sri Lanka: poverty headcount at the global poverty lines, chained across MPO vintages to 2021 PPP, 2017 to 2028"\n'
'# source,"World Bank, Macro Poverty Outlook for Sri Lanka, April 2020 through April 2026 editions, poverty headcount rows; author\'s calculations."\n'
'# method,"Each year is taken from the most recent edition reporting it in an unflagged column (neither e nor f); 2025 to 2028 exist only flagged and come from April 2026. Line-definition changes are bridged at the oldest unflagged year both vintages share: 2017 PPP values are scaled to the 2021 PPP lines by the April 2026 / April 2025 ratio at 2023 (2.000, 1.018, 1.046), and 2011 PPP values are carried through it by the April 2023 / April 2022 ratio at 2020 (1.333, 1.085, 1.180), rounded to one decimal."\n'
'# note,"published_* columns are the values exactly as printed at that edition\'s own line set; the *_eq columns are the chained 2021 PPP equivalents that the chart plots. Each edition\'s actual data end with the 2016 or 2019 HIES, so every row is model-based."\n'
'# rates are percent of population\n\n'
'year,source_edition,line_set,column_flag,published_low,published_mid,published_high,'
'poverty_rate_300eq_percent,poverty_rate_420eq_percent,poverty_rate_830eq_percent\n')
with open('chart-sri-lanka-poverty-three-lines.csv','w') as f:
    f.write(HDR)
    for y,ed,ls,flag,raw,v in META:
        f.write('%d,%s,%s,%s,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f\n'%(
            y,'April '+ed[3:],ls,flag if flag else 'none',*raw,*v))
print('  wrote chart-sri-lanka-poverty-three-lines.csv  %d rows'%len(META))
