/**
 * nav.js — 顶部导航交互
 * 职责：移动端汉堡菜单开合 + 滚动时给导航栏加阴影
 */

export function initNav() {
  const nav = document.getElementById('nav');
  const menuBtn = document.getElementById('menuBtn');
  const navLinks = document.getElementById('navLinks');

  // 移动端菜单
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
    navLinks.addEventListener('click', (e) => {
      if (e.target.tagName === 'A') navLinks.classList.remove('open');
    });
  }

  // 滚动阴影
  if (nav) {
    const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
}
