# =============================================================================
# Chart 3.2: What past decades tell us about Sri Lanka's high-income horizon
#
# Provenance, frozen vintage. Nothing is read from disk or the network.
#   GNI per capita        : World Bank WDI, July 2026 vintage, Atlas method, current US$.
#   Thresholds 1990-2025  : World Bank OGHIST, 1 July 2026, Thresholds worksheet,
#                           official values as published, no smoothing.
#   Classifications       : World Bank OGHIST, 1 July 2026, Country Analytical History.
#   Vintage freeze date   : 1 July 2026. The chart is pinned to this vintage; do not swap
#                           the embedded data for a live API call.
#
# Reduction: val() is called only for 1990-2025 and TH[y] only for 1990-2025. The OGHIST
# panel is used only for Sri Lanka's own classification row, scanned across its year
# columns to date the transitions, so the pickle reduces to that one row.
# =============================================================================
"""Sri Lanka, two panels: the same extrapolation on two successive decades of growth."""
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from PIL import Image, ImageDraw, ImageFont

OUT=''
# ---- embedded series, see the provenance header ----
# Sri Lanka GNI per capita, Atlas method, current US$, 1990-2025
GNI={1990:490.0,1991:530.0,1992:580.0,1993:630.0,1994:670.0,1995:720.0,1996:760.0,1997:810.0,1998:810.0,1999:830.0,2000:860.0,2001:810.0,2002:820.0,2003:910.0,2004:1030.0,2005:1170.0,2006:1320.0,2007:1500.0,2008:1740.0,2009:1950.0,2010:2360.0,2011:2830.0,2012:3340.0,2013:3630.0,2014:3810.0,2015:3920.0,2016:4020.0,2017:4220.0,2018:4350.0,2019:4220.0,2020:3880.0,2021:4010.0,2022:3620.0,2023:3550.0,2024:3870.0,2025:4670.0}
# official operational thresholds [low, lower-middle, upper-middle], 1990-2025
TH={1990:[610.0, 2465.0, 7620.0],1991:[635.0, 2555.0, 7910.0],1992:[675.0, 2695.0, 8355.0],1993:[695.0, 2785.0, 8625.0],1994:[725.0, 2895.0, 8955.0],1995:[765.0, 3035.0, 9385.0],1996:[785.0, 3115.0, 9645.0],1997:[785.0, 3125.0, 9655.0],1998:[760.0, 3030.0, 9360.0],1999:[755.0, 2995.0, 9265.0],2000:[755.0, 2995.0, 9265.0],2001:[745.0, 2975.0, 9205.0],2002:[735.0, 2935.0, 9075.0],2003:[765.0, 3035.0, 9385.0],2004:[825.0, 3255.0, 10065.0],2005:[875.0, 3465.0, 10725.0],2006:[905.0, 3595.0, 11115.0],2007:[935.0, 3705.0, 11455.0],2008:[975.0, 3855.0, 11905.0],2009:[995.0, 3945.0, 12195.0],2010:[1005.0, 3975.0, 12275.0],2011:[1025.0, 4035.0, 12475.0],2012:[1035.0, 4085.0, 12615.0],2013:[1045.0, 4125.0, 12745.0],2014:[1045.0, 4125.0, 12735.0],2015:[1025.0, 4035.0, 12475.0],2016:[1005.0, 3955.0, 12235.0],2017:[995.0, 3895.0, 12055.0],2018:[1025.0, 3995.0, 12375.0],2019:[1035.0, 4045.0, 12535.0],2020:[1045.0, 4095.0, 12695.0],2021:[1085.0, 4255.0, 13205.0],2022:[1135.0, 4465.0, 13845.0],2023:[1145.0, 4515.0, 14005.0],2024:[1135.0, 4495.0, 13935.0],2025:[1175.0, 4635.0, 14375.0]}
# Sri Lanka's OGHIST classification row, 1987-2025, None where unclassified
OG={1987:'L',1988:'L',1989:'L',1990:'L',1991:'L',1992:'L',1993:'L',1994:'L',1995:'L',1996:'L',1997:'LM',1998:'LM',1999:'LM',2000:'LM',2001:'LM',2002:'LM',2003:'LM',2004:'LM',2005:'LM',2006:'LM',2007:'LM',2008:'LM',2009:'LM',2010:'LM',2011:'LM',2012:'LM',2013:'LM',2014:'LM',2015:'LM',2016:'LM',2017:'LM',2018:'UM',2019:'LM',2020:'LM',2021:'LM',2022:'LM',2023:'LM',2024:'LM',2025:'UM'}
def val(y): return GNI[y]
DRIFT=0.01244
YR=list(range(1990,2051))
S={y:val(y) for y in range(1990,2026)}
def thr(y,j): return TH[y][j] if y<=2025 else TH[2025][j]*(1+DRIFT)**(y-2025)
tL=[thr(y,0) for y in YR]; tM=[thr(y,1) for y in YR]; tU=[thr(y,2) for y in YR]

WIN=[(2016,2025,'Last decade, 2016 to 2025'),
     (2006,2015,'Previous decade, 2006 to 2015')]
RATE=[float(np.median([S[y]/S[y-1]-1 for y in range(a,z+1)])) for a,z,_ in WIN]

# official transitions from OGHIST, never inferred from the plotted line
TRANS=[]; prev=None
for y in sorted(OG):
    if OG[y] is None: continue
    if OG[y]!=prev and prev is not None and y>=1990: TRANS.append(y)
    prev=OG[y]
print('  OGHIST transitions in window:',TRANS)
# ---- the caption's stated numbers must follow from the embedded data ----
assert round(DRIFT*100,3)==1.244, 'caption states a 1.244 percent threshold drift'
assert TRANS==[1997,2018,2019,2025], 'caption states 1997, a single year at upper-middle in 2018, 2019 and 2025'
assert OG[2018]=='UM' and OG[2019]=='LM' and OG[2025]=='UM', (
    'caption states upper-middle for one year in 2018, back to lower-middle in 2019, upper-middle again in 2025')
assert [round(100*r,1) for r in RATE]==[2.8,13.2], 'panel titles state 2.8 and 13.2 percent'


PATHS={}      # panel label -> {year: GNI}, the exact series each panel plots
CROSS={}      # panel label -> first year the path clears the high-income line, else None

BAND={'L':'#C62828','LM':'#F9A825','UM':'#00897B','H':'#283593'}
INK='#141414'; PAPER='#FFFFFF'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.edgecolor':'#888',
 'axes.linewidth':1.0,'figure.facecolor':'white','xtick.labelsize':12,'ytick.labelsize':12})
fig,axs=plt.subplots(1,2,figsize=(11.2,7.1),dpi=200,sharey=True)
YLO,YHI=380,150000
for ax,(rate,(a,z,lab)) in zip(axs,zip(RATE,WIN)):
    P=dict(S)
    for y in range(2026,2051): P[y]=P[y-1]*(1+rate)
    ser=[P[y] for y in YR]
    PATHS[lab]=dict(P)
    ax.fill_between(YR,YLO,tL,color=BAND['L'],zorder=0)
    ax.fill_between(YR,tL,tM,color=BAND['LM'],zorder=0)
    ax.fill_between(YR,tM,tU,color=BAND['UM'],zorder=0)
    ax.fill_between(YR,tU,YHI,color=BAND['H'],zorder=0)
    for t in (tL,tM,tU): ax.plot(YR,t,ls='--',lw=1.3,color='white',alpha=0.85,zorder=2)
    ax.axvline(2025.5,ls=':',lw=1.8,color='white',zorder=3)
    n=YR.index(2025)+1
    ax.plot(YR[:n],ser[:n],color=PAPER,lw=3.0,zorder=5,solid_capstyle='round',
            path_effects=[pe.Stroke(linewidth=6.0,foreground=INK),pe.Normal()])
    ax.plot(YR[n-1:],ser[n-1:],color=PAPER,lw=2.8,ls=(0,(5,2.4)),zorder=5,
            path_effects=[pe.Stroke(linewidth=5.8,foreground=INK),pe.Normal()])
    ax.set_yscale('log'); ax.set_ylim(YLO,YHI); ax.set_xlim(1990,2050)
    ax.set_box_aspect(1)          # square plotting area, independent of data ranges
    ax.set_xticks([1990,2000,2025,2050])
    yt=[500,1000,2000,5000,10000,20000,50000,100000]
    ax.set_yticks(yt); ax.set_yticklabels(['$%s'%format(t,',') for t in yt]); ax.minorticks_off()
    for s in ('top','right'): ax.spines[s].set_visible(False)
    ax.set_title('%s\n%.1f%% a year'%(lab,100*rate),fontsize=12,fontweight='bold',color='#333',
                 pad=9,linespacing=1.35)
    # historical transitions, all three panels identical
    # identical in every panel: same anchor, same offset, same size
    MK={1997:(1.6,0.62,'left'),2018:(-1.6,1.70,'right'),2019:(1.6,0.60,'left'),2025:(1.6,1.62,'left')}
    for yr,(dx,fy,ha) in MK.items():
        ax.plot([yr],[S[yr]],'o',mfc=PAPER,mec=INK,mew=2.4,ms=10,zorder=8,clip_on=False)
        ax.text(yr+dx,S[yr]*fy,str(yr),fontsize=11,fontweight='bold',color=INK,ha=ha,va='center',
                zorder=9,bbox=dict(boxstyle='round,pad=0.24',facecolor=PAPER,edgecolor='none'))
    # the high-income crossing, if it happens by 2050
    hit=next((y for y in range(2026,2051) if P[y]>thr(y,2)),None)
    CROSS[lab]=hit
    if hit:
        ax.plot([hit],[P[hit]],'o',mfc=PAPER,mec=INK,mew=2.8,ms=13,zorder=8,clip_on=False)
        ax.text(hit-1.6,P[hit]*1.70,'%d'%hit,fontsize=11,fontweight='bold',color=INK,ha='right',
                va='center',zorder=9,bbox=dict(boxstyle='round,pad=0.24',facecolor=PAPER,edgecolor='none'))
    else:
        n2=np.log(thr(2025,2)/P[2025])/np.log((1+rate)/(1+DRIFT)) if rate>DRIFT else None
        msg='high income\nnot reached\nby 2050' if n2 is None else 'high income\nnot until %d'%(2025+int(np.ceil(n2)))
        ax.text(1991.5,118000,msg,fontsize=11,fontweight='bold',color=PAPER,ha='left',va='top',
                linespacing=1.3,zorder=9)
BANDLAB=[('HIGH\nINCOME',np.sqrt(tU[-1]*YHI),'#283593'),
         ('UPPER-\nMIDDLE',np.sqrt(tM[-1]*tU[-1]),'#00897B'),
         ('LOWER-\nMIDDLE',np.sqrt(tL[-1]*tM[-1]),'#B8860B'),
         ('LOW\nINCOME',np.sqrt(YLO*tL[-1]),'#C62828')]
for lab,yv,cc in BANDLAB:
    axs[-1].text(1.015,yv,lab,transform=axs[-1].get_yaxis_transform(),fontsize=11,fontweight='bold',
                color=cc,ha='left',va='center',linespacing=1.25,clip_on=False,zorder=6)
fig.tight_layout(rect=[0,0.300,0.960,0.985]); fig.subplots_adjust(wspace=0.16)

CAPFS=7.8
CAP=("Source: World Bank OGHIST and World Development Indicators, July 2026 release, for the income classifications, the official "
"thresholds and GNI per capita (Atlas method, current US$).\n"
"Note: This is not a forecast. Each panel carries a single past growth rate forward from 2025 and makes no allowance for policy, "
"demography, technology or shocks. The rate is the median of Sri Lanka's annual growth in GNI per capita over the decade named above "
"the panel. Thresholds beyond 2025 rise at 1.244 percent a year, the median annual increase of the past decade. "
"Sri Lanka held upper-middle income for a single year, 2018, fell back to lower-middle in 2019, and regained upper-middle in 2025.")
fig.canvas.draw(); r=fig.canvas.get_renderer()
Wpx=fig.get_figwidth()*fig.dpi
bots=[t.get_window_extent(r).y0 for t in axs[0].get_xticklabels() if t.get_text()]
xb=fig.transFigure.inverted().transform((0,min(bots)))[1]
LH=CAPFS*1.2/(72*fig.get_figheight())
pr=fig.text(0,0,'0',fontsize=CAPFS); fig.canvas.draw()
CW=pr.get_window_extent(fig.canvas.get_renderer()).width/Wpx; pr.remove()
def w(t,size=CAPFS):
    tt=fig.text(0,0,t,fontsize=size); fig.canvas.draw()
    v=tt.get_window_extent(fig.canvas.get_renderer()).width/Wpx; tt.remove(); return v
URL='movingfrontiers.substack.com'; UFS=CAPFS*1.2
x0=0.012; right=1.0-70.0/Wpx; full=right-x0
lines=[]
for para in CAP.split('\n'):
    cur=''
    for word in para.split():
        z2=(cur+' '+word).strip()
        if w(z2)<=full or not cur: cur=z2
        else: lines.append(cur); cur=word
    lines.append(cur)
top=xb-2.0*LH
objs=[fig.text(x0,top-i*LH,ln,fontsize=CAPFS,color='#666',va='top') for i,ln in enumerate(lines)]
fig.canvas.draw()
lb=objs[-1].get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
fig.text(right,lb.y0-0.45*LH,URL,ha='right',va='top',fontsize=UFS,color='#999')
assert lb.y0-0.45*LH>0.004
print('  caption %d lines'%len(lines))
FN='chart-3-2-sri-lanka-two-panels.png'
fig.savefig(OUT+FN,dpi=200); plt.close(fig)

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
title="How past decades inform Sri Lanka’s high-income horizon"
sub="Sri Lanka's GNI per capita extrapolated to 2050 on the median growth of two successive decades (current US$, Atlas)"
im=Image.open(OUT+FN).convert('RGB')
a=np.array(im.convert('L')); rr=np.where((a<250).sum(axis=1)>0)[0]
im=im.crop((0,0,im.size[0],min(im.size[1],int(rr.max())+10)))
W,H=im.size
fs=int(W*0.0245); f1=ImageFont.truetype(FB,fs)
fss=int(W*0.0145); f2=ImageFont.truetype(FR,fss)
dd=ImageDraw.Draw(im); M=int(W*0.03); LIM=W-2*M
def wrap(t,f):
    o=[];cur=''
    for x in t.split():
        z2=(cur+' '+x).strip()
        if dd.textlength(z2,font=f)<=LIM: cur=z2
        else: o.append(cur); cur=x
    o.append(cur); return o
tl=wrap(title,f1); sl=wrap(sub,f2)
lh=int(fs*1.25); lhs=int(fss*1.35)
bh=int(fs*0.85)+lh*len(tl)+int(fss*0.55)+lhs*len(sl)+int(fs*0.22)
cv=Image.new('RGB',(W,H+bh),'white'); cv.paste(im,(0,bh))
dr=ImageDraw.Draw(cv); y=int(fs*0.85)
for ln in tl: dr.text((M,y),ln,font=f1,fill=(45,45,45)); y+=lh
y+=int(fss*0.4)
for ln in sl: dr.text((M,y),ln,font=f2,fill=(100,100,100)); y+=lhs
cv.save(OUT+FN,optimize=True)
print('  %s %dx%d'%(FN,cv.size[0],cv.size[1]))
for (a2,z2,lab),rt in zip(WIN,RATE): print('  %-34s %.2f%%'%(lab,100*rt))

# =============================================================================
# Companion csv. Written from the same objects the chart plots, so the file and
# the figure cannot drift: PATHS holds each panel's extrapolated series, thr()
# supplies the thresholds, OG the published classification.
# =============================================================================
LAB1,LAB2=WIN[0][2],WIN[1][2]
R1,R2=RATE[0],RATE[1]

# the "high income not until" year quoted on a panel that never crosses by 2050
def horizon(rate):
    if rate<=DRIFT: return None
    n=np.log(thr(2025,2)/PATHS[LAB1][2025])/np.log((1+rate)/(1+DRIFT))
    return 2025+int(np.ceil(n))
H1=CROSS[LAB1] or horizon(R1)
H2=CROSS[LAB2] or horizon(R2)

# ---- the csv's stated numbers must follow from the embedded data ----
assert PATHS[LAB1][2025]==PATHS[LAB2][2025]==GNI[2025], 'both panels branch from the same 2025 actual'
assert all(PATHS[LAB1][y]==PATHS[LAB2][y]==GNI[y] for y in range(1990,2026)), 'history is identical in both panels'
assert CROSS[LAB1] is None and CROSS[LAB2]==2036, 'panel 1 does not cross by 2050, panel 2 crosses in 2036'
assert H1==2098, 'panel 1 annotation states high income not until 2098'

CSVFN='chart-3-2-sri-lanka-two-panels.csv'
HDR=(
'# chart,"Sri Lanka: GNI per capita extrapolated to 2050 on the median growth of two successive decades (current US$, Atlas)"\n'
'# source,"World Bank OGHIST and World Development Indicators, July 2026 release: income classifications, official operational thresholds, and GNI per capita (Atlas method, current US$)."\n'
'# vintage,"Frozen 1 July 2026. Values are embedded in the build script, not fetched; do not refresh against a live API."\n'
'# method,"History (1990-2025) is the published GNI per capita series and is identical in both panels. From 2026 each panel compounds the 2025 actual at a single constant rate, the median of Sri Lanka annual growth in GNI per capita over the decade named in the panel: %.4f (%.1f percent) for %s and %.4f (%.1f percent) for %s. Thresholds through 2025 are the official operational values as published; beyond 2025 they rise at %.5f (1.244 percent) a year, the median annual increase of the past decade."\n'
'# note,"This is not a forecast. Neither path makes any allowance for policy, demography, technology or shocks. The classification column is the group as published in OGHIST, which the World Bank assigns on the GNI estimate available at the time; later revisions can move the plotted line across a threshold without changing the classification, as they do in 2016, 2017 and 2019. Sri Lanka held upper-middle income for a single year, 2018, fell back to lower-middle in 2019, and regained upper-middle in 2025."\n'
'# crossing,"%s does not reach the high-income threshold by 2050 (extending the same rate puts it at %d). %s crosses in %d."\n'
'# units,"GNI per capita and thresholds in current US$; classification in OGHIST codes L, LM, UM, H."\n\n'
'year,period,gni_per_capita_usd,oghist_class,is_transition_year,'
'threshold_basis,threshold_low_to_lm_usd,threshold_lm_to_um_usd,threshold_um_to_high_usd,'
'path_last_decade_2016_2025_usd,path_previous_decade_2006_2015_usd\n'
)%(R1,100*R1,LAB1,R2,100*R2,LAB2,DRIFT,LAB1,H1,LAB2,CROSS[LAB2])

with open(OUT+CSVFN,'w') as f:
    f.write(HDR)
    for y in YR:
        hist   = y<=2025
        f.write('%d,%s,%s,%s,%s,%s,%.1f,%.1f,%.1f,%.2f,%.2f\n'%(
            y,
            'actual' if hist else 'extrapolated',
            ('%.1f'%GNI[y]) if hist else '',
            OG.get(y,'') if hist else '',
            'yes' if y in TRANS else 'no',
            'official' if hist else 'projected',
            thr(y,0), thr(y,1), thr(y,2),
            PATHS[LAB1][y], PATHS[LAB2][y]))
print('  %s %d rows'%(CSVFN,len(YR)))
