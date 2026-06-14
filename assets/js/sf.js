/* ════════════════════════════════════════════════
   SF Finance — Shared JS v3.0 · Premium-Playful
   Nav · Mobile · Video · GSAP/ScrollTrigger motion stack
   Degrades gracefully: no GSAP → IO fallback,
   reduced-motion → static, JS error → safety reveal.
   ════════════════════════════════════════════════ */

(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer  = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var hasGSAP      = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';

  /* ──────────────────────────────────────────────
     NAV — scroll border + mobile toggle
  ────────────────────────────────────────────── */
  var nav        = document.getElementById('sfNav');
  var navToggle  = document.getElementById('navToggle');
  var navMobile  = document.getElementById('navMobile');

  if (nav) {
    window.addEventListener('scroll', function () {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });
  }

  if (navToggle && navMobile) {
    navToggle.addEventListener('click', function () {
      var open = navToggle.classList.toggle('open');
      navMobile.classList.toggle('open', open);
      navToggle.setAttribute('aria-expanded', open);
    });
    navMobile.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        navToggle.classList.remove('open');
        navMobile.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ──────────────────────────────────────────────
     VIDEO TILE — coming-soon overlay
  ────────────────────────────────────────────── */
  document.querySelectorAll('.video-tile[data-coming-soon]').forEach(function (tile) {
    tile.addEventListener('click', function () {
      if (tile.querySelector('.coming-overlay')) return;
      var overlay = document.createElement('div');
      overlay.className = 'coming-overlay';
      overlay.setAttribute('style',
        'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;' +
        'background:rgba(6,12,26,.78);backdrop-filter:blur(3px);font-family:var(--f-mono);' +
        'font-size:.68rem;letter-spacing:.08em;color:#f0c040;text-transform:uppercase;z-index:10;' +
        'text-align:center;padding:1rem;animation:sfFadeIn .35s ease;');
      overlay.textContent = 'Kanal startet bald — folg uns!';
      tile.appendChild(overlay);
    });
  });

  /* ──────────────────────────────────────────────
     SAFETY NET — never leave .fi content invisible.
     If motion init throws or assets stall, force-reveal.
  ────────────────────────────────────────────── */
  function revealAll() {
    document.querySelectorAll('.fi:not(.v)').forEach(function (el) {
      el.classList.add('v');
      el.style.opacity = '';
      el.style.transform = '';
    });
  }
  var safetyTimer = setTimeout(revealAll, 2600);

  /* ──────────────────────────────────────────────
     FALLBACK reveals — IntersectionObserver
     (used when GSAP absent or reduced-motion)
  ────────────────────────────────────────────── */
  function fallbackReveals() {
    if (!('IntersectionObserver' in window)) { revealAll(); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('v'); io.unobserve(e.target); }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.fi').forEach(function (el) { io.observe(el); });
  }

  /* ──────────────────────────────────────────────
     COUNT-UP — animate numeric .stat-n on enter.
     Parses "$150k" → prefix "$", num 150, suffix "k".
     Non-numeric (e.g. "DUS") just reveals.
  ────────────────────────────────────────────── */
  function parseStat(raw) {
    var m = String(raw).match(/^(\D*?)([\d.,]+)(\D*)$/);
    if (!m) return null;
    var num = parseFloat(m[2].replace(/,/g, ''));
    if (isNaN(num)) return null;
    return { prefix: m[1], value: num, suffix: m[3], decimals: (m[2].split('.')[1] || '').length };
  }

  function countUp(el, useGSAP) {
    if (el.dataset.counted) return;
    el.dataset.counted = '1';
    var parsed = parseStat(el.textContent.trim());
    if (!parsed) return;
    var fmt = function (v) {
      return parsed.prefix + v.toFixed(parsed.decimals) + parsed.suffix;
    };
    if (useGSAP) {
      var obj = { v: 0 };
      window.gsap.to(obj, {
        v: parsed.value, duration: 1.6, ease: 'power2.out',
        onUpdate: function () { el.textContent = fmt(obj.v); }
      });
    } else {
      el.textContent = fmt(parsed.value);
    }
  }

  /* ──────────────────────────────────────────────
     MAGNETIC buttons — element drifts toward cursor
  ────────────────────────────────────────────── */
  function initMagnetic() {
    document.querySelectorAll('[data-magnetic]').forEach(function (el) {
      var strength = parseFloat(el.dataset.magnetic) || 0.35;
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        var x = e.clientX - (r.left + r.width / 2);
        var y = e.clientY - (r.top + r.height / 2);
        el.style.transform = 'translate(' + (x * strength) + 'px,' + (y * strength) + 'px)';
      });
      el.addEventListener('mouseleave', function () {
        el.style.transform = '';
      });
    });
  }

  /* ──────────────────────────────────────────────
     TILT — subtle 3D rotation following the cursor
  ────────────────────────────────────────────── */
  function initTilt() {
    document.querySelectorAll('[data-tilt]').forEach(function (el) {
      var max = parseFloat(el.dataset.tilt) || 6;
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform =
          'perspective(900px) rotateY(' + (px * max) + 'deg) rotateX(' + (-py * max) + 'deg) translateY(-8px)';
      });
      el.addEventListener('mouseleave', function () {
        el.style.transform = '';
      });
    });
  }

  /* ──────────────────────────────────────────────
     MOTION INIT — GSAP + ScrollTrigger (native scroll)
  ────────────────────────────────────────────── */
  function initMotion() {
    var gsap = window.gsap, ScrollTrigger = window.ScrollTrigger;
    gsap.registerPlugin(ScrollTrigger);
    document.documentElement.classList.add('sf-gsap');

    /* Native scroll only — no smooth-scroll library.
       macOS already provides momentum; a JS smoothing layer on top
       feels laggy ("hängt nach"). ScrollTrigger listens to native
       scroll directly, so reveals + parallax work unchanged.
       Anchor offset is handled in CSS via scroll-padding-top. */

    /* Staggered reveals — batch so grids cascade together */
    gsap.set('.fi', { opacity: 0, y: 26 });
    ScrollTrigger.batch('.fi', {
      start: 'top 88%',
      onEnter: function (batch) {
        gsap.to(batch, {
          opacity: 1, y: 0, duration: 0.95, ease: 'power3.out',
          stagger: 0.10, overwrite: true,
          onComplete: function () { batch.forEach(function (b) { b.classList.add('v'); }); }
        });
      }
    });

    /* Parallax — layers drift slower than scroll */
    document.querySelectorAll('[data-parallax]').forEach(function (el) {
      var amount = parseFloat(el.dataset.parallax) || 60;
      gsap.fromTo(el, { yPercent: -amount * 0.12 }, {
        yPercent: amount * 0.12, ease: 'none',
        scrollTrigger: { trigger: el.closest('section') || el, start: 'top bottom', end: 'bottom top', scrub: true }
      });
    });

    /* Hero — logo + mesh recede on scroll for depth */
    var heroLogo = document.querySelector('.hero-logo');
    var heroMesh = document.querySelector('.hero-mesh');
    var heroContent = document.querySelector('.hero-content');
    if (heroLogo) {
      gsap.to(heroLogo, {
        yPercent: 40, opacity: 0.2, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
      });
    }
    if (heroContent) {
      gsap.to(heroContent, {
        yPercent: 18, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
      });
    }
    if (heroMesh) {
      gsap.to(heroMesh, {
        yPercent: 22, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
      });
    }

    /* Count-up stats */
    document.querySelectorAll('.stat-n').forEach(function (el) {
      ScrollTrigger.create({
        trigger: el, start: 'top 90%', once: true,
        onEnter: function () { countUp(el, true); }
      });
    });

    clearTimeout(safetyTimer);
  }

  /* ──────────────────────────────────────────────
     BOOT
  ────────────────────────────────────────────── */
  try {
    if (reduceMotion || !hasGSAP) {
      fallbackReveals();
      document.querySelectorAll('.stat-n').forEach(function (el) { countUp(el, false); });
    } else {
      initMotion();
    }
    if (finePointer && !reduceMotion) {
      initMagnetic();
      initTilt();
    }
  } catch (err) {
    /* Anything goes wrong → content stays visible */
    if (window.console) console.warn('[sf] motion init failed, falling back:', err);
    revealAll();
  }

})();
