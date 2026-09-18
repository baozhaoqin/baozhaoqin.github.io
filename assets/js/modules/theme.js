/**
 * theme.js — 明暗主题切换
 * 职责：读取 localStorage 记忆 → 应用主题 → 绑定切换按钮
 */

const STORAGE_KEY = 'theme';
const ICONS = { light: '🌙', dark: '☀️' };
const DEFAULT_THEME = 'light';

/** 把主题写到 <html data-theme>，并同步按钮图标 */
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const icon = document.getElementById('themeIcon');
  if (icon) icon.textContent = ICONS[theme] || ICONS[DEFAULT_THEME];
}

/** 读取当前主题（以 DOM 为准，避免和数据属性不同步） */
function currentTheme() {
  return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
}

export function initTheme() {
  const btn = document.getElementById('themeBtn');
  if (!btn) return;

  let saved = null;
  try {
    saved = localStorage.getItem(STORAGE_KEY);
  } catch {
    /* 隐私模式下 localStorage 可能不可用，忽略即可 */
  }
  applyTheme(saved || DEFAULT_THEME);

  btn.addEventListener('click', () => {
    const next = currentTheme() === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      /* 写不进去也不影响本次切换 */
    }
  });
}
