"""8月冬眠中｜YouTube 縮圖產生器（日系手帳風，1280x720）
用法：uv run --no-project --python 3.12 --with edge-tts --with pillow --with numpy python tools/make_thumbnail.py 0101 "#1" "借りる|borrow" "貸す|lend"
輸出 out/0101/video/thumbnail.png
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_video as mv

W, H = 1280, 720
BLACK, BOLD = 'ZenMaruGothic-Black.ttf', 'ZenMaruGothic-Bold.ttf'

def main(pid, num, left, right):
    p = next(x for x in json.load(open(os.path.join(mv.ROOT, 'poems.json'), encoding='utf-8'))['poems'] if x['id'] == pid)
    rng = np.random.default_rng(7)
    img = Image.new('RGBA', (W, H), mv.page + (255,)); d = ImageDraw.Draw(img)
    for x in range(20, W, 32):
        for y in range(20, H, 32): d.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=mv.dotc)

    # 便條紙
    PW, PH, pad = 1140, 540, 30
    pl = Image.new('RGBA', (PW + pad * 2, PH + pad * 2), (0, 0, 0, 0))
    sh = Image.new('L', pl.size, 0); ImageDraw.Draw(sh).rounded_rectangle((pad + 5, pad + 10, pad + PW + 5, pad + PH + 10), 14, fill=80)
    pl.paste((120, 100, 80, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    pd = ImageDraw.Draw(pl)
    pd.rounded_rectangle((pad, pad, pad + PW, pad + PH), 14, fill=(255, 255, 253, 255))
    for y in range(pad + 70, pad + PH - 20, 56): pd.line((pad + 40, y, pad + PW - 40, y), fill=(236, 230, 220, 255), width=2)

    if ';' in right:  # 變化版型：左邊一個大字，右邊列出變化（例："見ない|don't look;見た|looked"）
        forms_layout(pd, pad, PW, left, right)
    else:
        pair_layout(pd, pad, PW, left, right)
    pd.text((pad + PW / 2, pad + PH - 55), f'{p["ja"]["title"]}  {p["en"]["title"]}  ·  an original poem',
            font=mv.font(BOLD, 36), fill=mv.ink, anchor='mm')
    mv.paste_rot(img, pl, (W / 2, H / 2 + 30), -1.2)

    # 正中間一條紙膠帶
    head = f'Learn Japanese with a Poem {num}'
    hf = mv.font(BOLD, 44); tw = int(d.textlength(head, font=hf)) + 140
    t = mv.tape((tw, 92), (168, 213, 186), 'plain', rng)
    ImageDraw.Draw(t).text((tw / 2, 47), head, font=hf, fill=mv.ink, anchor='mm')
    mv.paste_rot(img, t, (W / 2, H / 2 + 30 - PH / 2 + 2), 0)
    d = ImageDraw.Draw(img)
    mv.sparkle(d, W - 60, H - 110, 20, (246, 190, 90)); mv.sparkle(d, 55, 330, 14, (242, 160, 180))

    out = os.path.join(mv.ROOT, 'out', pid, 'video', 'thumbnail.png')
    img.convert('RGB').save(out, optimize=True)
    print('完成：', out, os.path.getsize(out) // 1024, 'KB')

def forms_layout(pd, pad, PW, left, right):
    lj, le = left.split('|')
    rows = [r.split('|') for r in right.split(';')]
    big = mv.font(BLACK, 190); rf = mv.font(BLACK, 70); mf = mv.font(BOLD, 32)
    cy = pad + 260
    lw = pd.textlength(lj, font=big)
    lx = pad + 70
    mv.marker(pd, lx, lx + lw, cy + 10, 170, (255, 182, 193, 190))
    pd.text((lx, cy), lj, font=big, fill=mv.ink, anchor='lm')
    pd.text((lx + lw / 2, cy + 150), le, font=mv.font(BOLD, 52), fill=mv.soft, anchor='mm')
    ax = lx + lw + 36
    pd.line((ax, cy, ax + 70, cy), fill=(236, 128, 100), width=12)
    pd.polygon([(ax + 70, cy - 24), (ax + 104, cy), (ax + 70, cy + 24)], fill=(236, 128, 100))
    rx = ax + 130; step = 112 if len(rows) > 2 else 150; y = cy - step * (len(rows) - 1) / 2 - (20 if len(rows) <= 2 else 0)
    for jp, mean in rows:
        jw = pd.textlength(jp, font=rf)
        mv.marker(pd, rx, rx + jw, y + 2, 70, (255, 226, 110, 200))
        pd.text((rx, y), jp, font=rf, fill=mv.ink, anchor='lm')
        if rx + jw + 26 + pd.textlength(mean, font=mf) <= pad + PW - 30:
            pd.text((rx + jw + 26, y + 8), mean, font=mf, fill=mv.soft, anchor='lm')
        else:  # 放不下就換到日文下一行
            pd.text((rx + 4, y + 58), mean, font=mf, fill=mv.soft, anchor='lm')
        y += step

def pair_layout(pd, pad, PW, left, right):
    (lj, le), (rj, re_) = left.split('|'), right.split('|')
    big = mv.font(BLACK, 160); vs = mv.font(BOLD, 64); sub = mv.font(BOLD, 52)
    cy = pad + 250
    lw, rw, vw = pd.textlength(lj, font=big), pd.textlength(rj, font=big), pd.textlength('vs', font=vs)
    gap = 44; total = lw + vw + rw + gap * 2
    x0 = pad + (PW - total) / 2
    lx, vx, rx = x0, x0 + lw + gap, x0 + lw + gap * 2 + vw
    mv.marker(pd, lx, lx + lw, cy + 5, 150, (255, 182, 193, 190))
    mv.marker(pd, rx, rx + rw, cy + 5, 150, (255, 226, 110, 200))
    pd.text((lx, cy), lj, font=big, fill=mv.ink, anchor='lm')
    pd.text((vx, cy + 20), 'vs', font=vs, fill=(236, 128, 100), anchor='lm')
    pd.text((rx, cy), rj, font=big, fill=mv.ink, anchor='lm')
    pd.text((lx + lw / 2, cy + 150), le, font=sub, fill=mv.soft, anchor='mm')
    pd.text((rx + rw / 2, cy + 150), re_, font=sub, fill=mv.soft, anchor='mm')

if __name__ == '__main__':
    main(*sys.argv[1:5])
