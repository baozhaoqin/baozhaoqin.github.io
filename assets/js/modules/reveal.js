/**
 * reveal.js — 元素进入视口时淡入
 * 职责：给匹配选择器的元素加 .reveal，由 IntersectionObserver 触发 .visible
 */

const DEFAULT_SELECTOR = '.card, .project-card, .note-list li, .contact-card';

export function initReveal(selector = DEFAULT_SELECTOR) {
  const targets = document.querySelectorAll(selector);
  if (!targets.length) return;

  // 不支持 IntersectionObserver 时直接显示，保证内容可见
  if (!('IntersectionObserver' in window)) {
    targets.forEach((el) => el.classList.add('visible'));
    return;
  }

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  targets.forEach((el) => {
    el.classList.add('reveal');
    io.observe(el);
  });
}
