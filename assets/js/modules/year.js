/**
 * year.js — 页脚年份
 * 职责：把 #year 填成当前年份，省得每年手改
 */

export function initYear() {
  const el = document.getElementById('year');
  if (el) el.textContent = String(new Date().getFullYear());
}
