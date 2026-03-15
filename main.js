/* =============================================
   THE MARGIN — main.js
   ============================================= */

// Highlight the active nav link based on current page
(function () {
  const links = document.querySelectorAll('.site-nav a');
  const current = window.location.pathname.split('/').pop() || 'index.html';

  links.forEach(link => {
    const href = link.getAttribute('href').split('/').pop();
    if (href === current) {
      link.style.color = 'var(--accent)';
      link.setAttribute('aria-current', 'page');
    }
  });
})();


// Animate cards into view as they scroll into the viewport
(function () {
  const cards = document.querySelectorAll('.card');

  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  cards.forEach(card => {
    card.style.animationPlayState = 'paused';
    observer.observe(card);
  });
})();


// Update footer year automatically
(function () {
  const copy = document.querySelector('.footer-copy');
  if (copy) {
    copy.textContent = copy.textContent.replace(/\d{4}/, new Date().getFullYear());
  }
})();
