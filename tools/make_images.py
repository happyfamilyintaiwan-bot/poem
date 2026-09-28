"""8月冬眠中｜詩圖產生器
用法：python3 tools/make_images.py 0102
讀 poems.json，輸出該首詩的日／中／英三張 1080x1350 圖到 out/ 資料夾。
字型不在 fonts/ 時會自動從 Google Fonts 下載。
"""
import os, sys, json, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(ROOT, 'fonts')
FONTS = {'Iansui-Regular.ttf': 'ofl/iansui/Iansui-Regular.ttf',
         'KleeOne-SemiBold.ttf': 'ofl/kleeone/KleeOne-SemiBold.ttf',
         'ShipporiMincho-Medium.ttf': 'ofl/shipporimincho/ShipporiMincho-Medium.ttf'}
os.makedirs(FD, exist_ok=True)
for f, u in FONTS.items():
    p = os.path.join(FD, f)
    if not os.path.exists(p):
        urllib.request.urlretrieve('https://raw.githubusercontent.com/google/fonts/main/' + u, p)
os.chdir(FD)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, random
W,H=2160,2700
paper=(241,236,225); ink=(56,50,44); grey=(140,131,120); red=(186,62,44)

def make_paper(seed=1):
    rng=np.random.default_rng(seed)
    b=np.full((H,W,3),paper,np.float32)+rng.normal(0,3.2,(H,W,1))
    s=rng.normal(0,1,(H//90,W//90)).astype(np.float32)
    s=np.array(Image.fromarray(((s+3)*40).clip(0,255).astype(np.uint8)).resize((W,H),Image.BICUBIC),np.float32)/255-.3
    b+=s[...,None]*6
    img=Image.fromarray(b.clip(0,255).astype(np.uint8))
    fib=Image.new('L',(W,H),0); d=ImageDraw.Draw(fib)
    for _ in range(260):
        x,y=rng.integers(0,W),rng.integers(0,H); a=rng.uniform(0,6.28); L=rng.integers(20,90)
        pts=[(x,y)]
        for k in range(6):
            a+=rng.normal(0,.5); x+=np.cos(a)*L/6; y+=np.sin(a)*L/6; pts.append((x,y))
        d.line(pts,fill=int(rng.integers(40,110)),width=2)
    fib=fib.filter(ImageFilter.GaussianBlur(1))
    img=Image.composite(Image.new('RGB',(W,H),(205,196,182)),img,fib.point(lambda v:int(v*.35)))
    return img

def inkify(mask,color,img,rough=(0.82,1.0),seed=2):
    rng=np.random.default_rng(seed)
    n=np.array(mask,np.float32)/255*rng.uniform(*rough,(H,W))
    mk=Image.fromarray((n*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    return Image.composite(Image.new('RGB',(W,H),color),img,mk)

def seal(img,x,y,size=150,chars='冬眠'):
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    d.rounded_rectangle((x,y,x+size,y+size),radius=14,fill=255)
    f=ImageFont.truetype(NOTO,int(size*.34),index=3)
    for i,c in enumerate(chars):
        d.text((x+size/2,y+size*(0.30+i*0.40)),c,font=f,fill=0,anchor='mm')
    rng=np.random.default_rng(5)
    n=np.array(m,np.float32)/255
    blot=np.array(Image.fromarray((rng.random((H//18,W//18))*255).astype(np.uint8)).resize((W,H),Image.BICUBIC),np.float32)/255
    n=n*np.clip(blot*0.9+.45,0,1)*0.88
    mk=Image.fromarray((n*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))
    return Image.composite(Image.new('RGB',(W,H),red),img,mk)

def render(title,stanzas,body_font,out,day='01',month='01',size=76,lh=150,gap=120,seed=1):
    img=make_paper(seed)
    tw=ImageFont.truetype('ShipporiMincho-Medium.ttf',40)
    small=Image.new('L',(W,H),0); s=ImageDraw.Draw(small)
    s.text((W/2,170),'A U G U S T   H I B E R N A T I O N',font=tw,fill=255,anchor='mt')
    num=ImageFont.truetype('ShipporiMincho-Medium.ttf',46)
    s.text((170,H-230),month,font=num,fill=255)
    s.text((W-170,H-230),day,font=num,fill=255,anchor='ra')
    s.line((W/2-40,H-205,W/2+40,H-205),fill=255,width=2)
    img=inkify(small,grey,img,seed=3)

    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    bf=ImageFont.truetype(body_font,size); tf=ImageFont.truetype(body_font,int(size*.9))
    total=int(size*.9)+200+sum(len(st)*lh for st in stanzas)+gap*(len(stanzas)-1)+190
    while (H-total)//2<380 and lh>110:  # 行數多時自動收緊行距，避免撞到上方英文標
        lh-=5; gap=max(80,gap-6)
        total=int(size*.9)+200+sum(len(st)*lh for st in stanzas)+gap*(len(stanzas)-1)+190
    y=(H-total)//2+10
    d.text((W/2,y),title,font=tf,fill=255,anchor='mt'); y+=int(size*.9)+200
    for st in stanzas:
        for line in st:
            d.text((W/2,y+size),line,font=bf,fill=255,anchor='ms'); y+=lh
        y+=gap
    sf=ImageFont.truetype(body_font,int(size*.82))
    sx=W-380; sy=y-20
    d.text((sx,sy+75),'8月冬眠中',font=sf,fill=255,anchor='rm')
    img=inkify(m,ink,img)

    img.resize((1080,1350),Image.LANCZOS).save(out)


if __name__ == '__main__':
    pid = sys.argv[1]
    data = json.load(open(os.path.join(ROOT, 'poems.json'), encoding='utf-8'))
    p = next(x for x in data['poems'] if x['id'] == pid)
    out = os.path.join(ROOT, 'out'); os.makedirs(out, exist_ok=True)
    mm, dd = pid[:2], pid[2:]
    kw = dict(day=dd, month=mm)
    render(f'〈{p["zh"]["title"]}〉', p['zh']['stanzas'], 'Iansui-Regular.ttf', os.path.join(out, f'{pid}_中文.png'), **kw)
    render(f'「{p["ja"]["title"]}」', p['ja']['stanzas'], 'KleeOne-SemiBold.ttf', os.path.join(out, f'{pid}_日本語.png'), size=72, **kw)
    if 'en' in p:
        render(f'\u201c{p["en"]["title"]}\u201d', p['en']['stanzas'], 'ShipporiMincho-Medium.ttf', os.path.join(out, f'{pid}_English.png'), size=70, lh=140, **kw)
    print('完成：', out)
