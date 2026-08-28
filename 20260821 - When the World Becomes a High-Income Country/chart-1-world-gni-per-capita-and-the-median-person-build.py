"""Chart 1: World GNI per capita and the income of the median person's country.

Reads chart-1-world-gni-per-capita-and-the-median-person.csv and writes the png of
the same name. Run from inside this folder:  python3 chart-1-world-gni-per-capita-and-the-median-person-build.py
"""
import csv
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- shared helpers
def read_chart_csv(path):
    """Read a chart csv, skipping the commented header rows."""
    rows=[r for r in csv.reader(open(path)) if r and not r[0].startswith('#')]
    hdr=rows[0]
    return hdr,[dict(zip(hdr,r)) for r in rows[1:]]

def caption(fig, ax, cap, fs, url_on_last_line, gap_lines=2.0, use_xlabel=False):
    """Moving Frontiers caption block. The watermark either sits on the baseline of
    the last note line, or on its own line below it."""
    fig.canvas.draw(); r=fig.canvas.get_renderer()
    Wpx=fig.get_figwidth()*fig.dpi
    bots=[t.get_window_extent(r).y0 for t in ax.get_xticklabels() if t.get_text()]
    if use_xlabel and ax.xaxis.label.get_text():
        bots.append(ax.xaxis.label.get_window_extent(r).y0)
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
    lastmax=right-w(URL,UFS)-2.0*CW-x0 if url_on_last_line else full
    lines=[]
    for para in cap.split(chr(10)):
        cur=''
        for word in para.split():
            z=(cur+' '+word).strip()
            if w(z)<=full or not cur: cur=z
            else: lines.append(cur); cur=word
        lines.append(cur)
    if url_on_last_line:
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
    fig.canvas.draw(); r2=fig.canvas.get_renderer()
    lb=objs[-1].get_window_extent(r2).transformed(fig.transFigure.inverted())
    if url_on_last_line:
        fig.text(right,lb.y0,URL,ha='right',va='bottom',fontsize=UFS,color='#999')
        assert lb.y0>0.004,'caption runs off the canvas'
    else:
        fig.text(right,lb.y0-0.45*LH,URL,ha='right',va='top',fontsize=UFS,color='#999')
        assert lb.y0-0.45*LH>0.004,'caption runs off the canvas'
    print('  caption %d lines'%len(lines))

def title_band(path, title, sub, title_frac, sub_frac):
    """Composite the title and subtitle above the rendered figure with PIL, after
    cropping the figure to its ink, so a two-line title never squeezes the plot."""
    FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    im=Image.open(path).convert('RGB')
    a=np.array(im.convert('L')); rr=np.where((a<250).sum(axis=1)>0)[0]
    im=im.crop((0,0,im.size[0],min(im.size[1],int(rr.max())+10)))
    W,H=im.size
    fs=int(W*title_frac); f1=ImageFont.truetype(FB,fs)
    fss=int(W*sub_frac);  f2=ImageFont.truetype(FR,fss)
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
    dr=ImageDraw.Draw(cv); y=int(fs*0.85)
    for ln in tl: dr.text((M,y),ln,font=f1,fill=(45,45,45)); y+=lh
    y+=int(fss*0.4)
    for ln in sl: dr.text((M,y),ln,font=f2,fill=(100,100,100)); y+=lhs
    cv.save(path,optimize=True)
    print('  wrote %s  %dx%d'%(path,cv.size[0],cv.size[1]))

CSV='chart-1-world-gni-per-capita-and-the-median-person.csv'
PNG='chart-1-world-gni-per-capita-and-the-median-person.png'
hdr,rows=read_chart_csv(CSV)
YR=[int(r['year']) for r in rows]
V={'mean':{int(r['year']):float(r['world_gni_per_capita_usd']) for r in rows},
   'med' :{int(r['year']):float(r['median_person_country_gni_per_capita_usd']) for r in rows}}
TH={int(r['year']):[float(r['threshold_lic_lmic_usd']),float(r['threshold_lmic_umic_usd']),
                    float(r['threshold_umic_hic_usd'])] for r in rows}
ECON={int(r['year']):r['median_person_country'] for r in rows}
S={k:np.array([V[k][y] for y in YR]) for k in ('mean','med')}
tL=np.array([TH[y][0] for y in YR]); tM=np.array([TH[y][1] for y in YR]); tU=np.array([TH[y][2] for y in YR])

# threshold crossings, each year against that year's own threshold
CR=[]
for k in ('mean','med'):
    for j,tn in enumerate(('LIC/LMIC','LMIC/UMIC','UMIC/HIC')):
        for i in range(1,len(YR)):
            a,b=YR[i-1],YR[i]
            if V[k][a]<=TH[a][j] and V[k][b]>TH[b][j]: CR.append((k,tn,b,'up'))
            if V[k][a]>TH[a][j] and V[k][b]<=TH[b][j]: CR.append((k,tn,b,'down'))
print('  crossings:',[(k,t,y,d) for k,t,y,d in CR])

BAND={'L':'#C62828','LM':'#F9A825','UM':'#00897B','H':'#283593'}
INK='#141414'; PAPER='#FFFFFF'; AMBERTXT='#8A5A00'
LC={'mean':PAPER,'med':'#FFD166'}
PEF={'mean':[pe.Stroke(linewidth=6.6,foreground=INK),pe.Normal()],
     'med' :[pe.Stroke(linewidth=6.4,foreground=INK),pe.Normal()]}
LEGLAB={'mean':'World GNI per capita','med':"GNI per capita in the median person's country"}

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'axes.edgecolor':'#888',
 'axes.linewidth':1.0,'figure.facecolor':'white','xtick.labelsize':9.8,'ytick.labelsize':9.8,
 'axes.labelsize':15})
fig,ax=plt.subplots(figsize=(8,7.6),dpi=200)
YLO,YHI=230,72000
ax.fill_between(YR,YLO,tL,color=BAND['L'],zorder=0)
ax.fill_between(YR,tL,tM,color=BAND['LM'],zorder=0)
ax.fill_between(YR,tM,tU,color=BAND['UM'],zorder=0)
ax.fill_between(YR,tU,YHI,color=BAND['H'],zorder=0)
for t in (tL,tM,tU): ax.plot(YR,t,ls='--',lw=1.5,color='white',alpha=0.85,zorder=2)
NH=YR.index(2025)+1
for k in ('med','mean'):
    ax.plot(YR[:NH],S[k][:NH],color=LC[k],lw=3.4,zorder=5,solid_capstyle='round',path_effects=PEF[k])
    ax.plot(YR[NH-1:],S[k][NH-1:],color=LC[k],lw=3.0,ls=(0,(5,2.4)),zorder=5,path_effects=PEF[k])
ax.axvline(2025.5,ls=':',lw=1.8,color='white',zorder=3)
def dot(x,y,col,ms=11):
    ax.plot([x],[y],'o',mfc=col,mec=INK if col!=INK else PAPER,mew=2.6,ms=ms,zorder=9,clip_on=False)
ax.set_yscale('log'); ax.set_ylim(YLO,YHI); ax.set_xlim(1986.6,2050.5)
ticks=[250,500,1000,2000,5000,10000,20000,50000]
ax.set_yticks(ticks); ax.set_yticklabels(['$%s'%format(t,',') for t in ticks]); ax.minorticks_off()
ax.set_xticks([1987,2000,2010,2020,2030,2040,2050])
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
fig.tight_layout(rect=[0.012,0.360,0.885,0.995])
fig.canvas.draw(); REN=fig.canvas.get_renderer()
CURVES=[lambda x:V['mean'][x],lambda x:V['med'][x],
        lambda x:TH[x][0],lambda x:TH[x][1],lambda x:TH[x][2]]
placed=[]
def databox(t):
    bb=t.get_window_extent(REN); inv=ax.transData.inverted()
    (x0,y0)=inv.transform((bb.x0,bb.y0)); (x1,y1)=inv.transform((bb.x1,bb.y1))
    return x0,x1,min(y0,y1),max(y0,y1)
def ok(box,pad=0.026):
    x0,x1,ylo,yhi=box
    if x0<1986.8 or x1>2050.3: return False
    if ylo<YLO*1.02 or yhi>YHI*0.98: return False
    lo,hi=ylo/10**pad,yhi*10**pad
    xs=[x for x in YR if x0-0.5<=x<=x1+0.5]
    for f in CURVES:
        for x in xs:
            if lo<=f(x)<=hi: return False
    for p in placed:
        if x0<p[1]+0.4 and p[0]<x1+0.4 and ylo/10**0.012<p[3] and p[2]<yhi*10**0.012: return False
    return True
def place(lab,cands,fs,col):
    for (lx,ly,ha,va) in cands:
        fc,tc=(PAPER,AMBERTXT) if col=='#FFD166' else (PAPER,INK)
        t=ax.text(lx,ly,lab,fontsize=fs,fontweight='bold',color=tc,ha=ha,va=va,zorder=8,
                  linespacing=1.25,bbox=dict(boxstyle='round,pad=0.24',facecolor=fc,edgecolor='none'))
        b=databox(t)
        if ok(b): placed.append(b); return
        t.remove()
    fc,tc=(PAPER,AMBERTXT) if col=='#FFD166' else (PAPER,INK)
    t=ax.text(cands[0][0],cands[0][1],lab,fontsize=fs,fontweight='bold',color=tc,
              ha=cands[0][2],va=cands[0][3],zorder=8,linespacing=1.25,
              bbox=dict(boxstyle='round,pad=0.24',facecolor=fc,edgecolor='none'))
    placed.append(databox(t)); print('   !! no clear slot for',lab.replace(chr(10),' ')[:30])

SKIP={(2022,'med')}
SHIFT={(2010,'med'):-2.0}
FIXED={(2020,'med'):(2020.9,V['med'][2010]/1.42,'left')}
PREF={(1998,'med'):'down-right',(2010,'med'):'down-right',
      (2020,'med'):'down-right',(2026,'mean'):'up-left'}
TXT={(1998,'med'):'1998  China',(2010,'med'):'2010  China',
     (2020,'med'):'2020-22  Indonesia',
     (2026,'mean'):'2026  world average'+chr(10)+'at high-income line'}
for k,tn,yr,dirn in CR:
    y0=V[k][yr]; dot(yr,y0,LC[k],ms=11)
    if (yr,k) in SKIP: continue
    if (yr,k) in FIXED:
        fx,fy,fha=FIXED[(yr,k)]; cands=[(fx,fy,fha,'center')]
    elif PREF[(yr,k)]=='down-right':
        sh=SHIFT.get((yr,k),0.0)
        cands=[(yr+1.2+sh,y0/f,'left','center') for f in (1.42,1.58,1.78,2.00)]+\
              [(yr-1.2+sh,y0/f,'right','center') for f in (1.45,1.62)]
    else:
        cands=[(yr-1.2,y0*f,'right','center') for f in (1.38,1.55,1.75)]+\
              [(yr+1.2,y0*f,'left','center') for f in (1.40,1.58)]
    place(TXT[(yr,k)],cands,8.05,LC[k])

handles=[Line2D([],[],color=LC[k],lw=3.4,label=LEGLAB[k],path_effects=PEF[k]) for k in ('mean','med')]
fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(0.5,0.272),ncol=1,frameon=False,
           fontsize=11.5,columnspacing=2.2,handlelength=2.6,labelspacing=0.5)
BANDLAB=[('HIGH'+chr(10)+'INCOME',np.sqrt(TH[2050][2]*YHI)),
         ('UPPER-'+chr(10)+'MIDDLE',np.sqrt(TH[2050][1]*TH[2050][2])),
         ('LOWER-'+chr(10)+'MIDDLE',np.sqrt(TH[2050][0]*TH[2050][1])),
         ('LOW'+chr(10)+'INCOME',np.sqrt(YLO*TH[2050][0]))]
for (lab,yv),cc in zip(BANDLAB,['#283593','#00897B','#B8860B','#C62828']):
    ax.text(1.012,yv,lab,transform=ax.get_yaxis_transform(),fontsize=11.5,fontweight='bold',
            color=cc,ha='left',va='center',linespacing=1.25,clip_on=False,zorder=6)

MEDNOTE=("The second line is the population-weighted median: rank economies by GNI per capita, accumulate population, and take the "
"value of the economy in which the total first reaches half. It is the average income of the country the median person lives in, not the "
"median income of people: every person is assigned their own country's average, so all within-country distribution is discarded. Markers "
"show every threshold crossing, labelled with the year and the economy concerned. The fall from 2014 to 2017 combines a real dollar-terms "
"collapse across commodity exporters, Russia down 34 percent and Brazil 26 percent from 2014 to 2016, with a reshuffling that moved the "
"median slot from Thailand through Venezuela and Georgia to Azerbaijan, while China and India rose past it. ")
CAP=("Source: World Bank WDI, GNI per capita, Atlas method (NY.GNP.PCAP.CD) and population (SP.POP.TOTL); World Bank OGHIST "
"(1 July 2026) for the operational thresholds. Author's calculations and projections. Schellekens 2026, The Great Income Inversion, "
"Moving Frontiers."+chr(10)+
"Note: Shaded bands are the four income groups, named at right; their boundaries are the official thresholds year by year. World GNI per "
"capita is world GNI divided by world population, the population-weighted mean across economies. "+MEDNOTE+
"Values are for 2026, which reflects a nowcast based on a conservative constant-pace scenario that replicates country-level median per "
"capita income growth over the last decade. See Schellekens 2026 for methodology.")
caption(fig,ax,CAP,7.4,url_on_last_line=True)
fig.savefig(PNG,dpi=200); plt.close(fig)
title_band(PNG,"World GNI per capita crosses the high-income line in 2026",
   "Atlas GNI per capita in current US dollars, log scale, against the World Bank's income-classification thresholds",
   0.0265,0.0163)
