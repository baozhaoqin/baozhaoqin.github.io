# baozhaoqin.github.io

My personal homepage —— 纯静态、零依赖，托管在 GitHub Pages。

源码按模块拆分，用 `build.py` 生成根目录的 `index.html`（产物已提交，GitHub Pages 直接用）。

## 目录结构

```
.
├── index.html            ← 构建产物（不要手改，改完 src/ 重新构建）
├── build.py              ← 构建脚本（零第三方依赖，Python 3.8+）
├── src/                  ← 源码
│   ├── data/site.json        站点内容（个人信息 / 导航 / 项目 / 笔记 / 联系方式）
│   ├── templates/base.html   页面骨架（head、CSS/JS 引入、区块占位）
│   └── partials/             各区块片段：nav / hero / about / projects / notes / contact / footer / scripts
└── assets/
    ├── css/
    │   ├── tokens.css        设计变量：颜色、阴影、圆角、尺寸、暗色主题
    │   ├── base.css          重置、基础排版、.wrap、减少动效偏好
    │   ├── layout.css        导航、首屏、区块、页脚、响应式断点
    │   └── components.css    按钮、卡片、标签、项目卡、笔记列表、联系卡、淡入
    └── js/
        ├── main.js           入口，只负责按顺序初始化各模块
        └── modules/
            ├── theme.js      明暗主题切换（localStorage 记忆）
            ├── nav.js        移动端菜单 + 滚动阴影
            ├── reveal.js     进入视口淡入
            └── year.js       页脚年份
```

## 常用操作

```bash
# 构建（生成 / 覆盖 index.html）
python build.py

# 只校验模板和数据，不写文件（改完想先确认没写错）
python build.py --check

# 本地预览（ES module 需要 http 协议，直接双击 index.html 不行）
python -m http.server 8000
# 然后打开 http://localhost:8000
```

> Windows 上若 `python` 指向了损坏的安装，用完整路径：
> `C:\Users\yx200\AppData\Local\Programs\Python\Python312\python.exe build.py`

## 改内容

大部分改动**不用碰 HTML**，直接编辑 `src/data/site.json` 后重新构建：

| 想改什么 | 改哪里 |
| --- | --- |
| 姓名 / 简介 / 头像文字 | `hero` |
| 导航项 | `nav` |
| 关于我三张卡 | `about.cards` |
| 项目卡片（新增就加一条） | `projects.items` |
| 笔记列表 | `notes.items` |
| 联系方式 | `contact.items` |
| 配色 / 暗色主题 | `assets/css/tokens.css` |

要新增一个整块区域：在 `src/partials/` 建 `xxx.html`，再到 `src/templates/base.html` 里加一行 `{{> xxx}}`。

## 模板语法（`build.py` 实现，够用就好）

```html
{{site.title}}                          变量，支持 a.b.c 路径
{{#if btn.external}} ... {{/if}}        条件，空值 / 空数组 / false 视为假，字段省略也当作假
{{#for nav as link}} ... {{/for}}       循环，体内用 {{link.href}}；支持嵌套
{{> nav}}                               引入 src/partials/nav.html，自动继承缩进
```

变量取值失败会直接报错中断构建，避免渲染出空洞页面。
