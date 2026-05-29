/* SF Finance — Shared JS v2.0 */

(function () {
  'use strict';

  /* ── NAV: scroll border + mobile toggle ── */
  const nav      = document.getElementById('sfNav');
  const navToggle = document.getElementById('navToggle');
  const navMobile = document.getElementById('navMobile');

  if (nav) {
    window.addEventListener('scroll', function () {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });
  }

  if (navToggle && navMobile) {
    navToggle.addEventListener('click', function () {
      const open = navToggle.classList.toggle('open');
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

  /* ── INTERSECTION OBSERVER: fade-in ── */
  const io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        e.target.classList.add('v');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.fi').forEach(function (el) {
    io.observe(el);
  });

  /* ── VIDEO TILE: click overlay ── */
  document.querySelectorAll('.video-tile[data-coming-soon]').forEach(function (tile) {
    tile.addEventListener('click', function () {
      if (tile.querySelector('.coming-overlay')) return;
      var overlay = document.createElement('div');
      overlay.className = 'coming-overlay';
      overlay.setAttribute('style',
        'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;' +
        'background:rgba(6,12,26,.75);font-family:var(--f-mono);font-size:.68rem;' +
        'letter-spacing:.08em;color:#c9a84c;text-transform:uppercase;z-index:10;' +
        'text-align:center;padding:1rem;');
      overlay.textContent = 'Kanal startet bald — folg uns!';
      tile.appendChild(overlay);
    });
  });

})();
