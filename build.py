"""8月冬眠中｜poem.knittinghiyori.com 產生器
用法：編輯 poems.json 後執行  python3 build.py
會產生 index.html、每首詩的資料夾（例如 0101/index.html）、404.html、分享預覽圖、sitemap.xml
"""
import json, os, html
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT, 'poems.json'), encoding='utf-8'))
SITE = DATA['site']; URL = SITE['url'].rstrip('/')
POEMS = sorted(DATA['poems'], key=lambda p: p['id'])
MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
# 和色：每個月一個季節色（顏色, 日文, 中文, 英文）
MONTHS = [('#c8707e', '紅梅', '紅梅', 'Red Plum'), ('#8f8b4e', '鶯', '鶯色', 'Bush Warbler'),
          ('#cf8f98', '桜', '櫻', 'Cherry Blossom'), ('#5f9477', '若竹', '若竹', 'Young Bamboo'),
          ('#8a80b3', '藤', '藤', 'Wisteria'), ('#6a86b6', '紫陽花', '紫陽花', 'Hydrangea'),
          ('#4c83ad', '露草', '露草', 'Dayflower'), ('#c99a33', '向日葵', '向日葵', 'Sunflower'),
          ('#a77490', '萩', '萩', 'Bush Clover'), ('#c47a4c', '柿', '柿', 'Persimmon'),
          ('#9a7449', '朽葉', '朽葉', 'Fallen Leaves'), ('#667891', '藍鼠', '藍鼠', 'Indigo Grey')]
E = html.escape
V = date.today().strftime('%Y%m%d')  # cache-busting for css/js

FONTS = ('https://fonts.googleapis.com/css2?family=Iansui&family=Klee+One:wght@400;600'
         '&family=Shippori+Mincho:wght@500&display=swap')


def L(ja, zh, en=None, tag='span'):
    en = ja if en is None else en
    return (f'<{tag} data-l="ja" lang="ja">{ja}</{tag}><{tag} data-l="zh" lang="zh-Hant">{zh}</{tag}>'
            f'<{tag} data-l="en" lang="en">{en}</{tag}>')


def T(p, k):
    return L(E(p['ja'].get(k, '')), E(p['zh'].get(k, '')), E(p.get('en', p['ja']).get(k, '')))


def head(title_ja, title_zh, title_en, desc, path, og_img, story_id, color='#c8707e', noindex=False):
    canon = URL + path
    if noindex:  # 404：不給 Google 收錄，也不放 canonical／hreflang／OG
        seo = '<meta name="robots" content="noindex">'
    else:
        seo = f'''<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="ja" href="{canon}">
<link rel="alternate" hreflang="zh-Hant" href="{canon}?lang=zh">
<link rel="alternate" hreflang="en" href="{canon}?lang=en">
<link rel="alternate" hreflang="x-default" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="8月冬眠中">
<meta property="og:title" content="{E(title_ja)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{URL}{og_img}">
<meta property="og:locale" content="ja_JP">
<meta property="og:locale:alternate" content="zh_TW">
<meta property="og:locale:alternate" content="en_US">
<meta name="twitter:card" content="summary_large_image">'''
    return f'''<!doctype html>
<html lang="ja" data-lang="ja" data-mode="day">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<script>(function(){{var r=document.documentElement,l=new URLSearchParams(location.search).get('lang');try{{l=l||localStorage.getItem('hy-poem-lang')}}catch(e){{}}var M={{ja:'ja',zh:'zh-Hant',en:'en'}};if(!M[l])l='ja';r.setAttribute('data-lang',l);r.lang=M[l];window.HY_PAGE_LANG=M[l];var m='day';try{{m=localStorage.getItem('hy-poem-mode')==='night'?'night':'day'}}catch(e){{}}r.setAttribute('data-mode',m);}})();</script>
<title>{E(title_ja)}</title>
<meta name="title-ja" content="{E(title_ja)}">
<meta name="title-zh" content="{E(title_zh)}">
<meta name="title-en" content="{E(title_en)}">
<meta name="description" content="{E(desc)}">
{seo}
<meta name="theme-color" content="#f1ece1">
<style>:root{{--m:{color}}}</style>
<link rel="icon" href="/icons/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="96x96" href="/icons/favicon-96.png">
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/style.css?v={V}">
<!-- GA4 統一追蹤 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={SITE['ga4']}"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());
gtag('set',{{story_id:'{story_id}',page_lang:window.HY_PAGE_LANG,content_group:'poem'}});
gtag('config','{SITE['ga4']}',{{cookie_domain:'.knittinghiyori.com'}});
</script>
</head>
'''


LANG_SWITCH = ('<div class="tools"><div class="lang" role="group" aria-label="Language">'
               '<button type="button" data-set="ja" aria-pressed="true">日本語</button>'
               '<button type="button" data-set="zh" aria-pressed="false">中文</button>'
               '<button type="button" data-set="en" aria-pressed="false" lang="en">EN</button></div>'
               '<button class="mode" id="mode" type="button" aria-pressed="false" aria-label="Night mode">'
               '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg>'
               '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/></svg>'
               '</button></div>')


def share_bar(url, ja, zh, en, poem):
    h = (L('この詩をシェア', '分享這首詩', 'Share this poem') if poem
         else L('このページをシェア', '分享這個網站', 'Share this site'))
    nets = ''.join(f'<a data-net="{k}" href="#" target="_blank" rel="noopener">{n}</a>' for k, n in
                   [('x', 'X'), ('threads', 'Threads'), ('line', 'LINE'), ('facebook', 'Facebook'), ('bluesky', 'Bluesky')])
    return (f'<footer class="sharebar" id="sharebar" data-url="{url}" data-text-ja="{E(ja)}" data-text-zh="{E(zh)}" data-text-en="{E(en)}">'
            f'<h2>{h}</h2><div class="nets">{nets}'
            f'<button type="button" class="copy" id="copy">{L("リンクをコピー", "複製連結", "Copy link")}</button>'
            f'<button type="button" class="copy" id="native" hidden>{L("その他", "更多", "More")}</button></div>'
            f'<p class="copied" id="copied" aria-live="polite"></p></footer>')


def newsletter(poem):
    """頁面最下方的電子報訂閱 CTA。連結填在 poems.json 的 site.newsletter"""
    url = SITE.get('newsletter') or '#'
    if poem:
        h = L('この詩が届いたなら、次の詩も。', '如果這首詩留在你心裡，', 'If this one stayed with you,')
        s = L('新しい詩のハイライトを、<br>1〜2週間に一度メールでお届けします。',
              '讓下一首也寄到你那裡。<br>每一到兩週，把新詩精選寄給你。',
              'let the next one find you.<br>Highlights from the newest poems, every week or two.')
    else:
        h = L('詩の便りを受け取る', '收一封詩的來信', 'Poems, by letter')
        s = L('新しい詩のハイライトを、<br>1〜2週間に一度メールでお届けします。',
              '每一到兩週，把新上線的詩挑幾首寄給你。',
              'Every week or two, a few highlights from the newest poems, sent to your inbox.')
    return (f'<section class="nl" aria-labelledby="nl-h">'
            '<svg class="env" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5.5" width="18" height="13" rx="1.5"/>'
            '<path d="M3.5 6.5l8.5 6.5 8.5-6.5"/></svg>'
            f'<p class="k" aria-hidden="true">NEWSLETTER</p>'
            f'<h2 id="nl-h">{h}</h2><p class="s">{s}</p>'
            f'<a class="btn" href="{E(url)}" target="_blank" rel="noopener" data-cta="newsletter_{"poem" if poem else "home"}" '
            f'data-cta-type="newsletter">{L("購読する", "訂閱電子報", "Subscribe")}</a>'
            f'<p class="note">{L("日本語・中国語・英語でお届けします", "以中文、日文、英文寄送", "Sent in Chinese, Japanese and English")}</p>'
            '</section>')


def video(p):
    """詩頁的 YouTube 教學影片連結。poems.json 該首詩填了 youtube 才會出現"""
    url = p.get('youtube')
    if not url:
        return ''
    return (f'<p class="yt"><a href="{E(url)}" target="_blank" rel="noopener" data-cta="youtube_poem" data-cta-type="video">'
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5.5v13l11-6.5z"/></svg>'
            f'{L("YouTubeで日本語レッスンを見る", "在 YouTube 看這首詩的日文教學", "Watch the lesson on YouTube")}</a></p>\n')


def x_link():
    if not SITE.get('x_profile'):
        return ''
    return (f'<a class="x" href="{E(SITE["x_profile"])}" target="_blank" rel="noopener" '
            f'data-cta="x_profile" data-cta-type="social">{L("Xで読む", "在 X 上閱讀", "Read on X")}</a>')


def build_home():
    have = {p['id']: p for p in POEMS}
    done_months = {int(p['id'][:2]) for p in POEMS}
    months = []
    for m, n in enumerate(MONTH_DAYS, 1):
        c, ja, zh, en = MONTHS[m - 1]
        cells = []
        for d in range(1, n + 1):
            pid = f'{m:02d}{d:02d}'
            if pid in have:
                cells.append(f'<a class="day done" data-d="{pid}" href="/{pid}/" aria-label="{m}月{d}日 {E(have[pid]["ja"]["title"])}">{d}</a>')
            else:
                cells.append(f'<span class="day" data-d="{pid}" aria-hidden="true">{d}</span>')
        months.append(f'<div class="month" style="--c:{c}"><h3>{m}月<small>{L(ja, zh, en)}</small></h3>'
                      f'<div class="days">{"".join(cells)}</div></div>')
    on = ' class="on"'
    seasons = ''.join(f'<i style="--c:{c}"{on if i + 1 in done_months else ""}></i>'
                      for i, (c, *_) in enumerate(MONTHS))
    rows = []
    for p in POEMS:
        mm, dd = p['id'][:2], p['id'][2:]
        rows.append(f'<tr style="--c:{MONTHS[int(mm) - 1][0]}"><td class="no"><a href="/{p["id"]}/">{mm}.{dd}</a></td>'
                    f'<td><a href="/{p["id"]}/">{T(p, "title")}</a></td></tr>')
    rows += ['<tr><td></td><td></td></tr>'] * 3

    desc = '8月冬眠中の、一年ぶんの詩。一日ひとつ、365篇の短い詩を日本語・中国語・英語で。'
    out = head('8月冬眠中｜365日の詩', '8月冬眠中｜365 天的詩', '8月冬眠中 | 365 Days of Poems',
               desc, '/', '/og.png', 'poem-hub')
    out += f'''<body>
<div class="wrap">
<div class="bar"><span></span>{LANG_SWITCH}</div>
<main>
<header class="mast fade">
<p class="en">AUGUST HIBERNATION</p>
<h1>8月冬眠中</h1>
<p class="sub">{L("365日の詩", "365 天的詩", "365 Days of Poems")}</p>
<div class="seasons" aria-hidden="true">{seasons}</div>
<p class="count"><b>{len(POEMS)}</b>/ 365</p>
</header>
<div class="views" role="tablist">
<button type="button" role="tab" data-view="cal" aria-selected="true">{L("カレンダー", "年曆", "Calendar")}</button>
<button type="button" role="tab" data-view="list" aria-selected="false">{L("貸出カード", "借書卡", "Library card")}</button>
</div>
<section id="v-cal" class="cal">{"".join(months)}</section>
<section id="v-list" hidden><div class="card">
<h2>{L("貸出カード", "借書卡", "Library Card")}</h2>
<table><thead><tr><th>{L("日付", "日期", "Date")}</th><th>{L("題名", "篇名", "Title")}</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>
</div></section>
<footer class="about">
<p>{L("一日ひとつ、一年で365篇。<br>8月冬眠中の短い詩を、日本語・中国語・英語で。",
      "一天一首，一年 365 首。<br>8月冬眠中的短詩，以日文、中文與英文書寫。",
      "One a day, 365 in a year.<br>Short poems by 8月冬眠中, in Japanese, Chinese and English.")}</p>
{x_link()}
</footer>
</main>
{share_bar(URL + "/", "8月冬眠中｜365日の詩\n\n#8月冬眠中 #365日の詩", "8月冬眠中｜365 天的詩\n\n#8月冬眠中 #365天的詩",
           "8月冬眠中 | 365 Days of Poems\n\n#8月冬眠中 #365poems", False)}
{newsletter(False)}
</div>
<script src="/assets/app.js?v={V}"></script>
</body>
</html>
'''
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)


def stanzas(st):
    return ''.join('<p class="st">' + '<br>'.join(E(x) for x in s) + '</p>' for s in st)


def build_poem(i, p):
    pid = p['id']; mm, dd = pid[:2], pid[2:]
    ja, zh = p['ja'], p['zh']; en = p.get('en', ja)
    c, mja, mzh, men = MONTHS[int(mm) - 1]
    prev = POEMS[i - 1] if i > 0 else None
    nxt = POEMS[i + 1] if i + 1 < len(POEMS) else None
    pl = (f'<a href="/{prev["id"]}/" rel="prev">‹ {T(prev, "title")}</a>' if prev else '<span class="off" aria-hidden="true">‹</span>')
    nl = (f'<a href="/{nxt["id"]}/" rel="next">{T(nxt, "title")} ›</a>' if nxt else '<span class="off" aria-hidden="true">›</span>')
    desc = ja.get('lead') or ''.join(ja['stanzas'][0])
    out = head(f'「{ja["title"]}」｜8月冬眠中 {pid}', f'〈{zh["title"]}〉｜8月冬眠中 {pid}', f'“{en["title"]}” | 8月冬眠中 {pid}',
               desc, f'/{pid}/', f'/{pid}/og.png', f'poem-{pid}', c)
    out += f'''<body>
<div class="wrap">
<div class="bar"><a class="back" href="/">‹ {L("一覧", "目錄", "Index")}</a>{LANG_SWITCH}</div>
<main style="--c:{c}">
<article class="sheet fade">
<p class="en" aria-hidden="true">AUGUST HIBERNATION</p>
<div class="poem" data-l="ja" lang="ja"><h1>「{E(ja["title"])}」</h1>{stanzas(ja["stanzas"])}<p class="by">8月冬眠中</p></div>
<div class="poem" data-l="zh" lang="zh-Hant"><h1>〈{E(zh["title"])}〉</h1>{stanzas(zh["stanzas"])}<p class="by">8月冬眠中</p></div>
<div class="poem" data-l="en" lang="en"><h1>“{E(en["title"])}”</h1>{stanzas(en["stanzas"])}<p class="by">8月冬眠中</p></div>
<div class="corner" aria-label="{int(mm)}月{int(dd)}日"><span>{mm}</span><i></i><span>{dd}</span></div>
</article>
<p class="kigo">{L(mja + "の月", mzh + "之月", "the month of " + men)}</p>
<p class="lead">{T(p, "lead")}</p>
{video(p)}<nav class="pager">{pl}{nl}</nav>
</main>
{share_bar(f"{URL}/{pid}/", f"365日の詩　{pid}\n「{ja['title']}」\n\n#8月冬眠中 #365日の詩",
           f"365 天的詩　{pid}\n〈{zh['title']}〉\n\n#8月冬眠中 #365天的詩",
           f"365 Days of Poems　{pid}\n“{en['title']}”\n\n#8月冬眠中 #365poems", True)}
{newsletter(True)}
</div>
<script src="/assets/app.js?v={V}"></script>
</body>
</html>
'''
    os.makedirs(os.path.join(ROOT, pid), exist_ok=True)
    open(os.path.join(ROOT, pid, 'index.html'), 'w', encoding='utf-8').write(out)


def build_404():
    """找不到頁面時 GitHub Pages 會送出 /404.html。引導回目錄，並列出最近的 3 首詩"""
    c = MONTHS[11][0]  # 藍鼠：冬天的顏色，配「冬眠」
    rows = []
    for p in POEMS[::-1][:3]:
        mm, dd = p['id'][:2], p['id'][2:]
        rows.append(f'<tr style="--c:{MONTHS[int(mm) - 1][0]}"><td class="no"><a href="/{p["id"]}/" data-cta="notfound_poem" data-cta-type="other">{mm}.{dd}</a></td>'
                    f'<td><a href="/{p["id"]}/" data-cta="notfound_poem" data-cta-type="other">{T(p, "title")}</a></td></tr>')
    msg = {
        'ja': ('迷子', [['このページは', 'まだ書かれていないか', 'どこかで冬眠しているみたい'], ['目録に戻れば', 'ほかの詩が待っています']]),
        'zh': ('迷路', [['這一頁', '還沒有被寫下', '或是躲到哪裡冬眠了'], ['回到目錄', '還有別的詩在等你']]),
        'en': ('Lost', [['This page', "hasn't been written yet,", "or it's hibernating", 'somewhere.'], ['Back at the index,', 'other poems', 'are waiting for you.']]),
    }
    marks = {'ja': '「{}」', 'zh': '〈{}〉', 'en': '“{}”'}
    langs = {'ja': 'ja', 'zh': 'zh-Hant', 'en': 'en'}
    poems = ''.join(f'<div class="poem" data-l="{k}" lang="{langs[k]}"><h1>{marks[k].format(E(t))}</h1>{stanzas(st)}</div>'
                    for k, (t, st) in msg.items())
    out = head('ページが見つかりません｜8月冬眠中', '找不到這一頁｜8月冬眠中', 'Page not found | 8月冬眠中',
               'お探しのページは見つかりませんでした。', '/404.html', '/og.png', 'poem-404', c, noindex=True)
    out += f'''<body>
<div class="wrap">
<div class="bar"><a class="back" href="/">‹ {L("一覧", "目錄", "Index")}</a>{LANG_SWITCH}</div>
<main style="--c:{c}">
<article class="sheet fade">
<p class="en" aria-hidden="true">AUGUST HIBERNATION</p>
{poems}
<div class="corner" aria-label="404"><span>4</span><i></i><span>04</span></div>
</article>
<p class="lead" id="nf-day" hidden>{L("この日の詩は、まだ冬眠中です。", "這一天的詩，還在冬眠中。", "The poem for this day is still hibernating.")}</p>
<p class="nf-home"><a class="btn" href="/" data-cta="notfound_home" data-cta-type="other">{L("目録へ戻る", "回到目錄", "Back to all poems")}</a></p>
<section class="card nf-recent">
<h2>{L("最近の詩", "最近的詩", "Recent Poems")}</h2>
<table><tbody>{"".join(rows)}</tbody></table>
</section>
</main>
</div>
<script src="/assets/app.js?v={V}"></script>
</body>
</html>
'''
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(out)


def build_og():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print('（未安裝 Pillow，略過預覽圖）'); return
    fdir = os.path.join(ROOT, 'fonts')
    klee = os.path.join(fdir, 'KleeOne-SemiBold.ttf'); latin = os.path.join(fdir, 'ShipporiMincho-Medium.ttf')
    if not os.path.exists(klee):
        print('（fonts/ 資料夾沒有字型檔，略過預覽圖）'); return
    ink, pencil, paper = (56, 50, 44), (140, 131, 120), (241, 236, 225)

    def card(lines, sub, out):
        W, H = 1200, 630
        im = Image.new('RGB', (W, H), paper); d = ImageDraw.Draw(im)
        d.text((W / 2, 70), 'A U G U S T   H I B E R N A T I O N', font=ImageFont.truetype(latin, 20), fill=pencil, anchor='mt')
        big = ImageFont.truetype(klee, 44)
        y = H / 2 - (len(lines) * 74) / 2 + 10
        for ln in lines:
            d.text((W / 2, y), ln, font=big, fill=ink, anchor='mt'); y += 74
        d.text((W / 2, H - 80), sub, font=ImageFont.truetype(klee, 24), fill=pencil, anchor='mt')
        im.save(out, optimize=True)

    card(['8月冬眠中', '365日の詩'], f'{len(POEMS)} / 365', os.path.join(ROOT, 'og.png'))
    for p in POEMS:
        first = p['ja']['stanzas'][0][:2]
        card([f'「{p["ja"]["title"]}」'] + first, f'8月冬眠中　{p["id"]}', os.path.join(ROOT, p['id'], 'og.png'))


def build_sitemap():
    urls = ['/'] + [f'/{p["id"]}/' for p in POEMS]
    items = ''.join(
        f'<url><loc>{URL}{u}</loc>'
        f'<xhtml:link rel="alternate" hreflang="ja" href="{URL}{u}"/>'
        f'<xhtml:link rel="alternate" hreflang="zh-Hant" href="{URL}{u}?lang=zh"/>'
        f'<xhtml:link rel="alternate" hreflang="en" href="{URL}{u}?lang=en"/></url>' for u in urls)
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        f'xmlns:xhtml="http://www.w3.org/1999/xhtml">{items}</urlset>\n')


if __name__ == '__main__':
    build_home()
    for i, p in enumerate(POEMS):
        build_poem(i, p)
    build_404()
    build_og()
    build_sitemap()
    print(f'完成：{len(POEMS)} 首詩')
    if not SITE.get('newsletter'):
        print('⚠ poems.json 的 site.newsletter 還沒填訂閱連結，按鈕目前連到 #')
