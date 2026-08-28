"""Chart 5: every economy as a multiple of the world average.

Reads chart-5-economies-by-multiple-of-world-average.csv and writes the png of the same name.
Run from inside this folder:  python3 chart-5-economies-by-multiple-of-world-average-build.py
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

hdr,rows=read_chart_csv('chart-5-economies-by-multiple-of-world-average.csv')
nm=[r['economy'] for r in rows]
r_=np.array([float(x['ratio_to_world_average']) for x in rows])
pop=np.array([float(x['population_millions']) for x in rows])
o=np.argsort(r_)
XM=np.log10(1450)-1.0
def area(pm):
    if pm<10: return 10.0
    return 10+((np.log10(pm)-1.0)/XM)**3.4*2200
r=r_
fig,ax=frame((6.8,8.6))
fig.tight_layout(rect=[0.02,0.335,0.99,0.985])
ax.axvspan(1e-3,1,color=RED,alpha=0.07,zorder=0)
ax.axvline(1,ls='--',lw=1.8,color=INK,zorder=4)
yv=np.arange(len(o))
sz=np.array([area(p) for p in pop[o]])
col=[RED if x<1 else INDIGO for x in r[o]]
ax.scatter(r[o],yv,s=sz,c=col,alpha=0.55,edgecolors='white',linewidths=0.6,zorder=5)
ax.set_xscale('log'); ax.set_xlim(0.011,26); ax.set_ylim(-10,len(o)+22)
ax.set_yticks([])
ticks=[0.02,0.05,0.1,0.25,0.5,1,2,4,10]
ax.set_xticks(ticks); ax.set_xticklabels(['0.02x','0.05x','0.1x','0.25x','0.5x','1x'+chr(10)+'world'+chr(10)+'average','2x','4x','10x'])
ax.minorticks_off()
ax.grid(axis='x',color='#E8E8E8',lw=0.8,zorder=0); ax.grid(axis='y',visible=False)
ax.spines['left'].set_visible(False)
fig.canvas.draw(); REN=fig.canvas.get_renderer()
CX,CY=ax.transData.transform(np.column_stack([r[o],yv])).T
RAD=np.sqrt(sz/np.pi)*fig.dpi/72.0
placed=[]
def clear(bb,skip_row):
    for i,(cx,cy,rad) in enumerate(zip(CX,CY,RAD)):
        if i==skip_row: continue
        nx=min(max(cx,bb.x0),bb.x1); ny=min(max(cy,bb.y0),bb.y1)
        if (nx-cx)**2+(ny-cy)**2 < (rad+2.0)**2: return False
    for pb in placed:
        if bb.x0<pb.x1+3 and pb.x0<bb.x1+3 and bb.y0<pb.y1+3 and pb.y0<bb.y1+3: return False
    ab=ax.get_window_extent(REN)
    if bb.x0<ab.x0+2 or bb.x1>ab.x1-2 or bb.y0<ab.y0+2 or bb.y1>ab.y1-2: return False
    return True
def lbl(name,prefer='left',fixed=None,vert=False,two=False):
    i=[k for k,x in enumerate(nm) if x==name]
    if not i: return
    i=i[0]; row=list(o).index(i)
    txt='%s  %.2fx'%(name,r[i])
    if two: txt='%s  %.2fx'%(name,r[i])+chr(10)+('poorest' if r[i]<1 else 'richest')
    c=RED if r[i]<1 else INDIGO
    inv=ax.transData.inverted()
    if fixed is not None:
        ha,dx,dy=fixed
        t=ax.text(r[i]*dx,row+dy,txt,fontsize=8.6,fontweight='bold',color=c,ha=ha,va='center',zorder=10)
        fig.canvas.draw(); bb=t.get_window_extent(REN); placed.append(bb)
        cx,cy,rad=CX[row],CY[row],RAD[row]
        if vert:
            lx=(bb.x0+bb.x1)/2; ye=bb.y1 if dy<0 else bb.y0
            (a0,b0)=inv.transform((lx,cy-rad-1.5 if dy<0 else cy+rad+1.5)); (a1,b1)=inv.transform((lx,ye))
            ax.plot([a0,a1],[b0,b1],color=c,lw=0.55,alpha=0.9,zorder=8)
        else:
            px=min(max(cx,bb.x0),bb.x1); py=min(max(cy,bb.y0),bb.y1)
            d=np.hypot(px-cx,py-cy)
            if d>rad+3:
                ux,uy=(px-cx)/d,(py-cy)/d
                (a0,b0)=inv.transform((cx+ux*(rad+1.5),cy+uy*(rad+1.5)))
                (a1,b1)=inv.transform((px-ux*1.5,py-uy*1.5))
                ax.plot([a0,a1],[b0,b1],color=c,lw=0.55,alpha=0.9,zorder=8)
        return
    sides=[('right',0.62),('left',1.6),('right',0.42),('left',2.3),('right',0.30),('left',3.2)]
    if prefer=='right': sides=[s for s in sides if s[0]=='left']+[s for s in sides if s[0]=='right']
    best=None
    for dy in (0,10,-10,20,-20,30,-30,42,-42,56,-56,72):
        for ha,dx in sides:
            t=ax.text(r[i]*dx,row+dy,txt,fontsize=8.6,fontweight='bold',color=c,ha=ha,va='center',zorder=10)
            fig.canvas.draw(); bb=t.get_window_extent(REN)
            if clear(bb,row): best=(t,bb,ha,dx,dy); break
            t.remove()
        if best: break
    if best is None:
        t=ax.text(r[i]*0.62,row,txt,fontsize=8.6,fontweight='bold',color=c,ha='right',va='center',zorder=10)
        fig.canvas.draw(); best=(t,t.get_window_extent(REN),'right',0.62,0)
        print('   !! no clear slot for',name)
    t,bb,ha,dx,dy=best; placed.append(bb)
    cx,cy,rad=CX[row],CY[row],RAD[row]
    px=min(max(cx,bb.x0),bb.x1); py=min(max(cy,bb.y0),bb.y1)
    d=np.hypot(px-cx,py-cy)
    if d>rad+3:
        ux,uy=(px-cx)/d,(py-cy)/d
        (dx0,dy0)=inv.transform((cx+ux*(rad+1.5),cy+uy*(rad+1.5)))
        (dx1,dy1)=inv.transform((px-ux*1.5,py-uy*1.5))
        ax.plot([dx0,dx1],[dy0,dy1],color=c,lw=0.55,alpha=0.9,zorder=8)
US_ROW=list(o).index([k for k,x in enumerate(nm) if x=='United States'][0])
BM_ROW=list(o).index([k for k,x in enumerate(nm) if x=='Bermuda'][0])
lbl('Bermuda',fixed=('center',1.0,-(BM_ROW-US_ROW)-22),vert=True,two=True)
lbl('United States')
lbl('China',fixed=('right',0.50,0))
lbl('India',fixed=('left',1.95,0))
lbl('Nigeria',fixed=('left',1.52,0))
lbl('Burundi',fixed=('center',1.0,17),vert=True,two=True)
LEG=[(1400,'1.4 bn'),(250,'250 m'),(50,'50 m')]
lx=10.0; legrows=[70,34,16]
ax.text(lx*0.60,legrows[0]+26,'Population',fontsize=8.8,fontweight='bold',color='#555',ha='left',va='center')
for (pv,plab),ry in zip(LEG,legrows):
    a=area(pv)
    ax.scatter([lx],[ry],s=a,c='#BBBBBB',alpha=0.75,edgecolors='white',linewidths=0.6,zorder=5)
    x_pt=ax.transData.transform((lx,ry))[0]+np.sqrt(a/np.pi)*fig.dpi/72.0+6
    ax.text(ax.transData.inverted().transform((x_pt,0))[0],ry,plab,fontsize=8.2,color='#555',ha='left',va='center')
ax.set_xlabel('GNI per capita as a multiple of world GNI per capita, log scale',fontsize=10.5)
ax.set_ylabel('197 economies, ranked poorest to richest',fontsize=10.5)
caption(fig,ax,SRC+PROJ+CAVEAT+("Each bubble is one economy, positioned by its GNI per capita relative to the world average and "
 "ranked from poorest at the bottom to richest at the top. Bubble area follows a logarithmic population scale; economies under ten "
 "million people are drawn at a fixed minimum size. Burundi at 0.016 times the world average and Bermuda at 9.7 times span a 600-fold "
 "range."),7.6,url_on_last_line=False,gap_lines=0.85,use_xlabel=True)
fig.savefig('chart-5-economies-by-multiple-of-world-average.png',dpi=200); plt.close(fig)
title_band('chart-5-economies-by-multiple-of-world-average.png','A 600-fold range, from Burundi to Bermuda',
 'Every economy as a multiple of world GNI per capita, bubble area on a log population scale, 2026',0.0285,0.0168)
