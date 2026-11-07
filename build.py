"""8月冬眠中｜poem.knittinghiyori.com 產生器
用法：編輯 poems.json 後執行  python3 build.py
會產生 index.html、每首詩的資料夾（例如 0101/index.html）、404.html、分享預覽圖、sitemap.xml、llms.txt
"""
import json, os, html, hashlib

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
# css/js 的版本號：依檔案內容產生，檔案一改就換號（同一天改兩次也會換），瀏覽器才會抓新版
V = hashlib.md5(b''.join(open(os.path.join(ROOT, 'assets', f), 'rb').read() for f in ('style.css', 'app.js'))).hexdigest()[:8]

# 變現與規範（knittinghiyori-specs core §1、§2、§4、§6；poem.md）
DRIVE = 'https://emrld.ltd/NTc4NjIw.js?t=578620'  # Travelpayouts Drive，poem 專用
AD_CLIENT = 'ca-pub-2022028565680247'  # AdSense 發布商 ID
# 首頁與詩頁共用同一個廣告單元（Zoe 2026-10-09：收益合在一起看；哪一頁人多看 GA4）
AD_SLOT_HOME = '6629751780'  # poem-目錄下方
AD_SLOT_POEM = AD_SLOT_HOME
SPEC = 'core-v1.9/poem-v0.7'
# 三語各有自己的網址（poem v0.7）：日文在根目錄（原本的網址），中文 /zh/、英文 /en/
PREFIX = {'ja': '', 'zh': '/zh', 'en': '/en'}
LANG_TAG = {'ja': 'ja', 'zh': 'zh-Hant', 'en': 'en'}
OG_LOCALE = {'ja': 'ja_JP', 'zh': 'zh_TW', 'en': 'en_US'}
PRIVACY = 'https://knittinghiyori.com/privacy-policy/'

FONTS = ('https://fonts.googleapis.com/css2?family=Iansui&family=Klee+One:wght@400;600'
         '&family=Shippori+Mincho:wght@500&display=swap')


def L(ja, zh, en=None, tag='span'):
    en = ja if en is None else en
    return (f'<{tag} data-l="ja" lang="ja">{ja}</{tag}><{tag} data-l="zh" lang="zh-Hant">{zh}</{tag}>'
            f'<{tag} data-l="en" lang="en">{en}</{tag}>')


def T(p, k):
    return L(E(p['ja'].get(k, '')), E(p['zh'].get(k, '')), E(p.get('en', p['ja']).get(k, '')))


def head(title_ja, title_zh, title_en, desc, path, og_img, story_id, color='#c8707e', noindex=False, ads=False, page_title=None, lang='ja'):
    """path 是不含語言前綴的路徑（例：/0101/）；lang 決定這一頁的網址、<html lang>、title 與 description"""
    titles = {'ja': title_ja, 'zh': title_zh, 'en': title_en}
    desc = desc[lang] if isinstance(desc, dict) else desc
    canon = URL + PREFIX[lang] + path
    if noindex:  # 404：不給 Google 收錄，也不放 canonical／hreflang／OG
        seo = '<meta name="robots" content="noindex, follow">'
    else:
        alts = ''.join(f'<link rel="alternate" hreflang="{LANG_TAG[k]}" href="{URL}{PREFIX[k]}{path}">\n' for k in PREFIX)
        locs = ''.join(f'<meta property="og:locale:alternate" content="{OG_LOCALE[k]}">\n' for k in PREFIX if k != lang)
        seo = f'''<link rel="canonical" href="{canon}">
{alts}<link rel="alternate" hreflang="x-default" href="{URL}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="8月冬眠中">
<meta property="og:title" content="{E(titles[lang])}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{URL}{og_img}">
<meta property="og:locale" content="{OG_LOCALE[lang]}">
{locs}<meta name="twitter:card" content="summary_large_image">'''
    return f'''<!doctype html>
<html lang="{LANG_TAG[lang]}" data-lang="{lang}" data-mode="day">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- Travelpayouts Drive（head 第一個 script） -->
<script data-cfasync="false">(function(){{var s=document.createElement("script");s.async=1;s.src="{DRIVE}";document.head.appendChild(s);}})();</script>
<script>(function(){{var r=document.documentElement,p=location.pathname,M={{ja:'ja',zh:'zh-Hant',en:'en'}},l=/^\\/zh(\\/|$)/.test(p)?'zh':/^\\/en(\\/|$)/.test(p)?'en':'ja',q=new URLSearchParams(location.search).get('lang');if(l==='ja'&&(q==='zh'||q==='en')){{location.replace('/'+q+p+location.hash);return}}r.setAttribute('data-lang',l);r.lang=M[l];window.HY_PAGE_LANG=M[l];var m='day';try{{m=localStorage.getItem('hy-poem-mode')==='night'?'night':'day'}}catch(e){{}}r.setAttribute('data-mode',m);}})();</script>
<title>{E(titles[lang])}</title>
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
{ADSENSE if ads else ''}<!-- GA4 統一追蹤 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={SITE['ga4']}"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());
gtag('set',{{story_id:'{story_id}',page_lang:window.HY_PAGE_LANG,content_group:'poem'{f",page_title:'{page_title}'" if page_title else ''}}});
gtag('config','{SITE['ga4']}',{{cookie_domain:'.knittinghiyori.com'}});
</script>
<meta name="spec-version" content="{SPEC}">
</head>
'''


# 不開自動廣告：載入碼不帶 ?client=
ADSENSE = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" crossorigin="anonymous"></script>\n'


def ad_unit(slot):
    """AdSense 版位：首頁在借書卡之後、about 之前；詩頁在電子報之後、頁尾說明之前。404 不放（AdSense 政策）"""
    return (f'<div class="kh-ad"><p class="kh-ad__label">{L("広告", "廣告", "Advertisement")}</p>'
            f'<ins class="adsbygoogle" style="display:block" data-ad-client="{AD_CLIENT}" data-ad-slot="{slot}" '
            'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div>')


def legal():
    """每頁頁尾的 Cookie 說明（core §6）"""
    return (f'<p class="kh-legal">'
            f'{L("当サイトはアクセス解析（Google Analytics）と広告配信（Google AdSense）のためにCookieを使用し、一部にアフィリエイトリンクを含みます。",
                 "本站使用 Cookie 進行流量分析（Google Analytics）與顯示廣告（Google AdSense），部分連結為聯盟連結。",
                 "This site uses cookies for analytics (Google Analytics) and ads (Google AdSense), and some links are affiliate links. ")}'
            f'<a href="{PRIVACY}">{L("プライバシーポリシー", "隱私權政策", "Privacy")}</a></p>')


def write(path, out):
    """寫出頁面；所有連結加 data-google-vignette="false"（不開自動廣告，core §4）"""
    out = out.replace('<a ', '<a data-google-vignette="false" ')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(out)


# 頁首品牌列（core §7）：正式 logo＋「編織日和・詩」，點了回詩網站首頁。窄螢幕先藏「・詩」
BRAND = ('<a class="kh-brand" href="https://poem.knittinghiyori.com/" data-cta="brand_hub" data-cta-type="poem">'
         '<img src="/icons/logo-knitting-120.webp" srcset="/icons/logo-knitting-120.webp 1x, /icons/logo-knitting-240.webp 2x" '
         'width="40" height="40" alt="">編織日和'
         f'<span class="kh-brand-sub">{L("・詩", "・詩", " · Poems")}</span></a>')
def back(lang='ja'):
    return f'<nav class="crumb"><a class="back" href="{PREFIX[lang]}/">‹ {L("一覧", "目錄", "Index")}</a></nav>'


def lang_switch(path=None, lang='ja'):
    """語言切換：按了立刻換字，網址也換成該語言的網址（data-href）。path=None（404）只換字"""
    def btn(k, label, extra=''):
        href = f' data-href="{PREFIX[k]}{path}"' if path else ''
        return f'<button type="button" data-set="{k}"{href} aria-pressed="{str(k == lang).lower()}"{extra}>{label}</button>'
    return ('<div class="tools"><div class="lang" role="group" aria-label="Language">'
            + btn('ja', '日本語') + btn('zh', '中文') + btn('en', 'EN', ' lang="en"') + '</div>'
            + MODE_BTN)


MODE_BTN = ('<button class="mode" id="mode" type="button" aria-pressed="false" aria-label="Night mode">'
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


def build_home(lang='ja'):
    P = PREFIX[lang]
    have = {p['id']: p for p in POEMS}
    done_months = {int(p['id'][:2]) for p in POEMS}
    months = []
    for m, n in enumerate(MONTH_DAYS, 1):
        c, ja, zh, en = MONTHS[m - 1]
        cells = []
        for d in range(1, n + 1):
            pid = f'{m:02d}{d:02d}'
            if pid in have:
                cells.append(f'<a class="day done" data-d="{pid}" href="{P}/{pid}/" aria-label="{m}月{d}日 {E(have[pid]["ja"]["title"])}">{d}</a>')
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
        rows.append(f'<tr style="--c:{MONTHS[int(mm) - 1][0]}"><td class="no"><a href="{P}/{p["id"]}/">{mm}.{dd}</a></td>'
                    f'<td><a href="{P}/{p["id"]}/">{T(p, "title")}</a></td></tr>')
    rows += ['<tr><td></td><td></td></tr>'] * 3

    desc = {'ja': '8月冬眠中の、一年ぶんの詩。一日ひとつ、365篇の短い詩を日本語・中国語・英語で。',
            'zh': '8月冬眠中的一年份的詩。一天一首，365 首短詩，以日文、中文與英文書寫。',
            'en': 'A year of poems by 8月冬眠中: one short poem a day, 365 in all, in Japanese, Chinese and English.'}
    out = head('8月冬眠中｜365日の詩', '8月冬眠中｜365 天的詩', '8月冬眠中 | 365 Days of Poems',
               desc, '/', '/og.png', 'poem-hub', ads=True, lang=lang)
    out += f'''<body>
<div class="wrap">
<div class="bar kh-brand-row">{BRAND}{lang_switch('/', lang)}</div>
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
{ad_unit(AD_SLOT_HOME)}
<footer class="about">
<p>{L("一日ひとつ、一年で365篇。<br>8月冬眠中の短い詩を、日本語・中国語・英語で。",
      "一天一首，一年 365 首。<br>8月冬眠中的短詩，以日文、中文與英文書寫。",
      "One a day, 365 in a year.<br>Short poems by 8月冬眠中, in Japanese, Chinese and English.")}</p>
{x_link()}
</footer>
</main>
{share_bar(URL + P + "/", "8月冬眠中｜365日の詩\n\n#8月冬眠中 #365日の詩", "8月冬眠中｜365 天的詩\n\n#8月冬眠中 #365天的詩",
           "8月冬眠中 | 365 Days of Poems\n\n#8月冬眠中 #365poems", False)}
{newsletter(False)}
{legal()}
</div>
<script src="/assets/app.js?v={V}"></script>
</body>
</html>
'''
    write(os.path.join(ROOT, P.strip('/'), 'index.html'), out)


def stanzas(st):
    return ''.join('<p class="st">' + '<br>'.join(E(x) for x in s) + '</p>' for s in st)


def build_poem(i, p, lang='ja'):
    P = PREFIX[lang]
    pid = p['id']; mm, dd = pid[:2], pid[2:]
    ja, zh = p['ja'], p['zh']; en = p.get('en', ja)
    c, mja, mzh, men = MONTHS[int(mm) - 1]
    prev = POEMS[i - 1] if i > 0 else None
    nxt = POEMS[i + 1] if i + 1 < len(POEMS) else None
    pl = (f'<a href="{P}/{prev["id"]}/" rel="prev">‹ {T(prev, "title")}</a>' if prev else '<span class="off" aria-hidden="true">‹</span>')
    nl = (f'<a href="{P}/{nxt["id"]}/" rel="next">{T(nxt, "title")} ›</a>' if nxt else '<span class="off" aria-hidden="true">›</span>')
    desc = {k: v.get('lead') or ''.join(v['stanzas'][0]) for k, v in (('ja', ja), ('zh', zh), ('en', en))}
    out = head(f'「{ja["title"]}」｜8月冬眠中 {pid}', f'〈{zh["title"]}〉｜8月冬眠中 {pid}', f'“{en["title"]}” | 8月冬眠中 {pid}',
               desc, f'/{pid}/', f'/{pid}/og.png', f'poem-{pid}', c, ads=True, lang=lang)
    out += f'''<body>
<div class="wrap">
<div class="bar kh-brand-row">{BRAND}{lang_switch(f'/{pid}/', lang)}</div>
{back(lang)}
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
{share_bar(f"{URL}{P}/{pid}/", f"365日の詩　{pid}\n「{ja['title']}」\n\n#8月冬眠中 #365日の詩",
           f"365 天的詩　{pid}\n〈{zh['title']}〉\n\n#8月冬眠中 #365天的詩",
           f"365 Days of Poems　{pid}\n“{en['title']}”\n\n#8月冬眠中 #365poems", True)}
{newsletter(True)}
{ad_unit(AD_SLOT_POEM)}
{legal()}
</div>
<script src="/assets/app.js?v={V}"></script>
</body>
</html>
'''
    write(os.path.join(ROOT, P.strip('/'), pid, 'index.html'), out)


# 404 跨站連結一行（core §7 v1.5）：到編織日和其他子網域，不含自己；cta_type 填目的地類型
NF_SITES = ('<nav class="nf-sites" aria-label="編織日和"><span>' + L('ほかのサイト：', '也可以逛逛：', 'More from Knitting Hiyori:') + '</span>'
            + ''.join(f'<a href="https://{host}.knittinghiyori.com/" data-cta="notfound_site" data-cta-type="{t}">{L(ja, zh, en)}</a>'
                      for host, t, ja, zh, en in [('story', 'story', '物語', '故事', 'Stories'), ('games', 'game', 'ミニゲーム', '小遊戲', 'Games'),
                                                  ('tools', 'tool', 'ツール', '小工具', 'Tools'), ('study', 'study', '学習ノート', '學習筆記', 'Study notes')])
            + '</nav>')


def build_404():
    """找不到頁面時 GitHub Pages 會送出 /404.html。引導回目錄、主站，並列出最近的 3 首詩（core §7：notfound_hub／notfound_main／notfound_card）"""
    c = MONTHS[11][0]  # 藍鼠：冬天的顏色，配「冬眠」
    rows = []
    for p in POEMS[::-1][:3]:
        mm, dd = p['id'][:2], p['id'][2:]
        rows.append(f'<tr style="--c:{MONTHS[int(mm) - 1][0]}"><td class="no"><a href="/{p["id"]}/" data-cta="notfound_card" data-cta-type="poem">{mm}.{dd}</a></td>'
                    f'<td><a href="/{p["id"]}/" data-cta="notfound_card" data-cta-type="poem">{T(p, "title")}</a></td></tr>')
    msg = {
        'ja': ('行き止まり', [['このページは', 'まだ書かれていないか', 'どこかで冬眠しているみたい'], ['目録に戻れば', 'ほかの詩が待っています']]),
        'zh': ('此路不通', [['這一頁', '還沒有被寫下', '或是躲到哪裡冬眠了'], ['回到目錄', '還有別的詩在等你']]),
        'en': ('Dead End', [['This page', "hasn't been written yet,", "or it's hibernating", 'somewhere.'], ['Back at the index,', 'other poems', 'are waiting for you.']]),
    }
    marks = {'ja': '「{}」', 'zh': '〈{}〉', 'en': '“{}”'}
    langs = {'ja': 'ja', 'zh': 'zh-Hant', 'en': 'en'}
    poems = ''.join(f'<div class="poem" data-l="{k}" lang="{langs[k]}"><h1>{marks[k].format(E(t))}</h1>{stanzas(st)}</div>'
                    for k, (t, st) in msg.items())
    out = head('ページが見つかりません｜8月冬眠中', '找不到這一頁｜8月冬眠中', 'Page not found | 8月冬眠中',
               'お探しのページは見つかりませんでした。', '/404.html', '/og.png', 'poem-404', c, noindex=True,
               page_title='詩|404|找不到頁面')
    out += f'''<body>
<div class="wrap">
<div class="bar kh-brand-row">{BRAND}{lang_switch()}</div>
{back()}
<main style="--c:{c}">
<article class="sheet fade">
<p class="en" aria-hidden="true">AUGUST HIBERNATION</p>
{poems}
<div class="corner" aria-label="404"><span>4</span><i></i><span>04</span></div>
</article>
<p class="lead" id="nf-day" hidden>{L("この日の詩は、まだ冬眠中です。", "這一天的詩，還在冬眠中。", "The poem for this day is still hibernating.")}</p>
<p class="nf-home"><a class="btn" href="/" data-cta="notfound_hub" data-cta-type="poem">{L("目録へ戻る", "回到目錄", "Back to all poems")}</a></p>
<p class="nf-main"><a href="https://knittinghiyori.com/" data-cta="notfound_main" data-cta-type="poem">{L("編織日和のサイトへ →", "到編織日和主站 →", "Visit Knitting Hiyori →")}</a></p>
<section class="card nf-recent">
<h2>{L("最近の詩", "最近的詩", "Recent Poems")}</h2>
<table><tbody>{"".join(rows)}</tbody></table>
</section>
{NF_SITES}
</main>
{legal()}
</div>
<script src="/assets/app.js?v={V}"></script>
</body>
</html>
'''
    write(os.path.join(ROOT, '404.html'), out)


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
    alts = lambda u: ''.join(f'<xhtml:link rel="alternate" hreflang="{LANG_TAG[k]}" href="{URL}{PREFIX[k]}{u}"/>' for k in PREFIX) \
        + f'<xhtml:link rel="alternate" hreflang="x-default" href="{URL}{u}"/>'
    items = ''.join(f'<url><loc>{URL}{PREFIX[k]}{u}</loc>{alts(u)}</url>' for u in urls for k in PREFIX)
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        f'xmlns:xhtml="http://www.w3.org/1999/xhtml">{items}</urlset>\n')


def build_llms():
    """llms.txt：給 AI 搜尋與助理讀的網站摘要（GEO），每次 build 依 poems.json 自動列出全部的詩"""
    lines = ['# 8月冬眠中｜365日の詩 poem.knittinghiyori.com', '',
             '> 8月冬眠中の、一年ぶんの詩。一日ひとつ、365篇の短い詩を日本語・中国語・英語で。'
             '編織日和（knittinghiyori.com）的詩系列，目標 365 首短詩，每首都有日文、繁體中文、英文三語對照。', '',
             '- 語言：日文為主，每首附繁體中文與英文',
             '- 筆名：8月冬眠中',
             f'- 詩的網址是四位數的日期編號，例如 0101 代表 1 月 1 日：{URL}/0101/',
             f'- 三語各有網址：日文 {URL}/0101/、繁體中文 {URL}/zh/0101/、英文 {URL}/en/0101/',
             '- 詩是原創作品，引用時請標示「8月冬眠中」並附上該首詩的網址，不要整首轉載', '',
             '## 入口', '', f'- [全部的詩]({URL}/): 依編號排列的詩目錄', '',
             f'## 已發表的詩（{len(POEMS)} 首）', '']
    lines += [f'- [{p["id"]}「{p["ja"]["title"]}」]({URL}/{p["id"]}/): {p["zh"]["title"]} / {p["en"]["title"]}' for p in POEMS]
    lines += ['', '## 相關網站', '', '- [編織日和](https://knittinghiyori.com/): 主站部落格',
              '- [如何追蹤編織日和](https://knittinghiyori.com/follow/): RSS 與給 AI 的追蹤指令', '']
    open(os.path.join(ROOT, 'llms.txt'), 'w', encoding='utf-8').write('\n'.join(lines))

if __name__ == '__main__':
    for lang in PREFIX:
        build_home(lang)
        for i, p in enumerate(POEMS):
            build_poem(i, p, lang)
    build_404()
    build_og()
    build_sitemap()
    build_llms()
    print(f'完成：{len(POEMS)} 首詩')
    if not SITE.get('newsletter'):
        print('⚠ poems.json 的 site.newsletter 還沒填訂閱連結，按鈕目前連到 #')
