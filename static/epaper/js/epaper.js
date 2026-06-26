(function () {
    var dataNode = document.getElementById("epaper-pages-data");
    if (!dataNode) {
        return;
    }

    var pages = JSON.parse(dataNode.textContent || "[]");
    var currentIndex = 0;
    var zoom = 100;
    var image = document.querySelector("[data-reader-image]");
    var title = document.querySelector("[data-reader-title]");
    var section = document.querySelector("[data-reader-section]");
    var thumbs = Array.prototype.slice.call(document.querySelectorAll(".page-thumb"));
    var zoomRange = document.querySelector("[data-reader-zoom]");

    function renderPage(index) {
        if (!pages[index] || !image) {
            return;
        }
        currentIndex = index;
        image.src = pages[index].image;
        image.alt = pages[index].title;
        if (title) {
            title.textContent = pages[index].title;
        }
        if (section) {
            section.textContent = pages[index].section || "";
        }
        thumbs.forEach(function (thumb, thumbIndex) {
            thumb.classList.toggle("is-active", thumbIndex === currentIndex);
        });
    }

    function setZoom(value) {
        zoom = Math.max(70, Math.min(160, value));
        if (zoomRange) {
            zoomRange.value = zoom;
        }
        if (image) {
            image.style.width = zoom + "%";
        }
    }

    thumbs.forEach(function (thumb) {
        thumb.addEventListener("click", function () {
            renderPage(Number(thumb.dataset.pageIndex || 0));
        });
    });

    var prev = document.querySelector("[data-reader-prev]");
    var next = document.querySelector("[data-reader-next]");
    var zoomIn = document.querySelector("[data-reader-zoom-in]");
    var zoomOut = document.querySelector("[data-reader-zoom-out]");
    var zoomFit = document.querySelector("[data-reader-fit]");

    if (prev) {
        prev.addEventListener("click", function () {
            renderPage((currentIndex - 1 + pages.length) % pages.length);
        });
    }
    if (next) {
        next.addEventListener("click", function () {
            renderPage((currentIndex + 1) % pages.length);
        });
    }
    if (zoomRange) {
        zoomRange.addEventListener("input", function () {
            setZoom(Number(zoomRange.value));
        });
    }
    if (zoomIn) {
        zoomIn.addEventListener("click", function () {
            setZoom(zoom + 10);
        });
    }
    if (zoomOut) {
        zoomOut.addEventListener("click", function () {
            setZoom(zoom - 10);
        });
    }
    if (zoomFit) {
        zoomFit.addEventListener("click", function () {
            setZoom(100);
        });
    }
})();
