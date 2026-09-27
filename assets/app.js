(function () {
  var root = document.documentElement, $ = function (s) { return document.querySelector(s); };
  var LANGS = { ja: 'ja', zh: 'zh-Hant', en: 'en' };
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function ev(n, p) { if (window.gtag) gtag('event', n, p || {}); }

  /* language */
  function setLang(l, user) {
    if (!LANGS[l]) l = 'ja';
    root.dataset.lang = l; root.lang = LANGS[l];
    document.querySelectorAll('.lang button').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.set === l); });
    var t = document.querySelector('meta[name="title-' + l + '"]'); if (t) document.title = t.content;
    if (window.gtag) gtag('set', { page_lang: LANGS[l] });
    if (user) { store('hy-poem-lang', l); ev('interaction', { interaction_type: 'toggle', interaction_id: 'lang_' + l }); }
  }
  setLang(root.dataset.lang);
  document.querySelectorAll('.lang button').forEach(function (b) { b.onclick = function () { setLang(b.dataset.set, true); }; });

  /* night mode (default: day) */
  var mode = $('#mode');
  function setMode(m, user) {
    root.dataset.mode = m; if (mode) mode.setAttribute('aria-pressed', m === 'night');
    if (user) { store('hy-poem-mode', m); ev('interaction', { interaction_type: 'toggle', interaction_id: 'mode_' + m }); }
  }
  if (mode) mode.onclick = function () { setMode(root.dataset.mode === 'night' ? 'day' : 'night', true); };

  /* home: calendar / list */
  var tabs = document.querySelectorAll('.views button');
  function view(v, user) {
    tabs.forEach(function (b) { b.setAttribute('aria-selected', b.dataset.view === v); });
    $('#v-cal').hidden = v !== 'cal'; $('#v-list').hidden = v !== 'list';
    if (user) { store('hy-poem-view', v); ev('interaction', { interaction_type: 'filter', interaction_id: 'view_' + v }); }
  }
  if (tabs.length) {
    view(store('hy-poem-view') === 'list' ? 'list' : 'cal');
    tabs.forEach(function (b) { b.onclick = function () { view(b.dataset.view, true); }; });
    var d = new Date(), today = ('0' + (d.getMonth() + 1)).slice(-2) + ('0' + d.getDate()).slice(-2);
    var c = document.querySelector('[data-d="' + today + '"]'); if (c) { c.classList.add('today'); c.setAttribute('aria-current', 'date'); }
  }

  /* poem: swipe + arrow keys */
  var prev = $('.pager a[rel="prev"]'), next = $('.pager a[rel="next"]');
  function go(a, how) { if (!a) return; ev('interaction', { interaction_type: 'explore', interaction_id: a.rel + '_' + how }); location.href = a.href; }
  if (prev || next) {
    var sx = 0, sy = 0;
    document.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; sy = e.touches[0].clientY; }, { passive: true });
    document.addEventListener('touchend', function (e) {
      var dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) go(dx > 0 ? prev : next, 'swipe');
    }, { passive: true });
    document.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') go(prev, 'key'); if (e.key === 'ArrowRight') go(next, 'key'); });
  }

  /* share bar */
  var bar = $('#sharebar');
  function info() {
    var l = root.dataset.lang;
    return { url: bar.dataset.url + (l === 'ja' ? '' : '?lang=' + l), text: bar.dataset['text' + l.charAt(0).toUpperCase() + l.slice(1)] };
  }
  if (bar) {
    document.querySelectorAll('[data-net]').forEach(function (a) {
      a.addEventListener('click', function () {
        var s = info(), u = encodeURIComponent(s.url), t = encodeURIComponent(s.text), both = encodeURIComponent(s.text + '\n' + s.url);
        a.href = { x: 'https://x.com/intent/post?text=' + t + '&url=' + u,
          threads: 'https://www.threads.net/intent/post?text=' + both,
          line: 'https://social-plugins.line.me/lineit/share?url=' + u,
          facebook: 'https://www.facebook.com/sharer/sharer.php?u=' + u,
          bluesky: 'https://bsky.app/intent/compose?text=' + both }[a.dataset.net];
        ev('cta_click', { cta_id: 'share_' + a.dataset.net, cta_type: 'share', link_url: s.url });
      });
    });
    var msg = { ja: 'リンクをコピーしました', zh: '已複製連結', en: 'Link copied' };
    $('#copy').onclick = function () {
      var u = info().url;
      var ok = function () { $('#copied').textContent = msg[root.dataset.lang]; setTimeout(function () { $('#copied').textContent = ''; }, 2200); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(ok, function () { prompt('URL', u); });
      else prompt('URL', u);
      ev('cta_click', { cta_id: 'share_copy', cta_type: 'share', link_url: u });
    };
    if (navigator.share) {
      $('#native').hidden = false;
      $('#native').onclick = function () {
        var s = info(); ev('cta_click', { cta_id: 'share_native', cta_type: 'share', link_url: s.url });
        navigator.share({ title: document.title, text: s.text, url: s.url }).catch(function () {});
      };
    }
  }

  document.querySelectorAll('[data-cta]').forEach(function (a) {
    a.addEventListener('click', function () { ev('cta_click', { cta_id: a.dataset.cta, cta_type: a.dataset.ctaType || 'social', link_url: a.href }); });
  });
})();
