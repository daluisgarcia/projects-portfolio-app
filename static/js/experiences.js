// experiences.js — page-specific micro-interaction for the /experiences/ page.
//
// Cursor-follow glow on .glass-panel elements: each mousemove updates
// the --mouse-x and --mouse-y CSS custom properties on the panel,
// which any future CSS rule (e.g., a radial-gradient mask) can read.
// This implementation only sets the properties; the visual effect is
// a no-op until a CSS rule consumes them.

(function () {
    "use strict";

    document.querySelectorAll(".glass-panel").forEach(function (panel) {
        panel.addEventListener("mousemove", function (event) {
            var rect = panel.getBoundingClientRect();
            var x = event.clientX - rect.left;
            var y = event.clientY - rect.top;
            panel.style.setProperty("--mouse-x", x + "px");
            panel.style.setProperty("--mouse-y", y + "px");
        });
    });
})();
