/* ============================================================
   HANSCRYPTO — script.js
   Vanilla JS for:
     1. Nav border on scroll
     2. Scroll-triggered fade-in animations
   No libraries or frameworks needed.
============================================================ */

(function () {
  'use strict';

  /* ── 1. NAV: Add "scrolled" class when page is scrolled ──────
     This triggers a subtle bottom border on the sticky nav.
     You can change the scroll threshold (currently 50px) below.
  ────────────────────────────────────────────────────────────── */
  const nav = document.querySelector('.nav');

  function handleNavScroll() {
    if (window.scrollY > 50) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }

  window.addEventListener('scroll', handleNavScroll, { passive: true });
  handleNavScroll(); // run once on load in case page is already scrolled


  /* ── 2. FADE-IN ANIMATIONS on scroll ─────────────────────────
     All elements with the class .fade-in will animate into view
     when they enter the viewport.
     Uses IntersectionObserver for performance (no scroll math).
  ────────────────────────────────────────────────────────────── */

  // Options: rootMargin pushes the trigger point down slightly
  // so elements start animating just before they're fully visible.
  const observerOptions = {
    root: null,
    rootMargin: '0px 0px -60px 0px',
    threshold: 0.1
  };

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        // Stop observing once animated — no need to re-trigger
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe every .fade-in element
  document.querySelectorAll('.fade-in').forEach(function (el) {
    observer.observe(el);
  });


  /* ── 3. SMOOTH SCROLL for anchor links ──────────────────────
     Handles clicks on internal # links (like nav links).
     The CSS `scroll-behavior: smooth` handles most cases,
     but this JS version gives better control over offset
     to account for the fixed nav bar height.
  ────────────────────────────────────────────────────────────── */
  const NAV_HEIGHT = 80; // px — adjust if nav height changes

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return; // skip bare # links

      const target = document.querySelector(targetId);
      if (!target) return;

      e.preventDefault();

      const top = target.getBoundingClientRect().top + window.scrollY - NAV_HEIGHT;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });

})();
