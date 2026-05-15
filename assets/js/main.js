(function () {
  var stage = document.getElementById("gallery-stage");
  var thumbs = document.querySelectorAll(".thumbs button");
  if (!stage || !thumbs.length) return;

  function setActive(btn) {
    thumbs.forEach(function (b) {
      b.classList.toggle("is-active", b === btn);
    });
  }

  thumbs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var src = btn.getAttribute("data-full");
      if (!src) return;
      var alt = btn.getAttribute("data-alt") || "";
      stage.innerHTML =
        '<img src="' +
        src +
        '" alt="' +
        alt.replace(/"/g, "&quot;") +
        '" width="960" height="720" loading="lazy" decoding="async" />';
      setActive(btn);
    });
  });

  var first = document.querySelector(".thumbs button.is-active") || thumbs[0];
  if (first) first.click();
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
