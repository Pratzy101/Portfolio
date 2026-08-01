/* ============================================================================
   SHARED SITE BEHAVIOUR
   Loaded by every page. Carried forward unchanged from V1.2 except for the
   defensive guards noted below.

   Modules that only ever run on the homepage — ACTIVE NAV LINK and GITHUB
   ACTIVITY — deliberately stay inline in index.html rather than living here.
   Shipping them to every page would mean five pages downloading and parsing
   code that can never fire.

   V1.3 change: each module now bails early if the elements it owns are absent,
   because the case-study and log pages do not have all of the homepage's DOM.
   Without the guards, a missing element throws and every module defined after
   it in the file silently stops running.
   ============================================================================ */

/* ========================================================================
   MODULE START: CURSOR
   Same scroll + idle-timeout fix from V1.1: a scroll event clears the dot
   immediately, and a 600ms idle timer clears it as backup if the pointer
   simply stops moving.
   ======================================================================== */
(function cursorModule(){
  const cursor = document.getElementById('cursor');
  if(!cursor) return;
  let idleTimer = null;

  function activate(x, y){
    cursor.classList.add('active');
    cursor.style.left = x + 'px';
    cursor.style.top = y + 'px';
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => cursor.classList.remove('active'), 600);
  }

  window.addEventListener('pointermove', e => activate(e.clientX, e.clientY));
  window.addEventListener('pointerdown', e => activate(e.clientX, e.clientY));

  window.addEventListener('scroll', () => {
    clearTimeout(idleTimer);
    cursor.classList.remove('active');
  }, { passive: true });

  /* V1.3: selector widened to cover the new case-study and log page elements.
     Elements absent on a given page simply match nothing. */
  document.querySelectorAll('a, button, .work-card, .work-flagship, .case-nav a').forEach(el => {
    el.addEventListener('pointerenter', () => cursor.classList.add('grow'));
    el.addEventListener('pointerleave', () => cursor.classList.remove('grow'));
  });
})();
/* ========================================================================
   MODULE END: CURSOR
   ======================================================================== */

/* ========================================================================
   MODULE START: MAGNETIC BUTTONS
   Desktop only: buttons follow the mouse slightly.
   ======================================================================== */
(function magneticButtonsModule(){
  if(!window.matchMedia('(hover: hover)').matches) return;
  document.querySelectorAll('.btn, .ccard, .email-card').forEach(btn => {
    btn.addEventListener('mousemove', e => {
      const r = btn.getBoundingClientRect();
      const x = e.clientX - r.left - r.width/2;
      const y = e.clientY - r.top - r.height/2;
      btn.style.transform = `translate(${x*0.1}px, ${y*0.14}px)`;
    });
    btn.addEventListener('mouseleave', () => { btn.style.transform = 'translate(0,0)'; });
  });
})();
/* ========================================================================
   MODULE END: MAGNETIC BUTTONS
   ======================================================================== */

/* ========================================================================
   MODULE START: MOBILE MENU
   ======================================================================== */
(function mobileMenuModule(){
  const mobToggle = document.getElementById('mobToggle');
  const mobMenu = document.getElementById('mobMenu');
  if(!mobToggle || !mobMenu) return;

  function setOpen(open){
    mobMenu.classList.toggle('open', open);
    mobToggle.setAttribute('aria-expanded', String(open));
    mobToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }

  mobToggle.addEventListener('click', () => setOpen(!mobMenu.classList.contains('open')));
  mobMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setOpen(false)));

  /* V1.3: Escape closes the menu. On the case-study pages the menu covers the
     whole viewport, so a keyboard user who opens it needs a way out that is
     not "tab to the toggle". */
  document.addEventListener('keydown', e => {
    if(e.key === 'Escape' && mobMenu.classList.contains('open')) setOpen(false);
  });
})();
/* ========================================================================
   MODULE END: MOBILE MENU
   ======================================================================== */

/* ========================================================================
   MODULE START: SCROLL REVEAL
   ======================================================================== */
(function scrollRevealModule(){
  const targets = document.querySelectorAll('.reveal');
  if(!targets.length) return;

  /* V1.3: if the browser reports a reduced-motion preference, show everything
     immediately instead of observing. The CSS already neutralises the
     transition, but this also skips the observer work entirely. */
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    targets.forEach(el => el.classList.add('in-view'));
    return;
  }

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if(e.isIntersecting){ e.target.classList.add('in-view'); io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  targets.forEach(el => io.observe(el));
})();
/* ========================================================================
   MODULE END: SCROLL REVEAL
   ======================================================================== */
