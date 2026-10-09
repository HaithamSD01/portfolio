/* Portfolio Haitham Dhaimi : petit script, sans dépendance.
   Tout ce qui est ici est un plus : le site reste lisible sans JavaScript. */
(function () {
  'use strict';

  var root = document.documentElement;

  function store(key, value) {
    try {
      if (value === null) localStorage.removeItem(key);
      else localStorage.setItem(key, value);
    } catch (e) { /* navigation privée : on ignore */ }
  }
  function read(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  /* ---------- Thème : auto / clair / sombre ---------- */
  var themeButtons = document.querySelectorAll('[data-theme-choice]');
  var darkQuery = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function syncThemeColor() {
    var dark = root.getAttribute('data-theme') === 'dark' ||
      (!root.hasAttribute('data-theme') && darkQuery && darkQuery.matches);
    var metas = document.querySelectorAll('meta[name="theme-color"]');
    for (var i = 0; i < metas.length; i++) {
      metas[i].setAttribute('content', dark ? '#0B121F' : '#F5F0E4');
    }
  }

  function applyTheme(choice) {
    if (choice === 'light' || choice === 'dark') {
      root.setAttribute('data-theme', choice);
      store('hd-theme', choice);
    } else {
      choice = 'auto';
      root.removeAttribute('data-theme');
      store('hd-theme', null);
    }
    for (var i = 0; i < themeButtons.length; i++) {
      var b = themeButtons[i];
      b.setAttribute('aria-pressed', b.getAttribute('data-theme-choice') === choice ? 'true' : 'false');
    }
    syncThemeColor();
  }

  var saved = read('hd-theme');
  applyTheme(saved === 'light' || saved === 'dark' ? saved : 'auto');
  for (var t = 0; t < themeButtons.length; t++) {
    themeButtons[t].addEventListener('click', function () {
      applyTheme(this.getAttribute('data-theme-choice'));
    });
  }
  if (darkQuery && darkQuery.addEventListener) darkQuery.addEventListener('change', syncThemeColor);

  /* ---------- Menu mobile ---------- */
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.getElementById('site-menu');

  function setMenu(open) {
    if (!toggle || !menu) return;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    var label = toggle.getAttribute(open ? 'data-close' : 'data-open');
    var sr = toggle.querySelector('.sr-only');
    if (sr && label) sr.textContent = label;
    menu.classList.toggle('open', open);
  }

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
    menu.addEventListener('click', function (e) {
      if (e.target.closest && e.target.closest('a')) setMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        toggle.focus();
      }
    });
    document.addEventListener('click', function (e) {
      if (toggle.getAttribute('aria-expanded') === 'true' &&
          !menu.contains(e.target) && !toggle.contains(e.target)) setMenu(false);
    });
  }

  /* ---------- Langue : on retient le choix, on suggère sans rediriger ---------- */
  var langLinks = document.querySelectorAll('[data-lang]');
  for (var l = 0; l < langLinks.length; l++) {
    langLinks[l].addEventListener('click', function () {
      store('hd-lang', this.getAttribute('data-lang'));
    });
  }

  var suggest = document.querySelector('[data-suggest]');
  if (suggest) {
    var target = suggest.getAttribute('data-suggest');
    var browser = (navigator.languages && navigator.languages[0]) || navigator.language || '';
    browser = browser.slice(0, 2).toLowerCase();
    var already = read('hd-lang') || read('hd-suggest-dismissed');
    if (browser === target && !already) suggest.hidden = false;
    var close = suggest.querySelector('.lang-suggest-close');
    if (close) {
      close.addEventListener('click', function () {
        suggest.hidden = true;
        store('hd-suggest-dismissed', '1');
      });
    }
  }

  /* ---------- Copier l'adresse e-mail ---------- */
  var copyBtn = document.querySelector('.copy-btn');
  var status = document.querySelector('.copy-status');
  if (copyBtn && navigator.clipboard && window.isSecureContext) {
    copyBtn.hidden = false;
    copyBtn.addEventListener('click', function () {
      var ok = copyBtn.getAttribute('data-ok');
      var fail = copyBtn.getAttribute('data-fail');
      navigator.clipboard.writeText(copyBtn.getAttribute('data-copy')).then(function () {
        if (status) status.textContent = ok;
      }, function () {
        if (status) status.textContent = fail;
      });
      setTimeout(function () { if (status) status.textContent = ''; }, 4000);
    });
  }

  /* ---------- Section visible dans la navigation ---------- */
  var navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
  if ('IntersectionObserver' in window && navLinks.length) {
    var byId = {};
    var sections = [];
    for (var n = 0; n < navLinks.length; n++) {
      var id = navLinks[n].getAttribute('href').slice(1);
      var s = document.getElementById(id);
      if (s) { byId[id] = navLinks[n]; sections.push(s); }
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        for (var k in byId) byId[k].removeAttribute('aria-current');
        var link = byId[entry.target.id];
        if (link) link.setAttribute('aria-current', 'true');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (s) { observer.observe(s); });
  }
})();
