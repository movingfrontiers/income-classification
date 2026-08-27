import pandas as pd, numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

OUT=''; FN='chart-3-GNI-per-capita-China-and-India.png'
RED='#FFFFFF'; TEAL='#141414'          # line colours, chosen to read on every solid band
BAND={'L':'#C62828','LM':'#F9A825','UM':'#00897B','H':'#283593'}   # solid, as on the shares and levels charts
INK='#141414'; PAPER='#FFFFFF'
import matplotlib.patheffects as pe
PE_W=[pe.Stroke(linewidth=6.4,foreground=INK),pe.Normal()]     # white line, dark outline
PE_K=[pe.Stroke(linewidth=6.0,foreground=PAPER),pe.Normal()]   # dark line, white outline
CSV='wdi_gni_per_capita.csv'

TH={int(k):v for k,v in json.load(open('th_full.json')).items()}
DRIFT=0.012440
A=pd.read_csv('growth_c14p.csv').set_index('name')
gCN,gIN=float(A.loc['China','gr']),float(A.loc['India','gr'])

df=pd.read_csv(CSV); df=df[df['Country Code'].notna()]
for c in [c for c in df.columns if c[:4].isdigit()]: df[int(c[:4])]=pd.to_numeric(df[c],errors='coerce')
g=df.set_index('Country Code')
HY=list(range(1990,2026)); PY=list(range(2025,2051))
cn={y:float(g.loc['CHN',y]) for y in HY}; ind={y:float(g.loc['IND',y]) for y in HY}
for y in PY[1:]:
    cn[y]=cn[y-1]*(1+gCN); ind[y]=ind[y-1]*(1+gIN)
th={y:list(TH[y]) for y in HY}
for y in PY[1:]: th[y]=[v*(1+DRIFT) for v in th[y-1]]
YR=list(range(1990,2051))
tL=np.array([th[y][0] for y in YR]); tM=np.array([th[y][1] for y in YR]); tU=np.array([th[y][2] for y in YR])

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'axes.edgecolor':'#888',
 'axes.linewidth':1.0,'figure.facecolor':'white','xtick.labelsize':14,'ytick.labelsize':14,
 'axes.labelsize':15})
fig,ax=plt.subplots(figsize=(8,6.6),dpi=200)
YLO,YHI=190,62000
ax.fill_between(YR,YLO,tL,color=BAND['L'],zorder=0)
ax.fill_between(YR,tL,tM,color=BAND['LM'],zorder=0)
ax.fill_between(YR,tM,tU,color=BAND['UM'],zorder=0)
ax.fill_between(YR,tU,YHI,color=BAND['H'],zorder=0)
for t in (tL,tM,tU):
    ax.plot(YR,t,ls='--',lw=1.5,color='white',alpha=0.85,zorder=2)
ax.axvline(2025.5,ls=':',lw=1.8,color='white',zorder=3)

ax.plot(HY,[cn[y] for y in HY],color=RED,lw=3.4,zorder=5,solid_capstyle='round',path_effects=PE_W)
ax.plot(PY,[cn[y] for y in PY],color=RED,lw=3.0,ls=(0,(5,2.6)),zorder=5,path_effects=PE_W)
ax.plot(HY,[ind[y] for y in HY],color=TEAL,lw=3.4,zorder=5,solid_capstyle='round',path_effects=PE_K)
ax.plot(PY,[ind[y] for y in PY],color=TEAL,lw=3.0,ls=(0,(5,2.6)),zorder=5,path_effects=PE_K)

def dot(x,y,col):
    edge = INK if col==PAPER else PAPER
    ax.plot([x],[y],'o',mfc=col,mec=edge,mew=2.8,ms=12,zorder=7)
# ---- label placement solver: pick anchors that clear every curve and every other label ----
ax.set_yscale('log'); ax.set_ylim(YLO,YHI); ax.set_xlim(1989.6,2050.5)
ticks=[200,500,1000,2000,5000,10000,20000,40000]
ax.set_yticks(ticks); ax.set_yticklabels(['$%s'%format(t,',') for t in ticks]); ax.minorticks_off()
ax.set_xticks([1990,2000,2010,2020,2030,2040,2050])

ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
fig.tight_layout(rect=[0,0.218,0.902,0.995])
fig.canvas.draw()
REN=fig.canvas.get_renderer()
CURVES=[lambda x:cn[x],lambda x:ind[x],lambda x:th[x][0],lambda x:th[x][1],lambda x:th[x][2]]
placed=[]
def databox(t):
    bb=t.get_window_extent(REN); inv=ax.transData.inverted()
    (x0,y0)=inv.transform((bb.x0,bb.y0)); (x1,y1)=inv.transform((bb.x1,bb.y1))
    return x0,x1,min(y0,y1),max(y0,y1)
def ok(box,pad=0.030):
    x0,x1,ylo,yhi=box
    if x0<1989.8 or x1>2050.3: return False
    lo,hi=ylo/10**pad,yhi*10**pad
    xs=[x for x in YR if x0-0.7<=x<=x1+0.7]
    for f in CURVES:
        for x in xs:
            if lo<=f(x)<=hi: return False
    for p in placed:
        if x0<p[1]+0.4 and p[0]<x1+0.4 and ylo/10**0.012<p[3] and p[2]<yhi*10**0.012: return False
    return True
def place(lab,cands,fs,col,weight='bold'):
    for (lx,ly,ha,va) in cands:
        fc,tc=(INK,PAPER) if col==PAPER else (PAPER,INK)
        t=ax.text(lx,ly,lab,fontsize=fs,fontweight=weight,color=tc,ha=ha,va=va,
                  zorder=8,linespacing=1.3,
                  bbox=dict(boxstyle='round,pad=0.26',facecolor=fc,edgecolor='none'))
        b=databox(t)
        if ok(b):
            placed.append(b); return t,b
        t.remove()
    fc,tc=(INK,PAPER) if col==PAPER else (PAPER,INK)
    t=ax.text(cands[0][0],cands[0][1],lab,fontsize=fs,fontweight=weight,color=tc,
              ha=cands[0][2],va=cands[0][3],zorder=8,linespacing=1.3,
              bbox=dict(boxstyle='round,pad=0.26',facecolor=fc,edgecolor='none'))
    b=databox(t); placed.append(b); print('  !! no clear slot for',lab.replace(chr(10),' ')[:28])
    return t,b

JOBS=[
 ('2026',2026,cn[2026],RED,
   [(2024.6,y,'right','center') for y in (21500,24000,19500)]+
   [(2027.8,y,'left','center') for y in (11800,11000)]),
 ('2010',2010,cn[2010],RED,
   [(2008.8,y,'right','center') for y in (6100,6700,5600)]+
   [(2011.8,y,'left','center') for y in (3250,3000)]),
 ('1999',1999,cn[1999],RED,
   [(1997.6,y,'right','center') for y in (1200,1330,1090)]+
   [(2000.9,y,'left','center') for y in (610,560)]),
 ('2036',2036,ind[2036],TEAL,
   [(2037.8,y,'left','center') for y in (4100,3800,4450)]+
   [(2034.2,y,'right','center') for y in (7400,8100)]),
 ('2007',2007,ind[2007],TEAL,
   [(2008.8,y,'left','center') for y in (630,580,690)]+
   [(2005.2,y,'right','center') for y in (630,580)]),
]
for lab,dx,dy,col,cands in JOBS:
    dot(dx,dy,col)
    place(lab,cands,13,col)

place('China',[(2043.5,y,'right','center') for y in (44000,48500,40000)]+
      [(2038,y,'right','center') for y in (37000,41000)],13,RED)
place('India',[(2046.5,y,'right','center') for y in (14600,13600,15600,16600)]+
      [(2043,y,'right','center') for y in (14600,13600,16000)]+
      [(2049.8,y,'right','center') for y in (17500,16000)],13,TEAL)

# band labels, outside the axes on the right, two lines each, centred in each band
BANDLAB=[('HIGH\nINCOME',  np.sqrt(th[2050][2]*YHI)),
         ('UPPER-\nMIDDLE',np.sqrt(th[2050][1]*th[2050][2])),
         ('LOWER-\nMIDDLE',np.sqrt(th[2050][0]*th[2050][1])),
         ('LOW\nINCOME',   np.sqrt(YLO*th[2050][0]))]
BANDCOL=['#283593','#00897B','#B8860B','#C62828']
for (lab,yv),cc in zip(BANDLAB,BANDCOL):
    ax.text(1.012,yv,lab,transform=ax.get_yaxis_transform(),fontsize=11.5,fontweight='bold',
            color=cc,ha='left',va='center',linespacing=1.25,clip_on=False,zorder=6)

ax.text(2026.4,YLO*1.12,'projected',fontsize=11.5,color='white',fontweight='bold',ha='left',va='bottom',zorder=6)
ax.text(2024.6,YLO*1.12,'actual',fontsize=11.5,color='white',fontweight='bold',ha='right',va='bottom',zorder=6)

CAPFS=7.4
CAPTXT=("Source: World Bank OGHIST (1 July 2026): Thresholds worksheet for the official thresholds and Country Analytical History for\n"
"the classifications, both 1990 to 2025; WDI GNI per capita, Atlas method (July 2026 vintage); author's calculations and projections.\n"
"Note: Shaded bands are the four income groups, named at right. Their boundaries are the official thresholds year by year as\n"
"published, with no smoothing, extended beyond 2025 at 1.244 percent a year, the median annual increase of the past decade. Solid\n"
"lines are actual GNI per capita through 2025, dashed lines projected at each economy's decade-median growth, 5.0 percent for\n"
"China and 6.4 percent for India. Circles mark each economy's crossings, dated by the classification year; each is announced the\n"
"following July.")
fig.canvas.draw()
_r=fig.canvas.get_renderer()
_bots=[t.get_window_extent(_r).y0 for t in ax.get_xticklabels() if t.get_text()]
xl=ax.xaxis.get_label().get_window_extent(_r)
xl_bot=fig.transFigure.inverted().transform((0,min(_bots+[xl.y0])))[1]
LH=CAPFS*1.2/(72*fig.get_figheight())
cap=fig.text(0.012,xl_bot-2*LH,CAPTXT,fontsize=CAPFS,color='#666',va='top')
fig.canvas.draw()
cb=cap.get_window_extent(fig.canvas.get_renderer())
top,bot=[fig.transFigure.inverted().transform((0,v))[1] for v in (cb.y1,cb.y0)]
print('axis bottom {:.4f} | caption top {:.4f} | gap {:.2f} caption lines'.format(xl_bot,top,(xl_bot-top)/LH))
print('caption bottom {:.4f}'.format(bot))
assert bot>0.004, 'caption runs off the canvas'

# watermark: same format and placement as the shares and levels charts,
# right-aligned to the last plotted year, sitting on the caption's bottom line
# right edge set to match the shares and levels charts exactly (95 px from the canvas edge)
xw=1.0-95.0/(fig.get_figwidth()*fig.dpi)
wm=fig.text(xw,bot-1.30*LH,'movingfrontiers.substack.com',ha='right',va='bottom',
            fontsize=7.9,color='#999')
fig.canvas.draw()
wb=wm.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
cbx=cap.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
print('watermark x {:.4f}-{:.4f} y {:.4f}-{:.4f} | caption right edge {:.4f}'.format(
      wb.x0,wb.x1,wb.y0,wb.y1,cbx.x1))
assert wb.x0>0 and wb.x1<1.0, 'watermark off canvas'
fig.savefig(OUT+FN,dpi=200); plt.close(fig)

# ---- standard title band ----
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title="China and India's climb through the income classification, 1990 to 2050"
sub="GNI per capita (Atlas method, logs) against World Bank's moving income thresholds"
im=Image.open(OUT+FN).convert('RGB')
_a=np.array(im.convert('L')); _rows=np.where((_a<250).sum(axis=1)>0)[0]
im=im.crop((0,0,im.size[0],min(im.size[1],int(_rows.max())+6)))
W,H=im.size
print('trimmed trailing whitespace: height {} -> {}'.format(_a.shape[0],H))
fs=int(W*0.031); f1=ImageFont.truetype(FB,fs)
fss=int(W*0.0225); f2=ImageFont.truetype(FR,fss)
dd=ImageDraw.Draw(im); lines=[]; cur=''
for w in title.split():
    t=(cur+' '+w).strip()
    if dd.textlength(t,font=f1)<=W-2*int(W*0.03): cur=t
    else: lines.append(cur); cur=w
lines.append(cur)
lh=int(fs*1.25); lhs=int(fss*1.3)
band=int(fs*0.85)+lh*len(lines)+int(fss*0.5)+lhs+int(fs*0.2)
cv=Image.new('RGB',(W,H+band),'white'); cv.paste(im,(0,band))
dr=ImageDraw.Draw(cv); y=int(fs*0.85)
for ln in lines: dr.text((int(W*0.03),y),ln,font=f1,fill=(45,45,45)); y+=lh
y+=int(fss*0.35); dr.text((int(W*0.03),y),sub,font=f2,fill=(100,100,100))
cv.save(OUT+FN,optimize=True)
print('saved',FN,cv.size)
print('China 2025 %.0f  2026 %.0f  2045 %.0f | growth %.4f%%'%(cn[2025],cn[2026],cn[2045],gCN*100))
print('India 2025 %.0f  2036 %.0f  2045 %.0f | growth %.4f%%'%(ind[2025],ind[2036],ind[2045],gIN*100))
print('thresholds 2026 %s | 2036 %s | 2045 %s'%([round(v) for v in th[2026]],[round(v) for v in th[2036]],[round(v) for v in th[2045]]))
