(function () {
    function debounce(fn, delay) {
        var timer;
        return function () {
            var context = this;
            var args = arguments;
            clearTimeout(timer);
            timer = setTimeout(function () {
                fn.apply(context, args);
            }, delay);
        };
    }

    var editors = document.querySelectorAll("[data-markdown-editor]");

    editors.forEach(function (editor) {
        var textarea = editor.querySelector("textarea[name='content']");
        var preview = editor.querySelector("[data-preview-target]");
        var previewUrl = editor.getAttribute("data-preview-url");

        if (!textarea || !preview || !previewUrl) {
            return;
        }

        function renderPreview() {
            var text = textarea.value || "";

            if (!text.trim()) {
                preview.innerHTML = "<p>Live preview will appear here.</p>";
                return;
            }

            fetch(previewUrl + "?text=" + encodeURIComponent(text), {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error("Preview request failed");
                    }
                    return response.json();
                })
                .then(function (payload) {
                    preview.innerHTML = payload.html || "<p>Unable to preview content.</p>";
                })
                .catch(function () {
                    preview.innerHTML = "<p>Preview is currently unavailable.</p>";
                });
        }

        var debouncedRender = debounce(renderPreview, 180);
        textarea.addEventListener("input", debouncedRender);
        renderPreview();
    });
})();
