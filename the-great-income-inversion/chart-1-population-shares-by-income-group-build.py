import pandas as pd, numpy as np, pickle, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'figure.facecolor':'white'})
VCOL={'L':'#C62828','LM':'#F9A825','UM':'#00897B','H':'#283593'}
LEG={'L':'Low-income countries','LM':'Lower-middle-income countries',
     'UM':'Upper-middle-income countries','H':'High-income countries'}
OUT=''
panel=pd.read_pickle('oghist.pkl')
d=pickle.load(open('proj2050_p.pkl','rb'))
proj=d['proj']
# ---- population: WDI SP.POP.TOTL to 2025, UN WPP 2024 growth path thereafter ----
import numpy as np, pandas as _pd
_POP=_pd.read_pickle('pop_spliced.pkl')
def pop_at(nm,year):
    v=_POP.get(nm,{}).get(year,np.nan)
    return 0.0 if _pd.isna(v) else float(v)
def cls_at(nm,year):
    if year<=2025:
        r=panel[panel['name']==nm]
        v=r.iloc[0][year] if not r.empty else None
        return v if pd.notna(v) else None
    return proj.get(nm,{}).get(year)
STAGES=[1990,2000,2010,2020,2030,2040,2050]
order=['H','UM','LM','L']
rank={g:i for i,g in enumerate(order)}
names=list(panel['name'])
tot={y: sum(pop_at(nm,y) for nm in names if cls_at(nm,y) in order) for y in STAGES}
share={(y,g): 100*sum(pop_at(nm,y) for nm in names if cls_at(nm,y)==g)/tot[y] for y in STAGES for g in order}
flows={}
for k in range(len(STAGES)-1):
    t0,t1=STAGES[k],STAGES[k+1]
    m={}
    for nm in names:
        g0,g1=cls_at(nm,t0),cls_at(nm,t1)
        if g0 is None or g1 is None: continue
        m.setdefault((g0,g1),[0.,0.])
        m[(g0,g1)][0]+=100*pop_at(nm,t0)/tot[t0]
        m[(g0,g1)][1]+=100*pop_at(nm,t1)/tot[t1]
    flows[k]=m
GAPV=1.6; NODE_W=3.0
XPOS={y:i*8 for i,y in enumerate(STAGES)}
def stack_pos(y):
    pos={}; cur=100+3*GAPV
    for g in order:
        pos[g]=(cur-share[(y,g)],cur); cur-=share[(y,g)]+GAPV
    return pos
POS={y:stack_pos(y) for y in STAGES}
TOP=100+3*GAPV
def bez(p0,p1,s):
    return (1-s)**3*p0+3*(1-s)**2*s*p0+3*(1-s)*s**2*p1+s**3*p1
def grad_ribbon(ax,xs,bot,top,c0,c1,alpha,zorder):
    cmap=LinearSegmentedColormap.from_list('g',[c0,c1])
    X=np.vstack([xs,xs]); Y=np.vstack([bot,top])
    C=np.vstack([np.linspace(0,1,len(xs))]*2)
    ax.pcolormesh(X,Y,C,cmap=cmap,shading='gouraud',zorder=zorder,alpha=alpha,
                  antialiased=False,linewidth=0,edgecolors='none')
fig,ax=plt.subplots(figsize=(8,9.8))
anchor={}; NS=80
for k in range(len(STAGES)-1):
    t0,t1=STAGES[k],STAGES[k+1]
    m=flows[k]
    r_off={g:POS[t0][g][1] for g in order}
    l_off={g:POS[t1][g][1] for g in order}
    ribbons=[]
    for g0 in order:
        outs=[(g1,m[(g0,g1)]) for g1 in order if (g0,g1) in m and g1!=g0]
        ups=sorted([o for o in outs if rank[o[0]]<rank[g0]],key=lambda o:rank[o[0]])
        dns=sorted([o for o in outs if rank[o[0]]>rank[g0]],key=lambda o:rank[o[0]])
        seq=ups+dns+([(g0,m[(g0,g0)])] if (g0,g0) in m else [])
        for g1,(p0,p1) in seq:
            y0t=r_off[g0]; y0b=y0t-p0; r_off[g0]=y0b
            ribbons.append([g0,g1,p0,p1,y0t,y0b,None,None])
    for g1 in order:
        ins_up=sorted([r for r in ribbons if r[1]==g1 and rank[r[0]]>rank[g1]],key=lambda r:rank[r[0]])
        ins_dn=sorted([r for r in ribbons if r[1]==g1 and rank[r[0]]<rank[g1]],key=lambda r:rank[r[0]])
        stay=[r for r in ribbons if r[1]==g1 and r[0]==g1]
        for r in ins_up+ins_dn+stay:
            y1t=l_off[g1]; y1b=y1t-r[3]; l_off[g1]=y1b
            r[6],r[7]=y1t,y1b
    x0=XPOS[t0]+NODE_W/2; x1=XPOS[t1]-NODE_W/2
    ss=np.linspace(0,1,NS); xs=x0+(x1-x0)*ss
    for g0,g1,p0,p1,y0t,y0b,y1t,y1b in sorted(ribbons,key=lambda r:(r[0]!=r[1])):
        if p0<=0 and p1<=0: continue
        topE=np.array([bez(y0t,y1t,s) for s in ss])
        botE=np.array([bez(y0b,y1b,s) for s in ss])
        same=(g0==g1)
        if same:
            ax.fill_between(xs,botE,topE,color=VCOL[g0],lw=0,zorder=2)
        else:
            grad_ribbon(ax,xs,botE,topE,VCOL[g0],VCOL[g1],1.0,3)
            anchor[(k,g0,g1)]=(0.5*(x0+x1),0.5*(bez(y0t,y1t,0.5)+bez(y0b,y1b,0.5)))
for y in STAGES:
    for g in order:
        b,t=POS[y][g]
        ax.add_patch(plt.Rectangle((XPOS[y]-NODE_W/2,b),NODE_W,t-b,color=VCOL[g],
                     ec='white',lw=0.6,zorder=5))
        ax.text(XPOS[y],(b+t)/2,f'{share[(y,g)]:.0f}%',ha='center',va='center',
                color='white',fontsize=9,fontweight='bold',zorder=6)
    ax.text(XPOS[y],TOP+3.2,str(y),ha='center',fontsize=12.5,fontweight='bold',color='#444')
def halo(x,y,txt):
    ax.text(x,y,txt,fontsize=8.6,fontweight='bold',color='#111',ha='center',va='center',
            bbox=dict(boxstyle='round,pad=0.22',facecolor='white',edgecolor='none',alpha=0.9),zorder=6)
for g in order:
    b,t=POS[1990][g]
    ax.text(-2.2,(b+t)/2,{'H':'HIGH','UM':'UM','LM':'LM','L':'LOW'}[g],fontsize=8.2,
            fontweight='bold',color='#111',ha='right',va='center',zorder=6)
a0=anchor.get((0,'L','LM'))
a4=anchor.get((1,'L','LM')); a1=anchor.get((1,'LM','UM'))
a2=anchor.get((3,'UM','H')); a3=anchor.get((4,'LM','UM'))
if a0: halo(a0[0],a0[1],'CHINA + 6 \u2192 LM')
if a4: halo(a4[0],a4[1]-2.0,'INDIA + 26 \u2192 LM')
if a1: halo(a1[0],a1[1]-2.0,'CHINA + 25 \u2192 UM')
if a2: halo(a2[0],a2[1]-2.0,'CHINA + 19 \u2192 HIGH')
if a3: halo(a3[0],a3[1]-4.0,'INDIA + 8 \u2192 UM')
ax.text(XPOS[2030]+0.5,-3.1,'projection from mid-2020s \u2192',fontsize=10.5,style='italic',color='#555')
ax.set_xlim(-4.9,50.6); ax.set_ylim(-4.0,TOP+4.2)
ax.axis('off')
handles=[Patch(color=VCOL[g],label=LEG[g]) for g in ['L','LM','UM','H']]
fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(0.5,0.0890),ncol=2,frameon=False,
           fontsize=10.5,columnspacing=1.6,handletextpad=0.6)
cap=fig.text(0.012,0.0165,
"Source: World Bank OGHIST and WDI, July 2026 release, for the classifications, GNI per capita (Atlas method) and population\n"
"through 2025. Population from 2026 onward is the 2024 revision of UN World Population Prospects, medium variant, rebased to\n"
"each economy's 2025 level. Note: Projections beyond 2025 are illustrative. GNI per capita grows at the median of each economy's\n"
"ten annual rates over the decade to 2025, floored at 1.244 percent so none is downgraded and capped at the 90th percentile of its\n"
"income group. Thresholds drift up at 1.244 percent, the same median. Economies with fewer than eight of the ten annual\n"
"observations are held at their 2025 group.",
 fontsize=7.0,color='#666')
fig.tight_layout(rect=[0,0.146,1,0.995])
pos=ax.get_position(); xl=ax.get_xlim()
xw=pos.x0+(49.5-xl[0])/(xl[1]-xl[0])*pos.width
fig.text(xw,0.004,'movingfrontiers.substack.com',ha='right',fontsize=7.9,color='#999')
r=fig.canvas.get_renderer()
bb=cap.get_window_extent(r).transformed(fig.transFigure.inverted())
lb=fig.legends[0].get_window_extent(r).transformed(fig.transFigure.inverted())
print('caption top %.4f | legend bottom %.4f | gap %.4f fig units'%(bb.y1,lb.y0,lb.y0-bb.y1))
assert lb.y0>bb.y1, 'caption collides with legend'
fig.savefig(OUT+'chart-1-population-shares-by-income-group.png',dpi=200); plt.close(fig)
print('c14u saved')


# ---------------------------------------------------------------- title band
# The published chart carries a title band composited on top after rendering, so a
# two-line title never squeezes the plot. This is the step that takes the figure
# from 1960 to 2196 pixels tall.
from PIL import Image, ImageDraw, ImageFont
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title = "The evolution of the World Bank's country income classification, 1990 to 2050"
subtitle = "Population shares by country income group"
im=Image.open(OUT+'chart-1-population-shares-by-income-group.png').convert('RGB'); W,H=im.size
fs=int(W*0.031); font=ImageFont.truetype(FB,fs)
fss=int(W*0.0225); fonts=ImageFont.truetype(FR,fss)
tmp=ImageDraw.Draw(im)
words=title.split(); lines=[]; cur=''
for w in words:
    t=(cur+' '+w).strip()
    if tmp.textlength(t,font=font)<=W-2*int(W*0.03): cur=t
    else: lines.append(cur); cur=w
lines.append(cur)
lh=int(fs*1.25); lhs=int(fss*1.3)
band=int(fs*0.85)+lh*len(lines)+int(fss*0.5)+lhs+int(fs*0.2)
canvas=Image.new('RGB',(W,H+band),'white'); canvas.paste(im,(0,band))
dr=ImageDraw.Draw(canvas); y=int(fs*0.85)
for ln in lines:
    dr.text((int(W*0.03),y),ln,font=font,fill=(45,45,45)); y+=lh
y+=int(fss*0.35)
dr.text((int(W*0.03),y),subtitle,font=fonts,fill=(100,100,100))
canvas.save(OUT+'chart-1-population-shares-by-income-group.png',optimize=True)
print('titled chart-1-population-shares-by-income-group.png  %dx%d'%canvas.size)
