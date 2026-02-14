(function () {
    var toggle = document.querySelector("[data-sidebar-toggle]");
    var sidebar = document.querySelector("[data-sidebar]");

    if (!toggle || !sidebar) {
        return;
    }

    function setOpen(open) {
        document.body.classList.toggle("sidebar-open", open);
        toggle.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
    }

    setOpen(false);

    toggle.addEventListener("click", function () {
        setOpen(!document.body.classList.contains("sidebar-open"));
    });

    sidebar.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.innerWidth <= 980) {
                setOpen(false);
            }
        });
    });

    document.addEventListener("click", function (event) {
        if (!document.body.classList.contains("sidebar-open")) {
            return;
        }

        if (!sidebar.contains(event.target) && !toggle.contains(event.target) && window.innerWidth <= 980) {
            setOpen(false);
        }
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 980) {
            setOpen(false);
        }
    });
})();
