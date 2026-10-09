"""8月冬眠中｜詩教學影片產生器
用法：uv run --no-project --python 3.12 --with edge-tts --with pillow --with numpy python tools/make_video.py 0101 教學稿.md
讀教學稿（[CARD] [EN] [JA] [PAUSE 3s] 標記）與 poems.json，
輸出 out/0101/video/0101.mp4 與 0101.srt（YouTube 字幕）。
聲音用 edge-tts：英文 Jenny、日文 Nanami；英文句子裡的「日文」自動換 Nanami 唸。
"""
import os, re, sys, json, wave, asyncio, hashlib, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(ROOT, 'fonts')
W, H = 1920, 1080
SR = 24000
paper = (241, 236, 225); ink = (56, 50, 44); grey = (140, 131, 120); red = (186, 62, 44)

EN_VOICE, EN_RATE = 'en-US-JennyNeural', '-8%'
JA_VOICE = 'ja-JP-NanamiNeural'
JA_WORD_RATE, JA_POEM_RATE = '-25%', '-15%'
GAP_JA, GAP_EN, GAP_SENT, GAP_BLOCK, GAP_CARD, GAP_POEM = 0.45, 0.3, 0.45, 0.7, 0.5, 0.8
TTS_FIX = {'8月冬眠中': 'はちがつとうみんちゅう'}   # 只改念法，字幕照原文
SUB_FIX = {'poem dot knitting hiyori dot com': 'poem.knittinghiyori.com'}

def font(name, size): return ImageFont.truetype(os.path.join(FD, name), size)

# ---------- 解析教學稿 ----------
TOK = re.compile(r'\[(EN|JA|CARD|PAUSE (\d+(?:\.\d+)?)s)\]')

def split_sentences(t):
    return [s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z「"])|(?<=[.!?]")\s+', t) if s.strip()]

def parse(md, poem_ja_full):
    items = []  # ('card', title, extra_lines) / ('en', text) / ('ja', text) / ('pause', sec)
    lines = md.splitlines(); i = 0; first_ja = None
    while i < len(lines):
        ln = lines[i].strip(); i += 1
        if not ln or ln.startswith(('#', '>', '---')) or not ln.startswith('['):
            continue
        if ln.startswith('[CARD]'):
            title = ln[6:].strip(); extra = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('['):
                extra.append(lines[i].strip()); i += 1
            items.append(('card', title, extra)); continue
        parts = TOK.split(ln)  # ['', 'EN', None, 'text', ...]
        k = 1
        while k < len(parts):
            tag, sec, body = parts[k], parts[k+1], parts[k+2].strip(); k += 3
            if tag == 'EN': items.append(('en', body))
            elif tag == 'JA':
                if body.startswith('（'): body = first_ja or poem_ja_full
                first_ja = first_ja or body
                items.append(('ja', body))
            elif sec: items.append(('pause', float(sec)))
    return items

# ---------- 聲音 ----------
CACHE = None
async def tts(text, voice, rate):
    for a, b in TTS_FIX.items(): text = text.replace(a, b)
    key = hashlib.md5(f'{voice}|{rate}|{text}'.encode()).hexdigest()[:16]
    mp3 = os.path.join(CACHE, key + '.mp3'); wav = os.path.join(CACHE, key + '.wav')
    if not os.path.exists(wav):
        await edge_tts.Communicate(text, voice, rate=rate).save(mp3)
        af = ('silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
              'silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-18:TP=-2')
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mp3, '-af', af,
                        '-ar', str(SR), '-ac', '1', '-sample_fmt', 's16', wav], check=True)
    with wave.open(wav) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16)

def sil(sec): return np.zeros(int(SR * sec), np.int16)

def en_fragments(sentence):
    out = []
    for p in re.split(r'(「[^」]+」)', sentence):
        if p.startswith('「'): out.append(('ja', p[1:-1]))
        else:
            t = p.replace('"', '').replace('“', '').replace('”', '').strip(' ,:;')
            if re.search(r'[A-Za-z0-9]', t): out.append(('en', t))
    return out

# ---------- 畫面（日系手帳風：點格紙、便條紙、紙膠帶、螢光筆） ----------
FONT = 'KleeOne-SemiBold.ttf'   # 有長音符號 ō ū，英日都用它
page = (251, 248, 241); dotc = (226, 218, 204); ink = (74, 64, 58); soft = (150, 138, 128)
TAPES = [((242, 184, 198), 'stripe'), ((168, 213, 186), 'dot'), ((181, 211, 231), 'stripe'),
         ((246, 215, 139), 'dot'), ((214, 196, 232), 'plain')]
MARKER = (255, 226, 110, 150); MARKER2 = (255, 182, 193, 140)

def make_paper(seed=1):
    rng = np.random.default_rng(seed)
    b = np.full((H, W, 3), page, np.float32) + rng.normal(0, 1.6, (H, W, 1))
    img = Image.fromarray(b.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    for x in range(30, W, 40):
        for y in range(30, H, 40):
            d.ellipse((x - 1.6, y - 1.6, x + 1.6, y + 1.6), fill=dotc)
    return img

def is_ja(t): return bool(re.search(r'[぀-ヿ一-鿿]', t))

def wrap(d, text, f, maxw):
    cjk = is_ja(text) and ' ' not in text
    tokens, sep = (list(text), '') if cjk else (text.split(' '), ' ')
    out, cur = [], ''
    for tk in tokens:
        t = (cur + sep + tk) if cur else tk
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = tk
    if cur: out.append(cur)
    return out

def tape(size, color, pattern, rng):
    w, h = size
    t = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    zig = lambda x0, sgn: [(x0 + sgn * (4 if k % 2 else 0), k * h / 10) for k in range(11)]
    poly = zig(0, 1) + list(reversed(zig(w - 1, -1)))
    d.polygon(poly, fill=color + (205,))
    light = tuple(min(255, c + 28) for c in color) + (220,)
    if pattern == 'stripe':
        for x in range(-h, w, 26): d.line((x, h, x + h, 0), fill=light, width=9)
    elif pattern == 'dot':
        for x in range(14, w - 8, 26):
            for y in range(10, h - 4, 22): d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 255, 255, 170))
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
    t.putalpha(Image.fromarray(np.minimum(np.array(t.split()[3]), np.array(m))))
    return t

def paste_rot(base, layer, center, angle):
    r = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(r, (int(center[0] - r.width / 2), int(center[1] - r.height / 2)))

def marker(d, x0, x1, yc, h, color):
    d.rounded_rectangle((x0 - 6, yc - h * 0.05, x1 + 6, yc + h * 0.5), radius=10, fill=color)

def sparkle(d, x, y, r, color):
    d.line((x - r, y, x + r, y), fill=color, width=3); d.line((x, y - r, x, y + r), fill=color, width=3)
    d.line((x - r * .5, y - r * .5, x + r * .5, y + r * .5), fill=color, width=2)
    d.line((x - r * .5, y + r * .5, x + r * .5, y - r * .5), fill=color, width=2)

def quoted(sub): return re.findall(r'「([^」]+)」', sub or '')

def render(card, sub, header, bg, path):
    kind, title, extra = card
    seed = int(hashlib.md5((kind + title).encode()).hexdigest()[:6], 16)
    rng = np.random.default_rng(seed)
    img = bg.convert('RGBA')
    # 左上：紙膠帶標籤
    # 右下：網址膠帶
    url = tape((420, 56), (246, 215, 139), 'plain', rng)
    ImageDraw.Draw(url).text((210, 29), 'poem.knittinghiyori.com', font=font(FONT, 26), fill=ink, anchor='mm')
    paste_rot(img, url, (W - 250, H - 50), -2)

    # 便條紙
    PW, PH = 1400, 640
    pad = 40
    paper_l = Image.new('RGBA', (PW + pad * 2, PH + pad * 2), (0, 0, 0, 0))
    sh = Image.new('L', paper_l.size, 0); ImageDraw.Draw(sh).rounded_rectangle((pad + 6, pad + 12, pad + PW + 6, pad + PH + 12), 16, fill=70)
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    paper_l.paste((120, 100, 80, 255), (0, 0), sh)
    pd = ImageDraw.Draw(paper_l)
    pd.rounded_rectangle((pad, pad, pad + PW, pad + PH), 16, fill=(255, 255, 253, 255))
    for y in range(pad + 90, pad + PH - 30, 64):
        pd.line((pad + 60, y, pad + PW - 60, y), fill=(236, 230, 220, 255), width=2)
    cx, cy = pad + PW / 2, pad + PH / 2
    subq = quoted(sub)

    if kind == 'vocab':
        rows = [r.lstrip('- ').split('｜') for r in extra]
        fj, fe = font(FONT, 48), font(FONT, 38)
        cur = -1
        for n, (left, right) in enumerate(rows):
            jp = left.partition(' ')[0]
            if sub and (sub.strip('。') in jp.replace('〜', '、') or sub.rstrip('.').lower() == right.lower() or jp in subq): cur = n
        step = 64; y0 = pad + max(95, int((PH - len(rows) * step) / 2) + 20)
        for n, (left, right) in enumerate(rows):
            y = y0 + n * step; jp, _, rom = left.partition(' ')
            if n == cur: marker(pd, pad + 190, pad + PW - 120, y - 6, 52, MARKER)
            pd.rounded_rectangle((pad + 140, y - 14, pad + 168, y + 14), 5, outline=soft, width=3)
            if cur >= 0 and n <= cur:
                pd.line((pad + 143, y, pad + 153, y + 11, pad + 172, y - 16), fill=(220, 110, 130), width=5)
            pd.text((pad + 210, y), jp, font=fj, fill=ink, anchor='lm')
            pd.text((pad + 640, y), rom, font=fe, fill=soft, anchor='lm')
            pd.text((pad + 1000, y), right, font=fe, fill=ink, anchor='lm')
    elif kind == 'pairs':
        rows = []
        for r in extra:
            sides = []
            for side in r.lstrip('- ').split(' → '):
                left, _, mean = side.partition('｜'); jp, _, rom = left.partition(' ')
                sides.append((jp, rom, mean))
            rows.append(sides)
        fj, fs = font(FONT, 56), font(FONT, 30)
        xl, xr, xa = pad + 150, pad + 790, pad + 650
        for x, txt, col in ((xl, 'Going out  (away from you)', (242, 184, 198)), (xr, 'Coming in  (toward you)', (168, 213, 186))):
            tw = int(pd.textlength(txt, font=font(FONT, 32))) + 60
            t = tape((tw, 58), col, 'plain', rng); ImageDraw.Draw(t).text((tw / 2, 30), txt, font=font(FONT, 32), fill=ink, anchor='mm')
            paper_l.alpha_composite(t, (int(x - 20), pad + 100))
        side_hit = 0 if (sub or '').startswith('Going out') else 1 if (sub or '').startswith('Coming in') else -1
        y = pad + 245
        for sides in rows:
            row_hit = any(sd[0] in subq for sd in sides)
            for k, (jp, rom, mean) in enumerate(sides):
                x = xl if k == 0 else xr; jw = pd.textlength(jp, font=fj)
                if (side_hit == k) if side_hit >= 0 else row_hit: marker(pd, x, x + jw, y - 8, 56, MARKER if k == 0 else MARKER2)
                pd.text((x, y), jp, font=fj, fill=ink, anchor='lm')
                pd.text((x + jw + 28, y + 6), f'{rom} · {mean}', font=fs, fill=soft, anchor='lm')
            pd.line((xa, y, xa + 70, y), fill=(236, 128, 100), width=10)
            pd.polygon([(xa + 70, y - 20), (xa + 100, y), (xa + 70, y + 20)], fill=(236, 128, 100))
            for dx in range(xl, pad + PW - 110, 28):
                pd.line((dx, y + 52, dx + 14, y + 52), fill=(160, 196, 220), width=3)
            y += 100
    elif kind == 'poem':
        ja, en = extra
        fj, fe = font(FONT, 42), font(FONT, 32)
        n = sum(len(s) for s in ja) + len(ja) - 1; lh = 50
        y = cy - n * lh / 2 + lh / 2
        cur = [s for s in (sub or '').split('、')]
        words = lambda t: set(re.findall(r"[a-z']+", t.lower())) - {'the', 'a', 'i', 'it', 'is', 'in', 'my', 'you', 'we'}
        sw = words(sub or '')
        best = max(range(len(en)), key=lambda k: len(words(' '.join(en[k])) & sw))
        en_hit = best if len(words(' '.join(en[best])) & sw) >= 3 else -1
        norm = lambda t: re.sub(r"[^a-z0-9' ]", '', t.lower()).strip()
        jsub = re.sub(r'[、。，\s]', '', sub or ''); esub = norm(sub or '')
        en_lines = {b for se in en for b in se if b and len(norm(b)) > 3 and norm(b) in esub}
        for si, (sj, se) in enumerate(zip(ja, en)):
            for a, b in zip(sj + [''] * (len(se) - len(sj)), se + [''] * (len(sj) - len(se))):
                if a and jsub and re.sub(r'[、。，]', '', a) in jsub:
                    tl = pd.textlength(a, font=fj); marker(pd, cx - 60 - tl, cx - 60, y - 20, 44, MARKER)
                pd.text((cx - 60, y), a, font=fj, fill=ink, anchor='rm')
                eh = bool(b) and (b in en_lines if en_lines else si == en_hit)
                if eh:
                    marker(pd, cx + 40, cx + 40 + pd.textlength(b, font=fe), y - 16, 38, MARKER2)
                pd.text((cx + 40, y), b, font=fe, fill=ink if eh else soft, anchor='lm'); y += lh
            y += lh * 0.8
        pd.line((cx - 10, pad + 60, cx - 10, pad + PH - 60), fill=(236, 230, 220, 255), width=2)
    else:
        parts = [p.strip() for p in title.replace('🔔', '♪').split(' / ')]
        main, rest = parts[0], parts[1:] + extra
        fm = font(FONT, min(112, int(1180 / max(len(main), 1))))
        y = cy - (60 + 36 * len(rest)) + 20
        tl = pd.textlength(main, font=fm); left = cx - tl / 2
        for q in subq:
            k = main.find(q)
            if k >= 0 and q != main:
                x0 = left + pd.textlength(main[:k], font=fm); x1 = x0 + pd.textlength(q, font=fm)
                marker(pd, x0, x1, y - 10, 70, MARKER if len(subq) < 2 or q == subq[0] else MARKER2)
        pd.text((cx, y), main, font=fm, fill=ink, anchor='mm')
        # 手繪波浪底線
        wy = y + 78; pts = [(cx - tl / 2 + i * 12, wy + 5 * np.sin(i * 0.9)) for i in range(int(tl / 12) + 1)]
        if len(pts) > 1: pd.line(pts, fill=(242, 184, 198, 255), width=4)
        y += 140
        for r in rest:
            pd.text((cx, y), r, font=font(FONT, 44), fill=soft, anchor='mm'); y += 70

    ang = float(rng.uniform(-1.2, 1.2))
    pcx, pcy = W / 2, 480
    paste_rot(img, paper_l, (pcx, pcy), ang)
    # 紙膠帶貼在便條紙上
    hf = font(FONT, 40); lw = int(ImageDraw.Draw(img).textlength(header, font=hf)) + 160
    lab = tape((lw, 86), (168, 213, 186), 'plain', rng)
    ImageDraw.Draw(lab).text((lw / 2, 44), header, font=hf, fill=ink, anchor='mm')
    paste_rot(img, lab, (pcx, pcy - PH / 2 + 4), ang + 1.2)
    d = ImageDraw.Draw(img)
    sparkle(d, pcx + PW / 2 + 40, pcy + PH / 2 - 60, 16, (246, 190, 90))
    sparkle(d, pcx - PW / 2 - 50, pcy + 80, 11, (242, 160, 180))

    if sub:
        for a, b in SUB_FIX.items(): sub = sub.replace(a, b)
        f = font(FONT, 46)
        ls = wrap(d, sub, f, W - 420)
        y = 895 - (len(ls) - 1) * 30
        for l in ls:
            d.text((W / 2, y), l, font=f, fill=ink, anchor='mm'); y += 58
    img.convert('RGB').save(path)

# ---------- 主程式 ----------
async def main(pid, script_path):
    global CACHE
    data = json.load(open(os.path.join(ROOT, 'poems.json'), encoding='utf-8'))
    p = next(x for x in data['poems'] if x['id'] == pid)
    out = os.path.join(ROOT, 'out', pid, 'video'); CACHE = os.path.join(out, 'cache')
    os.makedirs(CACHE, exist_ok=True); fr = os.path.join(out, 'frames'); os.makedirs(fr, exist_ok=True)
    items = parse(open(script_path, encoding='utf-8').read(), '。'.join([p['ja']['title']] + ['、'.join(s) for s in p['ja']['stanzas']]) + '。')
    header = f'Learn Japanese with a Poem  ✿  No.{pid}'

    audio, timeline = [], []  # timeline: (card, subtitle, seconds)
    card = ('text', p['ja']['title'], []); t_audio = 0
    def push(chunk, sub):
        nonlocal t_audio
        audio.append(chunk); timeline.append((card, sub, len(chunk) / SR))
    for it in items:
        if it[0] == 'card':
            title, extra = it[1], it[2]
            if title.startswith('單字表'): card = ('vocab', title, extra)
            elif title.startswith('對照表'): card = ('pairs', title, extra)
            elif title.startswith('全詩'): card = ('poem', title, (p['ja']['stanzas'], p['en']['stanzas']))
            else: card = ('text', title, extra)
            push(sil(GAP_CARD), ''); continue
        if it[0] == 'pause':
            push(sil(it[1]), timeline[-1][1] if timeline else ''); continue
        if it[0] == 'ja':
            lines = [s for s in it[1].split('。') if s.strip()]
            for n, s in enumerate(lines):
                push(await tts(s + '。', JA_VOICE, JA_POEM_RATE), s)
                push(sil(GAP_POEM if n < len(lines) - 1 else GAP_BLOCK), s)
            continue
        for sent in split_sentences(it[1]):
            prev = None
            for lang, frag in en_fragments(sent):
                if prev: push(sil(GAP_JA if 'ja' in (prev, lang) else GAP_EN), sent)
                push(await tts(frag, JA_VOICE if lang == 'ja' else EN_VOICE, JA_WORD_RATE if lang == 'ja' else EN_RATE), sent)
                prev = lang
            push(sil(GAP_SENT), sent)
        push(sil(GAP_BLOCK - GAP_SENT), timeline[-1][1])
    push(sil(2.0), '')

    # 合併同畫面的片段，逐張畫圖
    merged = []
    for c, s, sec in timeline:
        if merged and merged[-1][0] == c and merged[-1][1] == s: merged[-1][2] += sec
        else: merged.append([c, s, sec])
    bg = make_paper()
    concat = open(os.path.join(fr, 'list.txt'), 'w')
    for n, (c, s, sec) in enumerate(merged):
        f = os.path.join(fr, f'{n:04d}.png'); render(c, s, header, bg, f)
        concat.write(f"file '{f}'\nduration {sec:.4f}\n")
    concat.write(f"file '{f}'\n"); concat.close()

    wav = os.path.join(out, 'audio.wav')
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.concatenate(audio).tobytes())
    mp4 = os.path.join(out, f'{pid}.mp4')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(fr, 'list.txt'),
                    '-i', wav, '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-tune', 'stillimage', '-crf', '20',
                    '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', mp4], check=True)

    # SRT
    def ts(x): return f'{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int(x*1000%1000):03d}'
    t = 0; n = 0; srt = []
    for c, s, sec in merged:
        if s:
            for a, b in SUB_FIX.items(): s = s.replace(a, b)
            n += 1; srt.append(f'{n}\n{ts(t)} --> {ts(t+sec)}\n{s}\n')
        t += sec
    open(os.path.join(out, f'{pid}.srt'), 'w', encoding='utf-8').write('\n'.join(srt))
    print(f'完成：{mp4}（{t:.1f} 秒，{len(merged)} 個畫面）')

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1], sys.argv[2]))
