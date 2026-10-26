// Maestro website: theme toggle, copy buttons, screen tabs and gesture presets.
(function () {
  "use strict";

  var root = document.documentElement;
  var announce = document.getElementById("announce");
  var darkQuery = window.matchMedia("(prefers-color-scheme: dark)");

  function say(text) {
    if (!announce) return;
    announce.textContent = "";
    window.setTimeout(function () { announce.textContent = text; }, 30);
  }

  // Theme: follows the system until the visitor picks one; the choice is kept in localStorage.
  function currentTheme() {
    return root.dataset.theme || (darkQuery.matches ? "dark" : "light");
  }

  function syncTheme() {
    var override = root.dataset.theme;
    var media = override ? (override === "dark" ? "all" : "not all") : "(prefers-color-scheme: dark)";
    document.querySelectorAll("picture[data-themed] source[data-for='dark']").forEach(function (source) {
      source.media = media;
    });
    var toggle = document.getElementById("theme-toggle");
    if (toggle) {
      toggle.setAttribute("aria-label", currentTheme() === "dark" ? "Switch to light theme" : "Switch to dark theme");
    }
  }

  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("maestro-theme", next); } catch (e) {}
      syncTheme();
      say(next === "dark" ? "Dark theme" : "Light theme");
    });
  }
  darkQuery.addEventListener("change", syncTheme);
  syncTheme();

  // Copy to clipboard. Links with data-copy fall back to their href when copying is unavailable.
  function fallbackCopy(text) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(area);
    return ok ? Promise.resolve() : Promise.reject(new Error("copy failed"));
  }

  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () { return fallbackCopy(text); });
    }
    return fallbackCopy(text);
  }

  function showCopied(el) {
    var label = el.querySelector(".btn-label");
    var use = el.querySelector("use");
    var oldLabel = label ? label.textContent : null;
    el.classList.add("is-copied");
    if (label) label.textContent = "Command copied";
    if (use) use.setAttribute("href", "#i-check");
    window.clearTimeout(el._copyTimer);
    el._copyTimer = window.setTimeout(function () {
      el.classList.remove("is-copied");
      if (label) label.textContent = oldLabel;
      if (use) use.setAttribute("href", "#i-copy");
    }, 2000);
  }

  document.querySelectorAll("[data-copy]").forEach(function (el) {
    el.addEventListener("click", function (event) {
      var text = el.getAttribute("data-copy");
      var href = el.getAttribute("href");
      if (href) event.preventDefault();
      copy(text).then(function () {
        showCopied(el);
        say("Copied to clipboard: " + text);
      }, function () {
        if (href) window.location.hash = href;
        say("Copy is not available. The command is shown in the Install section.");
      });
    });
  });

  // Tabs for app screens (WAI-ARIA tabs pattern with automatic activation).
  document.querySelectorAll("[data-tabs]").forEach(function (group) {
    var tabs = Array.prototype.slice.call(group.querySelectorAll("[role='tab']"));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab, false); });
      tab.addEventListener("keydown", function (event) {
        var next = null;
        if (event.key === "ArrowRight") next = tabs[(i + 1) % tabs.length];
        else if (event.key === "ArrowLeft") next = tabs[(i - 1 + tabs.length) % tabs.length];
        else if (event.key === "Home") next = tabs[0];
        else if (event.key === "End") next = tabs[tabs.length - 1];
        if (next) {
          event.preventDefault();
          select(next, true);
        }
      });
    });
  });

  // Gesture presets, matching the app's built-in gesture bundles.
  var presets = {
    windows: { up: "Full screen", down: "Omarchy menu", left: "Previous workspace", right: "Next workspace", tap: "Switch applications" },
    workspaces: { up: "Previous workspace", down: "Next workspace", left: "Previous workspace", right: "Next workspace", tap: "Next window" },
    media: { up: "Volume up", down: "Volume down", left: "Previous track", right: "Next track", tap: "Play or pause" },
    zoom: { up: "Zoom in", down: "Zoom out", left: "Zoom out", right: "Zoom in", tap: "Reset zoom" },
    custom: { up: "Your choice", down: "Your choice", left: "Your choice", right: "Your choice", tap: "Your choice" }
  };
  var chips = document.querySelectorAll("[data-preset]");
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var preset = presets[chip.getAttribute("data-preset")];
      chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
      document.querySelectorAll(".gesture [data-dir]").forEach(function (el) {
        el.textContent = preset[el.getAttribute("data-dir")];
      });
    });
  });
})();
