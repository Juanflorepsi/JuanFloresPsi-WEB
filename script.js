// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
navToggle?.addEventListener('click', () => {
  const isOpen = navLinks.classList.toggle('open');
  navToggle.classList.toggle('is-open', isOpen);
  navToggle.setAttribute('aria-expanded', String(isOpen));
  navToggle.setAttribute('aria-label', isOpen ? 'Cerrar menú' : 'Abrir menú');
});
navLinks?.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    const isMobileDropdownToggle = a.classList.contains('nav-toplink') &&
      a.closest('.nav-item.has-dropdown') &&
      window.matchMedia('(max-width:960px)').matches;
    if (!isMobileDropdownToggle) {
      navLinks.classList.remove('open');
      navToggle?.classList.remove('is-open');
      navToggle?.setAttribute('aria-expanded', 'false');
      navToggle?.setAttribute('aria-label', 'Abrir menú');
    }
  });
});

// Dropdown menus (Sobre nosotros / Servicios)
function toggleDropdown(item, btn) {
  const isOpen = item.classList.contains('open');
  document.querySelectorAll('.nav-item.open').forEach(open => {
    open.classList.remove('open');
    open.querySelector('.dropdown-toggle')?.setAttribute('aria-expanded', 'false');
  });
  if (!isOpen) {
    item.classList.add('open');
    btn?.setAttribute('aria-expanded', 'true');
  }
}
document.querySelectorAll('.dropdown-toggle').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    toggleDropdown(btn.closest('.nav-item'), btn);
  });
});
document.querySelectorAll('.nav-item.has-dropdown > .nav-toplink').forEach(link => {
  link.addEventListener('click', (e) => {
    if (window.matchMedia('(max-width:960px)').matches) {
      e.preventDefault();
      const item = link.closest('.nav-item');
      toggleDropdown(item, item.querySelector('.dropdown-toggle'));
    }
  });
});

// FAQ accordion
document.querySelectorAll('.faq-item').forEach(item => {
  const q = item.querySelector('.faq-q');
  const a = item.querySelector('.faq-a');
  q.addEventListener('click', () => {
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(open => {
      open.classList.remove('open');
      open.querySelector('.faq-a').style.maxHeight = null;
    });
    if (!isOpen) {
      item.classList.add('open');
      a.style.maxHeight = a.scrollHeight + 'px';
    }
  });
});

// Cookie consent
(function(){
  const CONSENT_KEY = 'jfp_cookie_consent';
  const banner = document.getElementById('cookieBanner');
  const modal = document.getElementById('cookieModal');
  if (!banner) return;
  const analyticsCheckbox = document.getElementById('cookieAnalytics');

  function getConsent() {
    try { return JSON.parse(localStorage.getItem(CONSENT_KEY)); } catch (e) { return null; }
  }
  function saveConsent(value) {
    localStorage.setItem(CONSENT_KEY, JSON.stringify(value));
    banner.classList.remove('show');
    if (modal) modal.hidden = true;
  }
  const saved = getConsent();
  if (!saved) {
    requestAnimationFrame(() => banner.classList.add('show'));
  } else if (analyticsCheckbox) {
    analyticsCheckbox.checked = !!saved.analytics;
  }

  document.getElementById('cookieAccept')?.addEventListener('click', () => saveConsent({ necessary: true, analytics: true }));
  document.getElementById('cookieReject')?.addEventListener('click', () => saveConsent({ necessary: true, analytics: false }));
  document.getElementById('cookieSettings')?.addEventListener('click', () => { if (modal) modal.hidden = false; });
  document.getElementById('cookieModalClose')?.addEventListener('click', () => { if (modal) modal.hidden = true; });
  document.getElementById('cookieSavePrefs')?.addEventListener('click', () => {
    saveConsent({ necessary: true, analytics: !!analyticsCheckbox?.checked });
  });
  document.getElementById('cookiePrefsLink')?.addEventListener('click', () => {
    if (analyticsCheckbox) analyticsCheckbox.checked = !!getConsent()?.analytics;
    if (modal) modal.hidden = false;
  });
})();

// Scroll reveal
const revealEls = document.querySelectorAll('.reveal');
const io = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in');
      io.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });
revealEls.forEach(el => io.observe(el));
