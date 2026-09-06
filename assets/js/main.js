/* Manish Tamta — portfolio interactions
   Progressive enhancement only: the page is fully usable with JS disabled. */
(function () {
  "use strict";

  var root = document.documentElement;
  var nav = document.getElementById("siteNav");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- theme toggle --------------------------------------------------- */
  var THEME_KEY = "mt-theme";
  var toggle = document.getElementById("themeToggle");

  function systemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  var urlTheme = new URLSearchParams(location.search).get("theme");
  try {
    var saved = localStorage.getItem(THEME_KEY);
    root.setAttribute("data-theme", urlTheme || saved || systemTheme());
    if (urlTheme) localStorage.setItem(THEME_KEY, urlTheme);
  } catch (e) {
    root.setAttribute("data-theme", urlTheme || systemTheme());
  }
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
    });
  }

  /* ---- hero name typing (home page only) --------------------------- */
  var heroName = document.getElementById("heroName");
  if (heroName) {
    var fullName = (heroName.textContent || "Manish Tamta").trim();
    heroName.setAttribute("aria-label", fullName);
    var revealName = function () { heroName.style.visibility = "visible"; };
    setTimeout(revealName, 1600); // failsafe: never leave it hidden
    if (reduceMotion) {
      revealName();
    } else {
      try {
        heroName.textContent = "";
        var typed = document.createElement("span");
        typed.className = "typed";
        var caret = document.createElement("span");
        caret.className = "caret";
        caret.setAttribute("aria-hidden", "true");
        heroName.appendChild(typed);
        heroName.appendChild(caret);
        revealName();
        var ni = 0;
        var typeTick = function () {
          typed.textContent = fullName.slice(0, ni);
          if (ni >= fullName.length) { heroName.classList.add("typing-done"); return; }
          var pause = fullName.charAt(ni) === " " ? 190 : 82;
          ni++;
          setTimeout(typeTick, pause);
        };
        setTimeout(typeTick, 320);
      } catch (e) {
        heroName.textContent = fullName;
        revealName();
      }
    }
  }

  /* ---- sticky nav shadow -------------------------------------------- */
  function onScroll() {
    nav.classList.toggle("scrolled", window.scrollY > 8);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---- mobile menu ------------------------------------------------- */
  var menuBtn = document.getElementById("menuToggle");
  function closeMenu() {
    nav.classList.remove("menu-open");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "false");
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("menu-open");
      menuBtn.setAttribute("aria-expanded", String(open));
    });
  }
  document.querySelectorAll(".nav-links a").forEach(function (a) {
    a.addEventListener("click", closeMenu);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeMenu();
  });

  /* ---- scrollspy (home page only: in-page "#" nav links) ---------- */
  var linkFor = {};
  document.querySelectorAll('.nav-links a[href^="#"]').forEach(function (a) {
    linkFor[a.getAttribute("href").slice(1)] = a;
  });
  var sections = Array.prototype.slice.call(
    document.querySelectorAll("main section[id]")
  ).filter(function (s) { return linkFor[s.id]; });

  if ("IntersectionObserver" in window && sections.length) {
    var visible = {};
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visible[entry.target.id] = entry.isIntersecting;
      });
      // Highlight the topmost section currently crossing the centre band.
      var current = null;
      sections.forEach(function (s) {
        if (visible[s.id] && linkFor[s.id] && !current) current = s.id;
      });
      Object.keys(linkFor).forEach(function (id) {
        var on = id === current;
        linkFor[id].classList.toggle("active", on);
        if (on) linkFor[id].setAttribute("aria-current", "true");
        else linkFor[id].removeAttribute("aria-current");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* ---- reveal on scroll ---------------------------------------- */
  var revealTargets = document.querySelectorAll(
    ".section-head, .card, .clip, .pub, .talks-group, .cv-col, .contact-list, " +
    ".research-note, .cv-download, .worldmap, .collab, .section-more"
  );
  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealTargets.forEach(function (el) { el.classList.add("in"); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add("reveal"); });
    var revealer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          revealer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    revealTargets.forEach(function (el) { revealer.observe(el); });

    // Failsafe: never leave content hidden if the observer misfires
    // (deep-link loads, restored scroll position, throttled timers).
    var showInView = function () {
      revealTargets.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) el.classList.add("in");
      });
    };
    window.addEventListener("load", showInView);
    setTimeout(function () {
      revealTargets.forEach(function (el) { el.classList.add("in"); });
    }, 2200);
  }

  /* ---- research clips: play like a silent GIF --------------------
     Markup is `autoplay muted loop playsinline` (no controls) so phones just
     loop them. Here we: (a) hard-stop them for reduced-motion users, (b) add
     scrubber controls back on desktop pointer devices, (c) pause off-screen. */
  var vids = document.querySelectorAll(".clip video");
  var desktopPointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  vids.forEach(function (v) {
    if (reduceMotion) {
      v.autoplay = false;
      v.removeAttribute("autoplay");
      try { v.pause(); } catch (e) {}
      v.setAttribute("controls", "");            // let them start it manually if they want
    } else if (desktopPointer) {
      v.setAttribute("controls", "");            // hover-to-scrub on desktop, bare loop on touch
    }
  });

  if ("IntersectionObserver" in window && vids.length) {
    var vObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var v = entry.target;
        if (entry.isIntersecting) {
          if (!reduceMotion) { var p = v.play(); if (p) p.catch(function () {}); }
        } else if (!v.paused) {
          v.pause();
        }
      });
    }, { threshold: 0.35 });
    vids.forEach(function (v) { vObs.observe(v); });
  }

  /* ---- collaborators map: link cards <-> pins ------------------ */
  var pins = document.querySelectorAll(".worldmap .pin");
  var collabCards = document.querySelectorAll(".collab[data-key]");
  if (pins.length && collabCards.length) {
    var setActive = function (key, on) {
      pins.forEach(function (p) {
        if (p.getAttribute("data-key") === key) p.classList.toggle("is-active", on);
      });
      collabCards.forEach(function (c) {
        if (c.getAttribute("data-key") === key) c.classList.toggle("is-active", on);
      });
    };
    collabCards.forEach(function (c) {
      var key = c.getAttribute("data-key");
      c.addEventListener("mouseenter", function () { setActive(key, true); });
      c.addEventListener("mouseleave", function () { setActive(key, false); });
      c.addEventListener("focusin", function () { setActive(key, true); });
      c.addEventListener("focusout", function () { setActive(key, false); });
    });
    pins.forEach(function (p) {
      var key = p.getAttribute("data-key");
      p.addEventListener("mouseenter", function () { setActive(key, true); });
      p.addEventListener("mouseleave", function () { setActive(key, false); });
    });
  }

  /* ---- footer year --------------------------------------------- */
  var yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();
})();
