(function () {
    var root = document.documentElement;
    var toggles = document.querySelectorAll("[data-theme-toggle]");

    if (!toggles.length) {
        return;
    }

    function labelForTheme(theme) {
        return theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
    }

    function applyTheme(theme) {
        root.setAttribute("data-theme", theme);
        localStorage.setItem("wikiread-theme", theme);
        var label = labelForTheme(theme);
        toggles.forEach(function (toggle) {
            toggle.setAttribute("aria-label", label);
            toggle.setAttribute("title", label);
        });
    }

    var currentTheme = root.getAttribute("data-theme") || "light";
    applyTheme(currentTheme);

    toggles.forEach(function (toggle) {
        toggle.addEventListener("click", function () {
            var nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
            applyTheme(nextTheme);
        });
    });
})();
