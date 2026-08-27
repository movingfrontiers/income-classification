"""Chart 9: how many economies sit in each income group.

Reads chart-9-how-many-economies-sit-in-each-income-group.csv and writes the png of the same name.
Run from inside this folder:  python3 chart-9-how-many-economies-sit-in-each-income-group-build.py
"""
import csv
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image, ImageDraw, ImageFont

SRC=("Source: World Bank OGHIST (1 July 2026), Country Analytical History, with WDI GNI per capita, Atlas method; author's calculations."+chr(10))

# ---------------------------------------------------------------- shared helpers
def read_chart_csv(path):
    rows=[r for r in csv.reader(open(path)) if r and not r[0].startswith('#')]
    hdr=rows[0]
    return hdr,[dict(zip(hdr,r)) for r in rows[1:]]

def place_marks(fig, ax, YY, series, marks, fontsize=10.5, pad_frac=0.014, align_x=None, override=None, dots=True, dotsize=8.5):
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
        xs=[q for q in YY if a0-0.7<=q<=a1+0.7]
        for s in series:
            if any(lo-pad<=s[YY.index(q)]<=hi+pad for q in xs): return True
        gx,gy=0.8,span*0.018
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
                    for dx,ha in ((-0.6,'right'),(0.6,'left'),(0.0,'center'),
                                  (2.5,'left'),(-2.5,'right'),(5.0,'left'),(-5.0,'right'),
                                  (8.0,'left'),(-8.0,'right')):
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

def caption(fig, ax, cap, fs=7.8, gap_lines=2.0):
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
    lastmax=right-w(URL,UFS)-2.0*CW-x0
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
    FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
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

AMBER='#F9A825'; AMBERTXT='#B8860B'; RED='#C62828'; INDIGO='#283593'
def panel(ax,ymax,ticks,lab,tickfmt):
    ax.axvspan(2025.5,2050,color='#F4F4F4',zorder=0)
    ax.axvline(2025.5,ls=':',lw=1.4,color='#777',zorder=1)
    ax.grid(axis='y',color='#E6E6E6',lw=0.8,zorder=0); ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.set_xlim(1987,2050); ax.set_xticks([1987,2000,2010,2020,2030,2040,2050])
    ax.set_ylim(0,ymax); ax.set_yticks(list(ticks))
    if tickfmt: ax.set_yticklabels([tickfmt(v) for v in ticks])
    ax.set_title(lab,fontsize=13,fontweight='bold',color='#333',pad=8)
def draw(ax,YY,S,col,NH):
    ax.plot(YY[:NH],S[:NH],color=col,lw=2.9,zorder=5,solid_capstyle='round')
    ax.plot(YY[NH-1:],S[NH-1:],color=col,lw=2.5,ls=(0,(4.5,2.2)),zorder=5)

CSV='chart-9-how-many-economies-sit-in-each-income-group.csv'
PNG='chart-9-how-many-economies-sit-in-each-income-group.png'
LEVCOLS={'LIC':'low_income_economies','MIC':'middle_income_economies','HIC':'high_income_economies'}
SHCOLS={'LIC':'low_income_share_of_classified_percent','MIC':'middle_income_share_of_classified_percent','HIC':'high_income_share_of_classified_percent'}
LEVTTL='Number of economies'
SHTTL='Percent of all classified economies'
YMAXL=152
TICKSL=range(0,131,25)
FMTL=None
YMAXS=70
TICKSS=range(0,61,10)
VALL=lambda v:'%d'%v
VALS=lambda v:'%.0f%%'%v
FORCE_BELOW=()
OVR={'lev':{(RED,1987):(1988.6,53.5,'left','bottom'),(AMBERTXT,1987):(1990.4,75.0,'left','center')}}
NOTE=("Note: Counts of economies, not people. Middle income combines the lower-middle and upper-middle groups. Classifications are actual "
"through 2025 and projected from 2026. Shares are of all economies classified in that year, a total that rises from 166 in 1987 to 218 "
"from 2025 on as new economies enter, so the counts and the shares carry different information. Projection: GNI per capita grows at each "
"economy's median annual rate over the decade to 2025, floored at the 1.244 percent threshold drift so that no economy is downgraded, "
"and capped at the 90th percentile of decade medians within its own 2025 income group. All three thresholds drift up at 1.244 percent a "
"year, the median annual increase in the published thresholds over the same decade to 2025.")
TITLE="How many economies sit in each income group"
SUB="Number of economies in each broad income group, and as a percent of all classified economies"

hdr,rows=read_chart_csv(CSV)
YY=[int(r['year']) for r in rows]
LEV={k:[float(r[c]) for r in rows] for k,c in LEVCOLS.items()}
SH ={k:[float(r[c]) for r in rows] for k,c in SHCOLS.items()}
NH=YY.index(2025)+1
KEYS=('LIC','MIC','HIC')
COL={'LIC':RED,'MIC':AMBER,'HIC':INDIGO}
TXT={'LIC':RED,'MIC':AMBERTXT,'HIC':INDIGO}
NAME={'LIC':'Low income','MIC':'Middle income','HIC':'High income'}
ALIGN={1987:(1988.6,'left'),2025:(2024.4,'right'),2050:(2049.4,'right')}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.edgecolor':'#888',
 'axes.linewidth':1.0,'figure.facecolor':'white','xtick.labelsize':12,'ytick.labelsize':12})
fig,axs=plt.subplots(1,2,figsize=(9.6,6.3),dpi=200)
for ax,(D,ttl,ymax,ticks,fmt,vf,which) in zip(axs,[(LEV,LEVTTL,YMAXL,TICKSL,FMTL,VALL,'lev'),
                                                   (SH,SHTTL,YMAXS,TICKSS,None,VALS,'sh')]):
    panel(ax,ymax,ticks,ttl,fmt)
    for k in KEYS: draw(ax,YY,D[k],COL[k],NH)
    MK=[]
    for k in KEYS:
        for yr in (1987,2025,2050):
            pref='below' if (k,yr) in FORCE_BELOW else 'above'
            MK.append((yr,vf(D[k][YY.index(yr)]),pref,D[k],TXT[k]))
    place_marks(fig,ax,YY,[D[k] for k in KEYS],MK,fontsize=10.0,align_x=ALIGN,
                override=(OVR.get(which) if OVR else None))
    ax.text(2026.4,ymax*0.955,'projected',fontsize=10.5,color='#777',style='italic',ha='left',va='top')
fig.legend(handles=[Line2D([],[],color=COL[k],lw=3.0,label=NAME[k]) for k in KEYS],
           loc='lower center',bbox_to_anchor=(0.5,0.268),ncol=3,frameon=False,fontsize=12,
           columnspacing=3.0,handlelength=2.2)
fig.tight_layout(rect=[0,0.340,1,0.985]); fig.subplots_adjust(wspace=0.16)
caption(fig,axs[0],SRC+NOTE)
fig.savefig(PNG,dpi=200); plt.close(fig)
title_band(PNG,TITLE,SUB)
