"""Reconstruction of the published figure from its csv. Typography follows the
Moving Frontiers chart conventions; pixel-level details may differ marginally
from the original render."""
import pandas as pd, numpy as np, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

plt.rcParams.update({'font.family':'DejaVu Sans',
    'axes.edgecolor':'#888','axes.linewidth':1.0,
    'figure.facecolor':'white','axes.facecolor':'white'})
RED,TEAL,INDIGO = '#C62828','#00897B','#283593'
HERE = os.path.dirname(os.path.abspath(__file__))

def caption(fig, lines, FIGH, y0=0.010):
    FS=7.0
    lh=22.0/(FIGH*200); ch=(FS*200/72)/(FIGH*200)
    n=len(lines)
    for i,ln in enumerate(lines):
        fig.text(0.012,y0+(n-1-i)*lh,ln,fontsize=FS,color='#666',
                 ha='left',va='bottom')
    fig.text(1-58/1600, y0-0.5*ch, 'movingfrontiers.substack.com',
             fontsize=FS,color='#999999',ha='right',va='bottom')
    return y0+n*lh

def title_band(OUT,title,subtitle):
    from PIL import Image, ImageDraw, ImageFont
    FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
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
    print('done',canvas.size)

d = pd.read_csv(os.path.join(HERE,'chart-3-evolution-of-country-terminology-by-major-news-outlets.csv'))
t = [int(m[:4])+(int(m[5:7])-1)/12 for m in d['month']]
FIGW,FIGH = 8, 6.6
fig,ax = plt.subplots(figsize=(FIGW,FIGH))
ax.plot(t,d['stories_per_1000_developing_country_12m'],color=RED,lw=3,
        label='"Developing country"')
ax.plot(t,d['stories_per_1000_developed_country_12m'],color=TEAL,lw=3,
        label='"Developed country"')
ax.plot(t,d['stories_per_1000_high_income_country_12m'],color=INDIGO,lw=3,
        label='"High-income country"')
for xv,lab in [(2016+3/12,'WDI 2016'),(2020+2/12,'COVID-19')]:
    ax.axvline(xv,color='#AAA',lw=1.2,ls=':')
    ax.text(xv,ax.get_ylim()[1]*1.02+3.25*0.02,lab,ha='left',va='bottom',
            fontsize=12,color='#333',clip_on=False)
ax.set_ylim(0,3.25)
ax.set_xticks(range(2016,2027,2)); ax.set_xlim(2015.7,2026.9)
ax.set_ylabel('Stories per 1,000, 12-month rolling',fontsize=13)
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.10),ncol=3,frameon=False,fontsize=11)
cap=[
 'Source: Media Cloud story index, January 2016 to July 2026, retrieved August 2026. Queries match the exact phrases developing country or',
 'countries, developed country or countries, and high-income country or countries, language English.',
 'Note: Pooled across all twelve outlets, grouped by country: Hong Kong SAR, China (South China Morning Post), India (The Times of India),',
 'Japan (The Japan Times), Malaysia (The Star), Nigeria (Punch), Qatar (Al Jazeera), Russia (Russian News Agency TASS), the United Kingdom',
 '(BBC and The Guardian) and the United States (CNN, Fox News and The New York Times). Complete months only and lines are twelve-month',
 'rolling shares. The Japan Times, Punch and the Russian News Agency (TASS) have gaps in daily index coverage, covering 87, 93 and 93',
 'percent of days, but results do not change significantly compared to a balanced sample. The dotted vertical rules mark the April 2016',
 'release of the World Development Indicators edition that dropped the developed and developing distinction, and the March 2020 onset of the',
 'COVID-19 pandemic.']
cap_top=caption(fig,cap,FIGH)
fig.tight_layout(rect=[0.02,cap_top+0.03,0.98,0.94])
OUT='chart-3-evolution-of-country-terminology-by-major-news-outlets.png'
fig.savefig(OUT,dpi=200); plt.close(fig)
title_band(OUT,'"Developed" and "developing" still rule the news',
           'Rolling twelve-month shares, twelve outlets, 2016 to 2026')
