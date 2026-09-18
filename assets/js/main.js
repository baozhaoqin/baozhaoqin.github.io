/**
 * main.js — 入口文件
 * 只负责按顺序初始化各个功能模块，具体逻辑都在 modules/ 下。
 */

import { initYear } from './modules/year.js';
import { initTheme } from './modules/theme.js';
import { initNav } from './modules/nav.js';
import { initReveal } from './modules/reveal.js';

function boot() {
  initYear();
  initTheme();
  initNav();
  initReveal();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}
