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
   MODULE START: THEME TOGGLE
   New in V1.4. Dark is the default; light is stored under the "theme" key
   and survives navigation.

   The theme is actually applied by a small inline script in each page's
   <head> — it has to run before first paint or the dark default renders for
   a frame and flashes. That script only sets the attribute. This module owns
   the button's label, icon, and persistence, so the two can never disagree:
   it reads the attribute the head script left behind rather than reading
   localStorage a second time.

   The 404 page carries the head script but no button, so this bails there.
   ======================================================================== */
(function themeToggleModule(){
  const btn = document.getElementById('themeToggle');
  if(!btn) return;
  const root = document.documentElement;
  const meta = document.querySelector('meta[name="theme-color"]');
  const icon = btn.querySelector('.theme-icon');

  function apply(theme){
    const light = theme === 'light';
    if(light) root.dataset.theme = 'light'; else delete root.dataset.theme;
    btn.setAttribute('aria-pressed', String(light));
    btn.setAttribute('aria-label', light ? 'Switch to dark theme' : 'Switch to light theme');
    if(icon) icon.textContent = light ? '☀' : '☾';
    if(meta) meta.content = light ? '#faf9f7' : '#0a0a0a';
    /* Safari in private mode throws on write, not on read. Failing to persist
       is survivable — the toggle still works for the current page. */
    try{ localStorage.setItem('theme', theme); }catch(e){}
  }

  apply(root.dataset.theme === 'light' ? 'light' : 'dark');

  btn.addEventListener('click', () => {
    apply(root.dataset.theme === 'light' ? 'dark' : 'light');
  });
})();
/* ========================================================================
   MODULE END: THEME TOGGLE
   ======================================================================== */

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

/* ========================================================================
   MODULE START: CONTACT FORM (new in V1.4)
   Posts to the FastAPI backend. Bails early on every page that has no form,
   consistent with the guards added in V1.3.
   ======================================================================== */
(function contactFormModule(){
  const form = document.getElementById('contact-form');
  if(!form) return;

  const statusEl = document.getElementById('cf-status');
  const button = form.querySelector('button[type="submit"]');

  /* Relative URL: identical on localhost and in production, because the API
     and the site are served from the same origin. */
  const ENDPOINT = '/api/contact';

  function setStatus(text, kind){
    statusEl.textContent = text;
    statusEl.className = 'cf-status' + (kind ? ' is-' + kind : '');
  }

  function clearErrors(){
    form.querySelectorAll('.cf-field.has-error').forEach(f => {
      f.classList.remove('has-error');
      const msg = f.querySelector('.cf-error');
      if(msg) msg.remove();
    });
  }

  function showError(fieldName, text){
    const input = form.querySelector('[name="' + fieldName + '"]');
    const field = input && input.closest('.cf-field');
    if(!field) return;
    field.classList.add('has-error');
    const msg = document.createElement('p');
    msg.className = 'cf-error';
    msg.textContent = text;
    field.appendChild(msg);
  }

  form.addEventListener('submit', async (event) => {
    /* Without this the browser does a full page reload and the fetch never
       completes. */
    event.preventDefault();
    clearErrors();

    /* The browser's own validation first — instant, and saves a pointless
       round trip. The server validates the same rules again regardless;
       this is a convenience, never a security control. */
    if(!form.checkValidity()){
      form.reportValidity();
      return;
    }

    const payload = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      message: form.message.value.trim(),
      website: form.website.value
    };

    button.disabled = true;
    setStatus('Sending…', null);

    try{
      const response = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      /* 422 is FastAPI's validation rejection. detail is a list; each entry
         has loc (which field) and msg (why). */
      if(response.status === 422){
        const problem = await response.json();
        (problem.detail || []).forEach(d => {
          const field = d.loc && d.loc[d.loc.length - 1];
          if(field) showError(field, d.msg);
        });
        setStatus('Check the highlighted fields.', 'error');
        return;
      }

      if(!response.ok) throw new Error('Server returned ' + response.status);

      const data = await response.json();

      if(data.status === 'received'){
        form.reset();
        setStatus(data.message, 'success');
      } else {
        setStatus(data.message, 'error');
      }
    } catch(err){
      console.error(err);
      setStatus("Couldn't send that — email shaandilyaprathit@gmail.com instead.", 'error');
    } finally {
      button.disabled = false;
    }
  });
})();
/* ========================================================================
   MODULE END: CONTACT FORM
   ======================================================================== */