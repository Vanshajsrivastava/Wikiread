(() => {
    const topicInput = document.querySelector("[data-topic-input]");
    const linkContainer = document.querySelector("[data-research-links]");
    if (!topicInput || !linkContainer) {
        return;
    }

    const anchors = Array.from(linkContainer.querySelectorAll("[data-research-link]"));
    if (!anchors.length) {
        return;
    }

    const urlBuilders = [
        (q) => `https://en.wikipedia.org/wiki/Special:Search?search=${q}`,
        (q) => `https://scholar.google.com/scholar?q=${q}`,
        (q) => `https://search.crossref.org/?q=${q}`,
        (q) => `https://openlibrary.org/search?q=${q}`,
        (q) => `https://www.google.com/search?q=${q}`,
    ];

    const updateLinks = () => {
        const topic = topicInput.value.trim() || "general research";
        const encoded = encodeURIComponent(topic);
        anchors.forEach((anchor, index) => {
            const build = urlBuilders[index];
            if (build) {
                anchor.href = build(encoded);
            }
        });
    };

    topicInput.addEventListener("input", updateLinks);
    updateLinks();
})();
