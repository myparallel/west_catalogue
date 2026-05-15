/* ========================================
   Gallery Manager
   ======================================== */
(function () {
  var DATA_SCRIPT = document.getElementById("gallery-data");
  if (!DATA_SCRIPT) return;

  var CONFIG_IMAGES = [];
  try { CONFIG_IMAGES = JSON.parse(DATA_SCRIPT.textContent); } catch(e) {}

  var STORAGE_KEY = "gallery_WEX280";
  var stage = document.getElementById("gallery-stage");
  var thumbsWrap = document.getElementById("gallery-thumbs");
  var catsWrap = document.getElementById("gallery-cats");
  var editBtn = document.getElementById("gallery-edit-btn");
  var saveBtn = document.getElementById("gallery-save-btn");
  var fileInput = document.getElementById("gallery-file-input");

  if (!stage || !thumbsWrap || !catsWrap) return;

  var currentFilter = "全部";
  var isEditMode = false;
  var selectedSrc = null;

  function loadStorage() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch(e) { return {}; }
  }

  function saveStorage(data) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch(e) { console.warn("localStorage full", e); }
  }

  function getEditData() {
    return loadStorage();
  }

  function setDeleted(src) {
    var d = getEditData();
    if (!d.deleted) d.deleted = [];
    if (d.deleted.indexOf(src) === -1) d.deleted.push(src);
    saveStorage(d);
  }

  function unsetDeleted(src) {
    var d = getEditData();
    if (!d.deleted) return;
    d.deleted = d.deleted.filter(function(s) { return s !== src; });
    saveStorage(d);
  }

  function isDeleted(src) {
    var d = getEditData();
    return d.deleted && d.deleted.indexOf(src) !== -1;
  }

  function getCategoryOverride(src) {
    var d = getEditData();
    return d.categories && d.categories[src] ? d.categories[src] : null;
  }

  function setCategoryOverride(src, cat) {
    var d = getEditData();
    if (!d.categories) d.categories = {};
    d.categories[src] = cat;
    saveStorage(d);
  }

  function getAddedImages() {
    var d = getEditData();
    return d.added || [];
  }

  function addAddedImage(img) {
    var d = getEditData();
    if (!d.added) d.added = [];
    d.added.push(img);
    saveStorage(d);
  }

  function removeAddedImage(src) {
    var d = getEditData();
    if (!d.added) return;
    d.added = d.added.filter(function(s) { return s.src !== src; });
    saveStorage(d);
  }

  function getAllImages() {
    var result = [];
    // config images minus deleted
    CONFIG_IMAGES.forEach(function(img) {
      if (!isDeleted(img.src)) {
        var cat = getCategoryOverride(img.src) || img.category;
        result.push({ src: img.src, alt: img.alt, category: cat, builtin: true });
      }
    });
    // user added images
    getAddedImages().forEach(function(img) {
      result.push({ src: img.src, alt: img.alt || "", category: img.category || "其他", builtin: false });
    });
    return result;
  }

  function storeLiveCounts(n) {
    var sku = (window.__PRODUCT_CONFIG__ && window.__PRODUCT_CONFIG__.sku) || "";
    if (sku) {
      try { localStorage.setItem("img_count_" + sku.replace(/-/g, ""), JSON.stringify(n)); } catch(e) {}
    }
  }

  function render() {
    var all = getAllImages();
    storeLiveCounts(all.length);
    updateHeroImage();
    // toggle empty / content
    var emptyEl = document.getElementById("gallery-empty");
    var contentEl = document.getElementById("gallery-content");
    var toolbarEl = document.getElementById("gallery-toolbar");
    if (all.length === 0) {
      if (emptyEl) emptyEl.hidden = false;
      if (contentEl) contentEl.hidden = true;
      if (toolbarEl) toolbarEl.hidden = true;
    } else {
      if (emptyEl) emptyEl.hidden = true;
      if (contentEl) contentEl.hidden = false;
      if (toolbarEl) toolbarEl.hidden = false;
    }
    var catTabs = catsWrap.querySelectorAll("button");
    catTabs.forEach(function(b) {
      b.classList.toggle("is-active", b.getAttribute("data-cat") === currentFilter);
    });
    var filtered = all.filter(function(img) {
      return currentFilter === "全部" || img.category === currentFilter;
    });
    // render thumbs
    var html = "";
    filtered.forEach(function(img, idx) {
      var act = selectedSrc === img.src ? ' is-active' : '';
      html += '<button type="button" class="gthumb' + act + '" data-full="' + img.src.replace(/"/g, "&quot;") + '" data-alt="' + (img.alt||"").replace(/"/g, "&quot;") + '" data-category="' + (img.category||"其他").replace(/"/g, "&quot;") + '" data-builtin="' + img.builtin + '"><img src="' + img.src.replace(/"/g, "&quot;") + '" alt="" width="120" height="90" loading="lazy" />';
      if (isEditMode) {
        html += '<button type="button" class="thumb-del" title="Delete">&times;</button>';
      }
      html += '<span class="thumb-cat">' + (img.category||"其他") + '</span></button>\n';
    });
    if (filtered.length === 0) {
      html = '<p class="gallery-empty">No images in this category.</p>';
    }
    thumbsWrap.innerHTML = html;
    // bind thumb clicks
    thumbsWrap.querySelectorAll(".gthumb").forEach(function(btn) {
      btn.addEventListener("click", function(e) {
        if (e.target.closest(".thumb-del")) return;
        selectImage(btn);
      });
      var delBtn = btn.querySelector(".thumb-del");
      if (delBtn) {
        delBtn.addEventListener("click", function(e) {
          e.stopPropagation();
          var src = btn.getAttribute("data-full");
          var builtin = btn.getAttribute("data-builtin") === "true";
          if (builtin) {
            setDeleted(src);
          } else {
            removeAddedImage(src);
          }
          if (selectedSrc === src) selectedSrc = null;
          render();
        });
      }
    });
    // select first visible if none selected
    if (!selectedSrc || !thumbsWrap.querySelector('.gthumb.is-active')) {
      var firstThumb = thumbsWrap.querySelector(".gthumb");
      if (firstThumb && !selectedSrc) {
        selectImage(firstThumb);
      } else if (!firstThumb) {
        stage.innerHTML = '<p style="color:var(--muted);padding:2rem">Select an image</p>';
      }
    }
  }

  function saveCategory(src, newCat, builtin) {
    if (builtin) {
      setCategoryOverride(src, newCat);
    } else {
      var added = getAddedImages();
      added = added.map(function(img) {
        if (img.src === src) img.category = newCat;
        return img;
      });
      var d = getEditData();
      d.added = added;
      saveStorage(d);
    }
  }

  function selectImage(btn) {
    if (!btn) return;
    var src = btn.getAttribute("data-full");
    var alt = btn.getAttribute("data-alt") || "";
    var cat = btn.getAttribute("data-category") || "其他";
    var builtin = btn.getAttribute("data-builtin") === "true";
    selectedSrc = src;
    // remove is-active from all
    thumbsWrap.querySelectorAll(".gthumb").forEach(function(b) {
      b.classList.toggle("is-active", b === btn);
    });
    // render stage
    var stageHtml = '<img src="' + src.replace(/"/g, "&quot;") + '" alt="' + alt.replace(/"/g, "&quot;") + '" width="960" height="720" loading="lazy" decoding="async" />';
    if (isEditMode) {
      stageHtml += '<div class="stage-edit-overlay stage-edit-top-right">' +
        '<select class="stage-cat-select">' +
        '<option value="主图"' + (cat==="主图"?" selected":"") + '>主图 / Main</option>' +
        '<option value="细节"' + (cat==="细节"?" selected":"") + '>细节 / Detail</option>' +
        '<option value="其他"' + (cat==="其他"?" selected":"") + '>其他 / Other</option>' +
        '</select></div>' +
        '<div class="stage-edit-overlay stage-edit-bottom-right">' +
        '<button type="button" class="stage-del-btn" data-src="' + src.replace(/"/g, "&quot;") + '">删除</button></div>';
    } else {
      var catEn = ({'主图':'Main','细节':'Detail','其他':'Other'})[cat] || cat;
      stageHtml += '<div class="stage-category"><span lang="en">' + catEn + '</span><span lang="zh" hidden>' + cat + '</span></div>';
    }
    stage.innerHTML = stageHtml;
    if (isEditMode) {
      var sel = stage.querySelector(".stage-cat-select");
      if (sel) {
        sel.addEventListener("change", function() {
          var newCat = sel.value;
          saveCategory(src, newCat, builtin);
          selectedSrc = null;
          render();
        });
      }
      var delBtn = stage.querySelector(".stage-del-btn");
      if (delBtn) {
        delBtn.addEventListener("click", function() {
          if (builtin) {
            setDeleted(src);
          } else {
            removeAddedImage(src);
          }
          selectedSrc = null;
          render();
        });
      }
    }
  }

  // Category tabs
  catsWrap.querySelectorAll("button").forEach(function(btn) {
    btn.addEventListener("click", function() {
      currentFilter = btn.getAttribute("data-cat");
      selectedSrc = null;
      render();
    });
  });

  function updateHeroImage() {
    var all = getAllImages();
    var mainImg = null;
    for (var i = 0; i < all.length; i++) {
      if (all[i].category === "主图") {
        mainImg = all[i].src;
        break;
      }
    }
    if (!mainImg && all.length > 0) mainImg = all[0].src;
    if (mainImg) {
      var heroImg = document.querySelector(".hero-visual img");
      if (heroImg && heroImg.getAttribute("src") !== mainImg) {
        heroImg.setAttribute("src", mainImg);
      }
    }
  }

  // Edit / Save toggle
  if (editBtn) {
    editBtn.addEventListener("click", function() {
      var all = getAllImages();
      if (all.length === 0) {
        // empty gallery → open file picker directly
        if (fileInput) fileInput.click();
        return;
      }
      isEditMode = !isEditMode;
      editBtn.hidden = isEditMode;
      if (saveBtn) saveBtn.hidden = !isEditMode;
      render();
    });
  }
  if (saveBtn) {
    saveBtn.addEventListener("click", function() {
      isEditMode = false;
      editBtn.hidden = false;
      saveBtn.hidden = true;
      render();
    });
  }

  // Add image via file input
  if (fileInput) {
    fileInput.addEventListener("change", function() {
      var files = fileInput.files;
      for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var reader = new FileReader();
        reader.onload = (function(f) {
          return function(e) {
            try {
              var dataUrl = e.target.result;
              addAddedImage({
                src: dataUrl,
                alt: f.name,
                category: "其他"
              });
              render();
            } catch(err) {
              alert("Failed to add image: " + err.message);
            }
          };
        })(file);
        reader.onerror = function() {
          alert("Failed to read file: " + file.name);
        };
        reader.readAsDataURL(file);
      }
      fileInput.value = "";
    });
  }

  // Add image button (injected into toolbar via JS)
  var addBtn = document.createElement("button");
  addBtn.type = "button";
  addBtn.className = "btn btn-sm";
  addBtn.id = "gallery-add-btn";
  addBtn.hidden = true;
  addBtn.innerHTML = '<span lang="en">+ Add Image</span><span lang="zh" hidden>+ 添加图片</span>';
  var actions = document.querySelector(".gallery-actions");
  if (actions) {
    actions.insertBefore(addBtn, saveBtn);
  }
  // apply current language to add button
  if (typeof currentLang !== "undefined") {
    addBtn.querySelectorAll("[lang]").forEach(function(el) {
      el.hidden = el.getAttribute("lang") !== currentLang;
    });
  }
  addBtn.addEventListener("click", function() {
    fileInput.click();
  });

  // Override edit/save to show/hide add button
  if (editBtn) {
    editBtn.addEventListener("click", function() {
      addBtn.hidden = false;
    });
  }
  if (saveBtn) {
    saveBtn.addEventListener("click", function() {
      addBtn.hidden = true;
    });
  }

  // Initial render
  render();

  // Apply lang toggle support for dynamically created elements
  document.addEventListener("langchange", function() {
    // handled by global i18n
  });
})();

/* ========================================
   Document Manager
   ======================================== */
(function () {
  var DOC_SCRIPT = document.getElementById("doc-data");
  if (!DOC_SCRIPT) return;

  var CONFIG_DOCS = [];
  try { CONFIG_DOCS = JSON.parse(DOC_SCRIPT.textContent); } catch(e) {}

  var STORAGE_KEY = "docs_WEX280";
  var table = document.getElementById("doc-table");
  var catsWrap = document.getElementById("doc-cats");
  var editBtn = document.getElementById("doc-edit-btn");
  var saveBtn = document.getElementById("doc-save-btn");
  var fileInput = document.getElementById("doc-file-input");

  if (!table || !catsWrap) return;

  var currentFilter = "全部";
  var isEditMode = false;

  function loadStorage() {
    try { var raw = localStorage.getItem(STORAGE_KEY); return raw ? JSON.parse(raw) : {}; } catch(e) { return {}; }
  }
  function saveStorage(d) { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(d)); } catch(e) { console.warn("localStorage full", e); } }

  function setDeleted(file) {
    var d = loadStorage();
    if (!d.deleted) d.deleted = [];
    if (d.deleted.indexOf(file) === -1) d.deleted.push(file);
    saveStorage(d);
  }
  function isDeleted(file) {
    var d = loadStorage();
    return d.deleted && d.deleted.indexOf(file) !== -1;
  }
  function getCatOverride(file) {
    var d = loadStorage();
    return d.categories && d.categories[file] ? d.categories[file] : null;
  }
  function setCatOverride(file, cat) {
    var d = loadStorage();
    if (!d.categories) d.categories = {};
    d.categories[file] = cat;
    saveStorage(d);
  }
  function getAdded() {
    var d = loadStorage();
    return d.added || [];
  }
  function addDoc(doc) {
    var d = loadStorage();
    if (!d.added) d.added = [];
    d.added.push(doc);
    saveStorage(d);
  }
  function removeAdded(file) {
    var d = loadStorage();
    if (!d.added) return;
    d.added = d.added.filter(function(x) { return x.file !== file; });
    saveStorage(d);
  }

  function getAllDocs() {
    var result = [];
    CONFIG_DOCS.forEach(function(doc) {
      if (!isDeleted(doc.file)) {
        var cat = getCatOverride(doc.file) || doc.category;
        result.push({ label: doc.label, file: doc.file, category: cat, format: doc.format, builtin: true });
      }
    });
    getAdded().forEach(function(doc) {
      result.push({ label: doc.label, file: doc.file, category: doc.category || "支持文档", format: doc.format || "PDF", builtin: false });
    });
    return result;
  }

  function fmtBadge(fmt) {
    return '<span class="doc-badge badge-' + fmt.toLowerCase() + '">' + fmt + '</span>';
  }

  function updateHeroSection() {
    var all = getAllDocs();
    // update count
    var countEl = document.getElementById("hero-docs-count");
    if (countEl) countEl.textContent = "(" + all.length + ")";
    // update dropdown menu items
    var menu = document.getElementById("hero-docs-menu");
    if (menu) {
      var itemsHtml = "";
      all.forEach(function(doc) {
        var fn = (doc.file.split("/").pop() || doc.file).replace(/"/g,"&quot;");
        itemsHtml += '<a class="docs-dropdown__item" href="' + doc.file.replace(/"/g,"&quot;") + '" download="' + fn + '">' + doc.label.replace(/"/g,"&quot;") + '</a>\n';
      });
      menu.innerHTML = itemsHtml;
    }
  }

  function triggerDownload(file, filename) {
    var a = document.createElement("a");
    a.href = file;
    a.download = filename || "download";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  function storeLiveDocCount(n) {
    var sku = (window.__PRODUCT_CONFIG__ && window.__PRODUCT_CONFIG__.sku) || "";
    if (sku) {
      try { localStorage.setItem("doc_count_" + sku.replace(/-/g, ""), JSON.stringify(n)); } catch(e) {}
    }
  }

  function render() {
    var all = getAllDocs();
    storeLiveDocCount(all.length);
    updateHeroSection();
    // toggle empty / content
    var emptyEl = document.getElementById("doc-empty");
    var contentEl = document.getElementById("doc-content");
    var toolbarEl = document.getElementById("doc-toolbar");
    if (all.length === 0) {
      if (emptyEl) emptyEl.hidden = false;
      if (contentEl) contentEl.hidden = true;
      if (toolbarEl) toolbarEl.hidden = true;
    } else {
      if (emptyEl) emptyEl.hidden = true;
      if (contentEl) contentEl.hidden = false;
      if (toolbarEl) toolbarEl.hidden = false;
    }
    // update cat tabs
    catsWrap.querySelectorAll("button").forEach(function(b) {
      b.classList.toggle("is-active", b.getAttribute("data-cat") === currentFilter);
    });
    var filtered = all.filter(function(doc) {
      return currentFilter === "全部" || doc.category === currentFilter;
    });
    // group by category
    var groups = {};
    var catOrder = ["用户手册","规格书","使用说明","支持文档","操作指引"];
    filtered.forEach(function(doc) {
      var c = doc.category || "支持文档";
      if (!groups[c]) groups[c] = [];
      groups[c].push(doc);
    });
    var html = "";
    catOrder.forEach(function(cat) {
      var docs = groups[cat];
      if (!docs) return;
      var rows = "";
      docs.forEach(function(doc, i) {
        var fn = (doc.file.split("/").pop() || doc.file).replace(/"/g,"&quot;");
        rows += '<tr class="doc-row" data-category="' + cat.replace(/"/g,"&quot;") + '" data-file="' + doc.file.replace(/"/g,"&quot;") + '" data-builtin="' + doc.builtin + '">';
        rows += '<td class="doc-num">' + (i+1) + '</td>';
        rows += '<td class="doc-fmt">' + fmtBadge(doc.format) + '</td>';
        rows += '<td class="doc-name"><a class="dl-link" href="' + doc.file.replace(/"/g,"&quot;") + '" download="' + fn + '">' + doc.label.replace(/"/g,"&quot;") + '</a></td>';
        rows += '<td class="doc-action">';
        if (isEditMode) {
          rows += '<select class="doc-cat-select">' +
            '<option value="用户手册"' + (cat==="用户手册"?" selected":"") + '>用户手册 / User Manual</option>' +
            '<option value="规格书"' + (cat==="规格书"?" selected":"") + '>规格书 / Specification</option>' +
            '<option value="使用说明"' + (cat==="使用说明"?" selected":"") + '>使用说明 / Instructions</option>' +
            '<option value="支持文档"' + (cat==="支持文档"?" selected":"") + '>支持文档 / Support</option>' +
            '<option value="操作指引"' + (cat==="操作指引"?" selected":"") + '>操作指引 / Guide</option>' +
            '</select>';
          rows += '<button type="button" class="doc-del-btn" title="Delete">&times;</button>';
        } else {
          rows += '<button type="button" class="doc-dl-btn" data-file="' + doc.file.replace(/"/g,"&quot;") + '" data-fn="' + fn + '"><span lang="en">Download</span><span lang="zh" hidden>下载</span></button>';
        }
        rows += '</td></tr>\n';
      });
      html += '<tbody class="doc-group" data-category="' + cat.replace(/"/g,"&quot;") + '">' +
        '<tr class="doc-group-header"><td colspan="4">' + cat + '</td></tr>' +
        rows + '</tbody>\n';
    });
    table.innerHTML = html;

    // bind events
    table.querySelectorAll(".doc-row").forEach(function(row) {
      var dlBtn = row.querySelector(".doc-dl-btn");
      if (dlBtn) {
        dlBtn.addEventListener("click", function() {
          var file = dlBtn.getAttribute("data-file");
          var fn = dlBtn.getAttribute("data-fn");
          triggerDownload(file, fn);
        });
      }
      if (isEditMode) {
        var sel = row.querySelector(".doc-cat-select");
        if (sel) {
          sel.addEventListener("change", function() {
            var newCat = sel.value;
            var file = row.getAttribute("data-file");
            var builtin = row.getAttribute("data-builtin") === "true";
            if (builtin) {
              setCatOverride(file, newCat);
            } else {
              var added = getAdded();
              added = added.map(function(d) {
                if (d.file === file) d.category = newCat;
                return d;
              });
              var store = loadStorage();
              store.added = added;
              saveStorage(store);
            }
            render();
          });
        }
        var delBtn = row.querySelector(".doc-del-btn");
        if (delBtn) {
          delBtn.addEventListener("click", function() {
            var file = row.getAttribute("data-file");
            var builtin = row.getAttribute("data-builtin") === "true";
            if (builtin) {
              setDeleted(file);
            } else {
              removeAdded(file);
            }
            render();
          });
        }
      }
    });
  }

  // Category filter tabs
  catsWrap.querySelectorAll("button").forEach(function(btn) {
    btn.addEventListener("click", function() {
      currentFilter = btn.getAttribute("data-cat");
      render();
    });
  });

  // Edit / Save toggle
  if (editBtn) {
    editBtn.addEventListener("click", function() {
      var all = getAllDocs();
      if (all.length === 0) {
        if (fileInput) fileInput.click();
        return;
      }
      isEditMode = !isEditMode;
      editBtn.hidden = isEditMode;
      if (saveBtn) saveBtn.hidden = !isEditMode;
      render();
    });
  }
  if (saveBtn) {
    saveBtn.addEventListener("click", function() {
      isEditMode = false;
      editBtn.hidden = false;
      saveBtn.hidden = true;
      render();
    });
  }

  // Add document via file input
  if (fileInput) {
    fileInput.addEventListener("change", function() {
      var files = fileInput.files;
      for (var i = 0; i < files.length; i++) {
        (function(file) {
          var label = file.name;
          var ext = label.split(".").pop().toLowerCase();
          var fmtMap = {"pdf":"PDF","png":"图片","jpg":"图片","jpeg":"图片","gif":"图片","webp":"图片","doc":"WORD","docx":"WORD","xls":"EXCEL","xlsx":"EXCEL","md":"MARKDOWN","markdown":"MARKDOWN"};
          var fmt = fmtMap[ext] || ext.toUpperCase();
          var reader = new FileReader();
          reader.onload = function(e) {
            try {
              addDoc({
                label: label,
                file: e.target.result,
                category: "支持文档",
                format: fmt
              });
              render();
            } catch(err) {
              alert("Failed to add document: " + err.message);
            }
          };
          reader.onerror = function() {
            alert("Failed to read file: " + file.name);
          };
          reader.readAsDataURL(file);
        })(files[i]);
      }
      fileInput.value = "";
    });
  }

  // Add doc button
  var addBtn = document.createElement("button");
  addBtn.type = "button";
  addBtn.className = "btn btn-sm";
  addBtn.id = "doc-add-btn";
  addBtn.hidden = true;
  addBtn.innerHTML = '<span lang="en">+ Add Document</span><span lang="zh" hidden>+ 添加文档</span>';
  var actions = document.querySelector(".doc-toolbar-actions");
  if (actions) {
    actions.insertBefore(addBtn, saveBtn);
  }
  if (typeof currentLang !== "undefined") {
    addBtn.querySelectorAll("[lang]").forEach(function(el) {
      el.hidden = el.getAttribute("lang") !== currentLang;
    });
  }
  addBtn.addEventListener("click", function() { fileInput.click(); });
  if (editBtn) {
    editBtn.addEventListener("click", function() { addBtn.hidden = false; });
  }
  if (saveBtn) {
    saveBtn.addEventListener("click", function() { addBtn.hidden = true; });
  }

  render();
})();

/* ========================================
   Video Manager
   ======================================== */
(function () {
  var DATA_SCRIPT = document.getElementById("video-data");
  if (!DATA_SCRIPT) return;

  var CONFIG_VIDEOS = [];
  try { CONFIG_VIDEOS = JSON.parse(DATA_SCRIPT.textContent); } catch(e) {}

  var STORAGE_KEY = "videos_WEX280";
  var playerWrap = document.getElementById("video-player");
  var placeholder = document.getElementById("video-placeholder");
  var listWrap = document.getElementById("video-list");
  var catsWrap = document.getElementById("video-cats");
  var editBtn = document.getElementById("video-edit-btn");
  var saveBtn = document.getElementById("video-save-btn");
  var fileInput = document.getElementById("video-file-input");

  if (!listWrap || !catsWrap) return;

  var currentFilter = "全部";
  var isEditMode = false;

  function loadStorage() {
    try { var raw = localStorage.getItem(STORAGE_KEY); return raw ? JSON.parse(raw) : {}; } catch(e) { return {}; }
  }
  function saveStorage(d) { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(d)); } catch(e) { console.warn("localStorage full", e); } }

  function setDeleted(file) {
    var d = loadStorage();
    if (!d.deleted) d.deleted = [];
    if (d.deleted.indexOf(file) === -1) d.deleted.push(file);
    saveStorage(d);
  }
  function isDeleted(file) {
    var d = loadStorage();
    return d.deleted && d.deleted.indexOf(file) !== -1;
  }
  function getCatOverride(file) {
    var d = loadStorage();
    return d.categories && d.categories[file] ? d.categories[file] : null;
  }
  function setCatOverride(file, cat) {
    var d = loadStorage();
    if (!d.categories) d.categories = {};
    d.categories[file] = cat;
    saveStorage(d);
  }
  function getAdded() {
    var d = loadStorage();
    return d.added || [];
  }
  function addVideo(v) {
    var d = loadStorage();
    if (!d.added) d.added = [];
    d.added.push(v);
    saveStorage(d);
  }
  function removeAdded(file) {
    var d = loadStorage();
    if (!d.added) return;
    d.added = d.added.filter(function(x) { return x.file !== file; });
    saveStorage(d);
  }

  function getAllVideos() {
    var result = [];
    CONFIG_VIDEOS.forEach(function(v) {
      if (!isDeleted(v.file)) {
        var cat = getCatOverride(v.file) || v.category;
        result.push({ label: v.label, file: v.file, poster: v.poster || "", category: cat, builtin: true });
      }
    });
    getAdded().forEach(function(v) {
      result.push({ label: v.label, file: v.file, poster: v.poster || "", category: v.category || "产品概览", builtin: false });
    });
    return result;
  }

  function playVideo(src, poster, label) {
    if (playerWrap) {
      playerWrap.src = src;
      playerWrap.poster = poster || "";
      playerWrap.load();
      playerWrap.play().catch(function(){});
      playerWrap.hidden = false;
    }
    if (placeholder) placeholder.hidden = true;
  }

  function storeLiveVideoCount(n) {
    var sku = (window.__PRODUCT_CONFIG__ && window.__PRODUCT_CONFIG__.sku) || "";
    if (sku) {
      try { localStorage.setItem("video_count_" + sku.replace(/-/g, ""), JSON.stringify(n)); } catch(e) {}
    }
  }

  function render() {
    var all = getAllVideos();
    storeLiveVideoCount(all.length);
    // toggle empty / content
    var emptyEl = document.getElementById("video-empty");
    var contentEl = document.getElementById("video-content");
    var toolbarEl = document.getElementById("video-toolbar");
    if (all.length === 0) {
      if (emptyEl) emptyEl.hidden = false;
      if (contentEl) contentEl.hidden = true;
      if (toolbarEl) toolbarEl.hidden = true;
    } else {
      if (emptyEl) emptyEl.hidden = true;
      if (contentEl) contentEl.hidden = false;
      if (toolbarEl) toolbarEl.hidden = false;
    }
    // update cat tabs
    if (catsWrap) {
      catsWrap.querySelectorAll("button").forEach(function(b) {
        b.classList.toggle("is-active", b.getAttribute("data-cat") === currentFilter);
      });
    }
    var filtered = all.filter(function(v) {
      return currentFilter === "全部" || v.category === currentFilter;
    });
    var groups = {};
    var catOrder = ["产品概览","使用说明","安装指引","操作演示","其他"];
    filtered.forEach(function(v) {
      var c = v.category || "产品概览";
      if (!groups[c]) groups[c] = [];
      groups[c].push(v);
    });
    var html = "";
    catOrder.forEach(function(cat) {
      var items = groups[cat];
      if (!items) return;
      var lis = "";
      items.forEach(function(v, i) {
        var src = v.file.replace(/"/g,"&quot;");
        var poster = (v.poster||"").replace(/"/g,"&quot;");
        var label = (v.label||"").replace(/"/g,"&quot;");
        lis += '<li class="vlist-item" data-src="' + src + '" data-poster="' + poster + '" data-label="' + label + '" data-category="' + cat.replace(/"/g,"&quot;") + '" data-builtin="' + v.builtin + '">';
        lis += '<span class="vlist-num">' + (i+1) + '</span>';
        lis += '<span class="vlist-label">' + label + '</span>';
        if (isEditMode) {
          lis += '<span class="vlist-actions">' +
            '<select class="vlist-cat-select">' +
            '<option value="产品概览"' + (cat==="产品概览"?" selected":"") + '>产品概览 / Overview</option>' +
            '<option value="使用说明"' + (cat==="使用说明"?" selected":"") + '>使用说明 / Instructions</option>' +
            '<option value="安装指引"' + (cat==="安装指引"?" selected":"") + '>安装指引 / Installation</option>' +
            '<option value="操作演示"' + (cat==="操作演示"?" selected":"") + '>操作演示 / Demo</option>' +
            '<option value="其他"' + (cat==="其他"?" selected":"") + '>其他 / Other</option>' +
            '</select>' +
            '<button type="button" class="vlist-del-btn" title="Delete">&times;</button></span>';
        }
        lis += '</li>\n';
      });
      html += '<ul class="vlist-group" data-category="' + cat.replace(/"/g,"&quot;") + '">' +
        '<li class="vlist-group-header">' + cat + '</li>' +
        lis + '</ul>\n';
    });
    listWrap.innerHTML = html;

    // bind events
    listWrap.querySelectorAll(".vlist-item").forEach(function(item) {
      item.addEventListener("click", function(e) {
        if (e.target.closest(".vlist-actions")) return;
        var src = item.getAttribute("data-src");
        var poster = item.getAttribute("data-poster");
        var label = item.getAttribute("data-label");
        playVideo(src, poster, label);
      });
      if (isEditMode) {
        var sel = item.querySelector(".vlist-cat-select");
        if (sel) {
          sel.addEventListener("change", function() {
            var newCat = sel.value;
            var file = item.getAttribute("data-src");
            var builtin = item.getAttribute("data-builtin") === "true";
            if (builtin) {
              setCatOverride(file, newCat);
            } else {
              var added = getAdded();
              added = added.map(function(v) {
                if (v.file === file) v.category = newCat;
                return v;
              });
              var store = loadStorage();
              store.added = added;
              saveStorage(store);
            }
            render();
          });
        }
        var delBtn = item.querySelector(".vlist-del-btn");
        if (delBtn) {
          delBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            var file = item.getAttribute("data-src");
            var builtin = item.getAttribute("data-builtin") === "true";
            if (builtin) {
              setDeleted(file);
            } else {
              removeAdded(file);
            }
            render();
          });
        }
      }
    });

    // auto-play first visible if none playing
    if (!playerWrap || playerWrap.hidden !== false) {
      var first = listWrap.querySelector(".vlist-item");
      if (first && first.getAttribute("data-src")) {
        playVideo(first.getAttribute("data-src"), first.getAttribute("data-poster"), first.getAttribute("data-label"));
      }
    }
  }

  // Category filter tabs
  if (catsWrap) {
    catsWrap.querySelectorAll("button").forEach(function(btn) {
      btn.addEventListener("click", function() {
        currentFilter = btn.getAttribute("data-cat");
        if (playerWrap) { playerWrap.hidden = true; }
        if (placeholder) placeholder.hidden = false;
        render();
      });
    });
  }

  // Edit / Save toggle
  if (editBtn) {
    editBtn.addEventListener("click", function() {
      var all = getAllVideos();
      if (all.length === 0) {
        if (fileInput) fileInput.click();
        return;
      }
      isEditMode = !isEditMode;
      editBtn.hidden = isEditMode;
      if (saveBtn) saveBtn.hidden = !isEditMode;
      render();
    });
  }
  if (saveBtn) {
    saveBtn.addEventListener("click", function() {
      isEditMode = false;
      editBtn.hidden = false;
      saveBtn.hidden = true;
      render();
    });
  }

  // Add video via file input
  if (fileInput) {
    fileInput.addEventListener("change", function() {
      var files = fileInput.files;
      for (var i = 0; i < files.length; i++) {
        (function(file) {
          var label = file.name;
          var reader = new FileReader();
          reader.onload = function(e) {
            try {
              addVideo({
                label: label,
                file: e.target.result,
                poster: "",
                category: "产品概览"
              });
              render();
            } catch(err) {
              alert("Failed to add video: " + err.message);
            }
          };
          reader.onerror = function() {
            alert("Failed to read file: " + file.name);
          };
          reader.readAsDataURL(file);
        })(files[i]);
      }
      fileInput.value = "";
    });
  }

  // Add video button
  var addBtn = document.createElement("button");
  addBtn.type = "button";
  addBtn.className = "btn btn-sm";
  addBtn.id = "video-add-btn";
  addBtn.hidden = true;
  addBtn.innerHTML = '<span lang="en">+ Add Video</span><span lang="zh" hidden>+ 添加视频</span>';
  var actions = document.querySelector(".video-actions");
  if (actions) {
    actions.insertBefore(addBtn, saveBtn);
  }
  if (typeof currentLang !== "undefined") {
    addBtn.querySelectorAll("[lang]").forEach(function(el) {
      el.hidden = el.getAttribute("lang") !== currentLang;
    });
  }
  addBtn.addEventListener("click", function() { fileInput.click(); });
  if (editBtn) {
    editBtn.addEventListener("click", function() { addBtn.hidden = false; });
  }
  if (saveBtn) {
    saveBtn.addEventListener("click", function() { addBtn.hidden = true; });
  }

  render();
})();

(function () {
  var modal = document.getElementById("quote-modal");
  var openBtn = document.getElementById("quote-open-btn");
  var form = document.getElementById("quote-form");
  var hint = document.getElementById("quote-form-hint");
  var dialog = modal && modal.querySelector(".quote-modal__dialog");
  if (!modal || !openBtn || !form || !dialog) return;

  var closeEls = modal.querySelectorAll("[data-close-quote]");
  var cfg = window.__PRODUCT_CONFIG__ || {};
  var SALES_EMAIL = cfg.email || "ftd_sales@west-hn.com";

  function getFocusables() {
    return Array.prototype.slice.call(
      dialog.querySelectorAll(
        "button:not([disabled]), a[href], input:not([disabled]), textarea:not([disabled]), select:not([disabled])"
      )
    );
  }

  function openModal() {
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");
    if (hint) hint.textContent = "";
    var firstField = document.getElementById("quote-name");
    if (firstField) firstField.focus();
  }

  function closeModal() {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
    openBtn.focus();
  }

  openBtn.addEventListener("click", openModal);

  closeEls.forEach(function (el) {
    el.addEventListener("click", function () {
      closeModal();
    });
  });

  document.addEventListener("keydown", function (e) {
    if (!modal.classList.contains("is-open")) return;
    if (e.key === "Escape") {
      e.preventDefault();
      closeModal();
      return;
    }
    if (e.key !== "Tab") return;
    var list = getFocusables();
    if (list.length < 2) return;
    var first = list[0];
    var last = list[list.length - 1];
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (hint) hint.textContent = "";
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    var name = document.getElementById("quote-name").value.trim();
    var company = document.getElementById("quote-company").value.trim();
    var email = document.getElementById("quote-email").value.trim();
    var phone = document.getElementById("quote-phone").value.trim();
    var region = document.getElementById("quote-region").value.trim();
    var message = document.getElementById("quote-message").value.trim();

    var prodName = cfg.name || "WE-T214 3-in-1 Soil Sensor Transmitter";
    var body =
      "Product: " + prodName + "\r\n\r\n" +
      "Name: " +
      name +
      "\r\n" +
      "Company: " +
      company +
      "\r\n" +
      "Email: " +
      email +
      "\r\n" +
      "Phone: " +
      (phone || "—") +
      "\r\n" +
      "Country / region: " +
      region +
      "\r\n\r\n" +
      "Application notes:\r\n" +
      message +
      "\r\n";

    var prodSku = cfg.sku || "WE-T214";
    var subject = prodSku + " Quote request — " + company;
    var mailto =
      "mailto:" +
      SALES_EMAIL +
      "?subject=" +
      encodeURIComponent(subject) +
      "&body=" +
      encodeURIComponent(body);

    window.location.href = mailto;
    closeModal();
    form.reset();
  });
})();

/* Download Helper - Ensure PDF triggers download */
(function () {
  var dlLinks = document.querySelectorAll(".dl-link");
  dlLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      // If the browser supports the download attribute, it will work.
      // This is a safety check for certain environments.
      var fileName = link.getAttribute("download");
      if (!fileName) return;
      
      // Force download for local preview if needed
      // (Note: browsers usually block automated downloads without user interaction, 
      // but here it is within a click event)
    });
  });
})();

/* Mobile Menu Toggle */
(function () {
  var toggle = document.getElementById("menu-toggle");
  var nav = document.getElementById("main-nav");
  var header = document.querySelector(".site-header");
  
  if (!toggle || !nav || !header) return;

  function toggleMenu() {
    var isOpen = nav.classList.toggle("is-active");
    header.classList.toggle("nav-open", isOpen);
    document.body.classList.toggle("nav-open", isOpen);
    toggle.setAttribute("aria-expanded", isOpen);
  }

  toggle.addEventListener("click", function(e) {
    e.stopPropagation();
    toggleMenu();
  });

  // Close menu when clicking links
  nav.querySelectorAll("a").forEach(function(link) {
    link.addEventListener("click", function() {
      if (nav.classList.contains("is-active")) {
        toggleMenu();
      }
    });
  });

  // Close when clicking outside
  document.addEventListener("click", function(e) {
    if (nav.classList.contains("is-active") && !nav.contains(e.target) && e.target !== toggle) {
      toggleMenu();
    }
  });
})();
