(function () {
  "use strict";

  // Header: solid background after scrolling
  var header = document.querySelector("[data-header]");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 24); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Mobile nav
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav]");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open);
      if (header) header.classList.toggle("is-scrolled", open || window.scrollY > 24);
    });
  }

  // Toasts auto-hide
  document.querySelectorAll(".toast").forEach(function (t) {
    setTimeout(function () { t.classList.add("is-hiding"); }, 6000);
    setTimeout(function () { t.remove(); }, 6500);
  });

  // Gallery lightbox
  var dataEl = document.getElementById("gallery-data");
  var lb = document.querySelector("[data-lightbox]");
  if (dataEl && lb) {
    var items = JSON.parse(dataEl.textContent);
    var img = lb.querySelector("[data-lb-img]");
    var cap = lb.querySelector("[data-lb-caption]");
    var count = lb.querySelector("[data-lb-count]");
    var idx = 0, lastFocus = null;

    var show = function (i) {
      idx = (i + items.length) % items.length;
      img.src = items[idx].src;
      cap.textContent = items[idx].caption || "";
      count.textContent = (idx + 1) + " / " + items.length;
    };
    var open = function (i) {
      lastFocus = document.activeElement;
      show(i);
      lb.hidden = false;
      document.body.style.overflow = "hidden";
      lb.querySelector("[data-lb-close]").focus();
    };
    var close = function () {
      lb.hidden = true;
      document.body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    };

    document.querySelectorAll("[data-gallery] [data-index]").forEach(function (btn) {
      btn.addEventListener("click", function () { open(parseInt(btn.dataset.index, 10)); });
    });
    lb.querySelector("[data-lb-close]").addEventListener("click", close);
    lb.querySelector("[data-lb-prev]").addEventListener("click", function () { show(idx - 1); });
    lb.querySelector("[data-lb-next]").addEventListener("click", function () { show(idx + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(idx - 1);
      if (e.key === "ArrowRight") show(idx + 1);
    });
    // Swipe
    var x0 = null;
    lb.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
      x0 = null;
    });
  }
})();
