// blog-record.js — page-specific micro-interaction for /blog/<slug>/.
//
// Two effects:
//   1. Reading progress bar: on every scroll, compute the page scroll
//      progress as a percentage of (scrollTop / (scrollHeight - clientHeight))
//      and set the width of #reading-bar. The bar element is pinned to
//      the top of the viewport via .reading-progress-container in
//      blog-record.css.
//   2. Bento-card micro-interaction on the related-articles grid: a
//      small translateY on mouseenter / leave. Subtle but reinforces
//      the "clickable" affordance for the related-post cards.
//
// Both effects are wrapped in a DOMContentLoaded listener so the
// script is safe to load via {% block extra_js %} at the end of <body>
// or via defer in <head>. Optional-chaining guards on the bar element
// so a missing #reading-bar doesn't throw.

(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        // 1. Reading progress bar
        var bar = document.getElementById("reading-bar");
        if (bar) {
            var updateReadingBar = function () {
                var winScroll =
                    document.body.scrollTop ||
                    document.documentElement.scrollTop;
                var height =
                    document.documentElement.scrollHeight -
                    document.documentElement.clientHeight;
                var scrolled = height > 0 ? (winScroll / height) * 100 : 0;
                bar.style.width = scrolled + "%";
            };
            window.addEventListener("scroll", updateReadingBar, { passive: true });
            updateReadingBar();
        }

        // 2. Bento-card translateY micro-interaction
        var cards = document.querySelectorAll(".bento-card");
        cards?.forEach(function (card) {
            card.addEventListener("mouseenter", function () {
                card.style.transform = "translateY(-4px)";
            });
            card.addEventListener("mouseleave", function () {
                card.style.transform = "translateY(0)";
            });
        });
    });
})();
