/* Lovinaland admin: draft auto-translation toolbar + copy-link buttons. */
(function () {
  "use strict";

  function onReady(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  // ---- copy-to-clipboard for share links (change list & inlines)
  document.addEventListener("click", function (e) {
    var el = e.target.closest(".ll-copy");
    if (!el) return;
    e.preventDefault();
    var text = el.getAttribute("data-copy");
    var done = function () {
      var old = el.textContent;
      el.textContent = "✓ copied";
      setTimeout(function () { el.textContent = old; }, 1400);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done);
    } else {
      var ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
      done();
    }
  });

  onReady(function () {
    var cfgEl = document.getElementById("autotranslate-config");
    if (!cfgEl) return;
    var cfg = JSON.parse(cfgEl.textContent);
    var langs = cfg.languages;
    var form = document.querySelector("#content-main form");
    if (!form) return;

    // Collect translatable base names: fields that exist as <base>_<lang> for every language.
    var re = new RegExp("^(.+)_(" + langs.join("|") + ")$");
    var groups = {};
    form.querySelectorAll("input[type=text], textarea").forEach(function (el) {
      var m = el.name && el.name.match(re);
      if (!m || el.name.indexOf("-") !== -1) return;
      (groups[m[1]] = groups[m[1]] || {})[m[2]] = el;
    });
    var bases = Object.keys(groups).filter(function (b) {
      return langs.every(function (l) { return groups[b][l]; });
    });
    if (!bases.length) return;

    // Toolbar
    var bar = document.createElement("div");
    bar.className = "ll-translate";
    var srcOptions = langs.map(function (l) {
      return '<option value="' + l + '">' + l.toUpperCase() + "</option>";
    }).join("");
    var targetBoxes = langs.map(function (l) {
      return '<label class="ll-target" data-lang="' + l + '"><input type="checkbox" value="' + l + '" checked> ' + l.toUpperCase() + "</label>";
    }).join("");
    bar.innerHTML =
      '<strong>🌐 Auto-translate</strong>' +
      '<label>from <select class="ll-src">' + srcOptions + "</select></label>" +
      '<span class="ll-arrow">→</span>' + targetBoxes +
      '<label class="ll-overwrite"><input type="checkbox" class="ll-ow"> overwrite filled fields</label>' +
      '<button type="button" class="button ll-go">Translate</button>' +
      '<span class="ll-status"></span>' +
      '<div class="ll-hint">Draft only: review the text, tick “checked”, then Save.</div>';
    var anchor = form.querySelector("fieldset");
    if (anchor) anchor.parentNode.insertBefore(bar, anchor);
    else form.prepend(bar);

    var src = bar.querySelector(".ll-src");
    var status = bar.querySelector(".ll-status");
    function syncTargets() {
      bar.querySelectorAll(".ll-target").forEach(function (lbl) {
        var same = lbl.dataset.lang === src.value;
        lbl.style.display = same ? "none" : "";
      });
    }
    src.addEventListener("change", syncTargets);
    syncTargets();

    bar.querySelector(".ll-go").addEventListener("click", function () {
      var source = src.value;
      var overwrite = bar.querySelector(".ll-ow").checked;
      var targets = Array.prototype.map.call(
        bar.querySelectorAll(".ll-target input:checked"), function (i) { return i.value; }
      ).filter(function (l) { return l !== source; });
      if (!targets.length) { status.textContent = "Pick a target language"; return; }

      var fields = {};
      bases.forEach(function (b) {
        var text = groups[b][source].value;
        if (!text.trim()) return;
        var needed = overwrite || targets.some(function (t) { return !groups[b][t].value.trim(); });
        if (needed) fields[b] = text;
      });
      if (!Object.keys(fields).length) { status.textContent = "Nothing to translate (targets already filled)"; return; }

      var btn = this;
      btn.disabled = true;
      status.className = "ll-status";
      status.textContent = "Translating…";
      fetch(cfg.url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: JSON.stringify({ source: source, targets: targets, fields: fields }),
      })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
        .then(function (res) {
          var tr = res.data.translations || res.data.partial || {};
          var count = 0;
          Object.keys(tr).forEach(function (lang) {
            Object.keys(tr[lang]).forEach(function (b) {
              var el = groups[b][lang];
              if (overwrite || !el.value.trim()) {
                el.value = tr[lang][b];
                el.classList.add("ll-filled");
                el.dispatchEvent(new Event("input", { bubbles: true }));
                count++;
              }
            });
            var check = document.getElementById("id_reviewed_" + lang);
            if (check) check.checked = false;
          });
          if (!res.ok) {
            status.className = "ll-status ll-error";
            status.textContent = (res.data.error || "Error") + (count ? " (" + count + " fields filled)" : "");
          } else {
            status.className = "ll-status ll-ok";
            status.textContent = "✓ " + count + " fields filled via " + res.data.provider + ". Review and save.";
          }
        })
        .catch(function (err) {
          status.className = "ll-status ll-error";
          status.textContent = "Network error: " + err;
        })
        .finally(function () { btn.disabled = false; });
    });
  });
})();
