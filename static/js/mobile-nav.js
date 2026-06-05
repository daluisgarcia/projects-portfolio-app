// Mobile navigation drawer controller.
// Opens/closes the off-canvas drawer, handles backdrop click, ESC key,
// and auto-closes when a link inside the drawer is tapped.
// Requires [data-mobile-nav-drawer], [data-mobile-nav-backdrop], and
// one or more [data-mobile-nav-toggle] elements in the DOM.

(function () {
  "use strict";

  const drawer = document.querySelector("[data-mobile-nav-drawer]");
  const backdrop = document.querySelector("[data-mobile-nav-backdrop]");
  const toggles = document.querySelectorAll("[data-mobile-nav-toggle]");

  if (!drawer || !backdrop) return;

  const isOpen = () => drawer.getAttribute("aria-hidden") === "false";

  const open = () => {
    drawer.classList.remove("translate-x-full");
    drawer.setAttribute("aria-hidden", "false");
    backdrop.classList.remove("opacity-0", "pointer-events-none");
    backdrop.classList.add("opacity-100");
    document.body.style.overflow = "hidden";
    toggles.forEach((t) => t.setAttribute("aria-expanded", "true"));
  };

  const close = () => {
    drawer.classList.add("translate-x-full");
    drawer.setAttribute("aria-hidden", "true");
    backdrop.classList.add("opacity-0", "pointer-events-none");
    backdrop.classList.remove("opacity-100");
    document.body.style.overflow = "";
    toggles.forEach((t) => t.setAttribute("aria-expanded", "false"));
  };

  toggles.forEach((t) => t.addEventListener("click", () => (isOpen() ? close() : open())));
  backdrop.addEventListener("click", close);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && isOpen()) close();
  });

  // Auto-close when a link inside the drawer is tapped
  drawer.querySelectorAll("a").forEach((a) => a.addEventListener("click", close));
})();
