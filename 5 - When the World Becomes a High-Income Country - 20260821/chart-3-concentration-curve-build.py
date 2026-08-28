"""Chart 3: concentration curve of world GNI across people.

Reads chart-3-concentration-curve.csv and writes the png of the same name.
Run from inside this folder:  python3 chart-3-concentration-curve-build.py
"""
import csv
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

RED='#C62828'; AMBER='#F9A825'; AMBERTXT='#B8860B'; INDIGO='#283593'; INK='#141414'

SRC=("Source: World Bank OGHIST classification and income thresholds, 1 July 2026; GNI per capita, Atlas method, and population from "
"World Bank WDI, July 2026 release; UN World Population Prospects 2024, medium variant; author's calculations and projections. "
"Schellekens 2026, The Great Income Inversion, Moving Frontiers." + chr(10))
PROJ=("Note: Values are for 2026, which reflects a nowcast based on a conservative constant-pace scenario that replicates country-level "
"median per capita income growth over the last decade. See Schellekens 2026 for methodology. ")
CAVEAT=("World GNI per capita is world GNI divided by world population, $14,801 in 2026, covering 8.14 billion people. Every person "
"carries their own country's average, so this is inequality between countries, not within them. ")

def frame(figsize):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.edgecolor':'#888',
     'axes.linewidth':1.0,'figure.facecolor':'white','xtick.labelsize':10,'ytick.labelsize':10})
    fig,ax=plt.subplots(figsize=figsize,dpi=200)
    ax.grid(axis='y',color='#E8E8E8',lw=0.8,zorder=0); ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    return fig,ax

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

hdr,rows=read_chart_csv('chart-3-concentration-curve.csv')
cw=np.array([0.0]+[float(r['cumulative_population_share_percent']) for r in rows])
cg=np.array([0.0]+[float(r['cumulative_gni_share_percent']) for r in rows])
pop=np.array([float(r['population_millions']) for r in rows])
below=np.array([r['at_or_below_world_average']=='yes' for r in rows])
P=100*pop[below].sum()/pop.sum()
fig,ax=frame((7.6,6.4))
fig.tight_layout(rect=[0.02,0.300,0.99,0.985])
ax.plot([0,100],[0,100],ls='--',lw=1.4,color='#999',zorder=2)
ax.fill_between(cw,cg,cw,color=INDIGO,alpha=0.13,zorder=1)
ax.plot(cw,cg,color=INDIGO,lw=3.2,zorder=5,solid_capstyle='round')
ax.plot([P,P],[0,np.interp(P,cw,cg)],ls=':',lw=1.6,color=RED,zorder=4)
ax.plot([P],[np.interp(P,cw,cg)],'o',mfc='white',mec=RED,mew=2.6,ms=11,zorder=9,clip_on=False)
def note(mx,my,lx,ly,txt,col,ha):
    ax.plot([mx],[my],'o',mfc='white',mec=col,mew=2.4,ms=9,zorder=9)
    t=ax.text(lx,ly,txt,fontsize=9.5,fontweight='bold',color=col,ha=ha,va='center',linespacing=1.3,zorder=10)
    fig.canvas.draw()
    bb=t.get_window_extent(fig.canvas.get_renderer()); inv=ax.transData.inverted()
    (x0,y0)=inv.transform((bb.x0,bb.y0)); (x1,y1)=inv.transform((bb.x1,bb.y1))
    ax.plot([mx,(x0+x1)/2],[my,(y0 if my<(y0+y1)/2 else y1)],color=col,lw=1.1,zorder=8)
note(50,np.interp(50,cw,cg),34,26,'Poorest half:'+chr(10)+'%.0f%% of world GNI'%np.interp(50,cw,cg),INDIGO,'left')
note(P,np.interp(P,cw,cg),56,39,'World average sits at'+chr(10)+'the %.0fth percentile'%P,RED,'left')
note(90,np.interp(90,cw,cg),87.5,66,'Richest tenth:'+chr(10)+'%.0f%% of GNI'%(100-np.interp(90,cw,cg)),INDIGO,'right')
ax.set_xlim(0,100); ax.set_ylim(0,100)
ax.set_xticks(range(0,101,20)); ax.set_yticks(range(0,101,20))
ax.set_xlabel('Cumulative share of world population, percent',fontsize=10.5)
ax.set_ylabel('Cumulative share of world GNI, percent',fontsize=10.5)
ax.grid(axis='x',color='#E8E8E8',lw=0.8,zorder=0)
caption(fig,ax,SRC+PROJ+CAVEAT+("Economies are ranked from poorest to richest; the curve accumulates their population and "
 "their GNI. The dashed diagonal is the line of equal income per person everywhere. The marked point is where world GNI per capita "
 "falls in the ranked distribution: 64 percent of people live in an economy poorer than the world average, and those economies "
 "together hold 17 percent of world GNI."),7.6,url_on_last_line=False,gap_lines=0.85,use_xlabel=True)
fig.savefig('chart-3-concentration-curve.png',dpi=200); plt.close(fig)
title_band('chart-3-concentration-curve.png','Between countries, half of humanity lives on nine percent of world income',
 'Cumulative share of world GNI against cumulative share of world population, economies ranked by GNI per '
 'capita, 2026; every person carries their country average, so inequality within countries is not shown',0.0285,0.0168)
