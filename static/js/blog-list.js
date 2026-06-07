// blog-list.js — page-specific behavior for /blog/.
//
// Two effects:
//   1. Cursor-follow on .bento-card elements: each mousemove updates
//      the --mouse-x and --mouse-y CSS custom properties on the card.
//      The CSS in blog-list.css reads these for the hover-glow effect.
//   2. Load more (AJAX append): when the "LOAD MORE LOGS" button is
//      clicked, fetch the next page from the server (via ?page=N&partial=1)
//      and append the returned cards to the existing grid. Hides the
//      button when fewer cards than page_size are returned (last page).
//
// Category filter is server-side (chips are <a href="?category=<slug>">)
// — no JS interception needed for filtering. The "load more" handler
// preserves the active filter by reading the current URL's category
// param and passing it to the next page request.

(function () {
    "use strict";

    function initBentoCards(scope) {
        (scope || document).querySelectorAll(".bento-card").forEach(function (card) {
            // Avoid double-binding if the card already has a handler.
            if (card.__bentoBound) return;
            card.__bentoBound = true;
            card.addEventListener("mousemove", function (event) {
                var rect = card.getBoundingClientRect();
                var x = event.clientX - rect.left;
                var y = event.clientY - rect.top;
                card.style.setProperty("--mouse-x", x + "px");
                card.style.setProperty("--mouse-y", y + "px");
            });
        });
    }

    function initLoadMore() {
        var btn = document.getElementById("load-more-btn");
        if (!btn) return;
        var label = document.getElementById("load-more-label");
        var grid = document.getElementById("blog-cards-grid");
        if (!grid) return;

        btn.addEventListener("click", function () {
            var nextPage = parseInt(btn.getAttribute("data-next-page"), 10);
            var pageSize = parseInt(btn.getAttribute("data-page-size"), 10);
            var baseUrl = btn.getAttribute("data-base-url");

            // Build the URL for the next page, preserving any active category filter.
            var params = new URLSearchParams();
            params.set("page", String(nextPage));
            params.set("partial", "1");
            var activeCategory = new URLSearchParams(window.location.search).get("category");
            if (activeCategory) params.set("category", activeCategory);

            var url = baseUrl + "?" + params.toString();

            // Lock the button to prevent double-clicks.
            btn.disabled = true;
            if (label) label.textContent = "LOADING...";

            fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
                .then(function (response) {
                    if (!response.ok) throw new Error("HTTP " + response.status);
                    return response.text();
                })
                .then(function (html) {
                    // Parse the response and extract the new card anchors.
                    var temp = document.createElement("div");
                    temp.innerHTML = html;
                    var newCards = temp.querySelectorAll("a.bento-card");
                    var count = newCards.length;

                    // Append each new card to the existing grid.
                    newCards.forEach(function (card) {
                        grid.appendChild(card);
                    });

                    // Re-attach the bento-card glow handler to the new cards.
                    initBentoCards(grid);

                    // If we got fewer cards than page_size, we're on the last page.
                    if (count < pageSize) {
                        // No more pages — remove the button.
                        btn.remove();
                    } else {
                        // More pages — update the button to point to the next page.
                        btn.setAttribute("data-next-page", String(nextPage + 1));
                        btn.disabled = false;
                        if (label) label.textContent = "LOAD MORE LOGS";
                    }
                })
                .catch(function (error) {
                    console.error("Load more failed:", error);
                    btn.disabled = false;
                    if (label) label.textContent = "LOAD MORE LOGS (retry)";
                });
        });
    }

    // Run inline if DOM is already ready (script at end of body), otherwise wait.
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            initBentoCards();
            initLoadMore();
        });
    } else {
        initBentoCards();
        initLoadMore();
    }
})();
