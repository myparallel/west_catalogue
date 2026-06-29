# WEST Product Catalogue · WEST产品目录

[中文](#中文) | [English](#english)

---

## 中文

WEST IoT传感器产品线的交互式产品目录，支持中英双语切换，内置图库/视频/文档管理功能，数据持久化存储在浏览器localStorage中。

### 产品列表

| SKU | 产品描述 |
|-----|---------|
| WE-X280 | 工业边缘计算网关 |
| WE-T214 | 三合一土壤传感器变送器 |
| WE-T800 | 多功能野外监测仪 |
| WE-W200 | 专业气象站 |

### 功能特点

- **产品页面** — 概览、亮点、图库、视频、规格参数、下载、联系方式
- **双语支持** — 所有页面支持中英文切换
- **图库管理** — 上传、分类（主图/详情/其他）、删除图片；主图自动同步
- **视频管理** — 上传、分类、点击播放视频列表；支持多视频
- **文档管理** — 上传、分类（用户手册/规格书/说明书/技术支持/指南），格式标签（PDF/Word/Excel/Markdown/图片），下载按钮
- **目录页面** — 产品索引，实时下载计数，逐行删除并清理localStorage
- **数据持久化** — 所有用户编辑（添加/删除/分类）存储在浏览器localStorage中
- **打印就绪** — A4打印样式，支持目录导出

### 使用方法

在浏览器中打开 `index.html`，或访问 [GitHub Pages 站点](https://myparallel.github.io/west_catalogue/)。

### 添加新产品

1. 复制 `config.sample.json` → `configs/NEW-SKU.json`
2. 填写产品详情、图片、文档、视频
3. 将资源文件放入 `products/NEW-SKU/images/` 和 `products/NEW-SKU/docs/`
4. 运行 `python generate.py configs/NEW-SKU.json`
5. 在 `index.html` 的 `products` 数组中添加条目
6. 打开 `index.html` 验证

### 文件结构

```
├── index.html              # 目录首页
├── config.sample.json      # 产品配置模板
├── generate.py             # 静态页面生成器
├── configs/                # 产品JSON配置
├── products/               # 生成的产品页面
│   └── <SKU>/
│       ├── index.html
│       ├── images/
│       └── docs/
└── assets/
    ├── css/main.css
    └── js/main.js
```

### 技术栈

纯HTML/CSS/JS — 无框架，无构建工具。Python脚本（`generate.py`）用于从JSON配置生成静态页面。GitHub Actions用于自动部署Pages。

---

## English

Interactive product catalogue for WEST IoT sensor product line, featuring bilingual (EN/ZH) support, in-browser gallery/video/document management with localStorage persistence.

### Products

| SKU | Description |
|-----|-------------|
| WE-X280 | Industrial Edge Computing Gateway |
| WE-T214 | 3-in-1 Soil Sensor Transmitter |
| WE-T800 | Multi-Function Field Monitor |
| WE-W200 | Professional Weather Station |

### Features

- **Product pages** — Overview, highlights, gallery, videos, specs, downloads, contact
- **Bilingual** — Full English/Chinese toggle on all pages
- **Gallery Manager** — Upload, categorize (Main/Detail/Other), delete images; hero image auto-syncs with Main category
- **Video Manager** — Upload, categorize, click-to-play video list; multi-video support
- **Document Manager** — Upload, categorize (User Manual/Specification/Instructions/Support/Guide), format badges (PDF/Word/Excel/Markdown/Image), download buttons
- **Catalog page** — Product index with live Download count, per-row delete with localStorage cleanup
- **Persistent** — All user edits (add/delete/categorize) stored in browser localStorage
- **Print-ready** — A4 print styles for catalogue export

### Usage

Open `index.html` in a browser, or visit the [GitHub Pages site](https://myparallel.github.io/west_catalogue/).

### Adding a new product

1. Copy `config.sample.json` → `configs/NEW-SKU.json`
2. Fill in product details, images, documents, videos
3. Place assets in `products/NEW-SKU/images/` and `products/NEW-SKU/docs/`
4. Run `python generate.py configs/NEW-SKU.json`
5. Add entry to the `products` array in `index.html`
6. Open `index.html` to verify

### File structure

```
├── index.html              # Catalogue landing page
├── config.sample.json      # Product config template
├── generate.py             # Static page generator
├── configs/                # Product JSON configs
├── products/               # Generated product pages
│   └── <SKU>/
│       ├── index.html
│       ├── images/
│       └── docs/
└── assets/
    ├── css/main.css
    └── js/main.js
```

### Tech

Pure HTML/CSS/JS — no frameworks, no build tools. Python script (`generate.py`) for static page generation from JSON configs. GitHub Actions for automatic Pages deployment.

---

**海南世电科技有限公司** · WEST Electronics Technology Co., Ltd.
