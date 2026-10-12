const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#site-navigation');
if (toggle && nav) {
  document.documentElement.classList.add('enhanced');
  const close = () => {nav.classList.remove('is-open');toggle.setAttribute('aria-expanded','false');toggle.textContent='Menu';};
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded',String(open));
    toggle.textContent = open ? 'Close' : 'Menu';
    nav.classList.toggle('is-open',open);
  });
  nav.addEventListener('click', e => {if (e.target.closest('a')) close();});
  document.addEventListener('keydown', e => {if (e.key === 'Escape' && nav.classList.contains('is-open')) {close();toggle.focus();}});
  matchMedia('(min-width:768px)').addEventListener('change', close);
}
const copy = document.querySelector('[data-copy-link]');
const status = document.querySelector('.copy-status');
if (copy && status) copy.addEventListener('click', async () => {
  const url = new URL(location.pathname,location.origin).href;
  try {
    if (!navigator.clipboard || !isSecureContext) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(url);
    status.textContent = 'Link copied.';
  } catch {
    status.textContent = 'Copy this link: ' + url;
  }
});
