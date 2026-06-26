(function () {
    var dataNode = document.getElementById("epaper-pages-data");
    if (!dataNode) {
        return;
    }

    var pages = JSON.parse(dataNode.textContent || "[]");
    var editionsNode = document.getElementById("epaper-editions-data");
    var editions = editionsNode ? JSON.parse(editionsNode.textContent || "[]") : [];
    var currentIndex = 0;
    var zoom = 100;
    var image = document.querySelector("[data-reader-image]");
    var pageFrame = document.querySelector(".page-frame");
    var readerStage = document.querySelector(".reader-stage");
    var title = document.querySelector("[data-reader-title]");
    var section = document.querySelector("[data-reader-section]");
    var currentPageLabels = Array.prototype.slice.call(document.querySelectorAll("[data-reader-current]"));
    var thumbs = Array.prototype.slice.call(document.querySelectorAll(".page-thumb"));
    var zoomRange = document.querySelector("[data-reader-zoom]");
    var cropBox = document.querySelector("[data-crop-box]");
    var cropActions = document.querySelector("[data-crop-actions]");
    var cropCancel = document.querySelector("[data-crop-cancel]");
    var cropSave = document.querySelector("[data-crop-save]");
    var cropButtons = Array.prototype.slice.call(document.querySelectorAll("[data-crop-toggle]"));
    var calendarButtons = Array.prototype.slice.call(document.querySelectorAll("[data-calendar-toggle]"));
    var calendarInputs = Array.prototype.slice.call(document.querySelectorAll("[data-edition-calendar]"));
    var cropMode = false;
    var cropStart = null;
    var cropSelection = null;

    function renderPage(index) {
        if (!pages[index] || !image) {
            return;
        }
        if (cropMode) {
            setCropMode(false);
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
        currentPageLabels.forEach(function (label) {
            label.textContent = String(currentIndex + 1);
        });
    }

    function setZoom(value) {
        zoom = Math.max(70, Math.min(160, value));
        if (zoomRange) {
            zoomRange.value = zoom;
        }
        if (image) {
            image.style.width = zoom === 100 ? "" : zoom + "%";
        }
    }

    function openCalendar() {
        var calendarInput = calendarInputs[0];
        if (!calendarInput) {
            return;
        }
        if (typeof calendarInput.showPicker === "function") {
            calendarInput.showPicker();
        } else {
            calendarInput.focus();
            calendarInput.click();
        }
    }

    function goToEditionDate(dateValue) {
        if (!dateValue) {
            return;
        }
        var matched = editions.find(function (edition) {
            return edition.date === dateValue;
        });
        if (matched && matched.url) {
            window.location.href = matched.url;
            return;
        }
        alert("E-paper is not available for this date.");
    }

    function resetCrop() {
        cropStart = null;
        cropSelection = null;
        if (cropBox) {
            cropBox.classList.remove("is-visible");
            cropBox.removeAttribute("style");
        }
        if (cropActions) {
            cropActions.classList.remove("is-open");
        }
    }

    function setCropMode(enabled) {
        cropMode = enabled;
        resetCrop();
        if (readerStage) {
            readerStage.classList.toggle("is-cropping", cropMode);
        }
        cropButtons.forEach(function (button) {
            button.classList.toggle("is-active", cropMode);
        });
    }

    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function getPointInFrame(event) {
        var frameRect = pageFrame.getBoundingClientRect();
        var imageRect = image.getBoundingClientRect();
        var clientX = event.clientX;
        var clientY = event.clientY;
        var x = clamp(clientX, imageRect.left, imageRect.right);
        var y = clamp(clientY, imageRect.top, imageRect.bottom);
        return {
            frameX: x - frameRect.left + pageFrame.scrollLeft,
            frameY: y - frameRect.top + pageFrame.scrollTop,
            imageX: x - imageRect.left,
            imageY: y - imageRect.top,
            imageRect: imageRect
        };
    }

    function drawCropBox(startPoint, endPoint) {
        if (!cropBox) {
            return;
        }
        var left = Math.min(startPoint.frameX, endPoint.frameX);
        var top = Math.min(startPoint.frameY, endPoint.frameY);
        var width = Math.abs(endPoint.frameX - startPoint.frameX);
        var height = Math.abs(endPoint.frameY - startPoint.frameY);
        cropBox.style.left = left + "px";
        cropBox.style.top = top + "px";
        cropBox.style.width = width + "px";
        cropBox.style.height = height + "px";
        cropBox.classList.add("is-visible");
    }

    function saveCrop() {
        if (!cropSelection || !image || cropSelection.width < 12 || cropSelection.height < 12) {
            alert("Please select a news clip first.");
            return;
        }

        var canvas = document.createElement("canvas");
        var scaleX = image.naturalWidth / cropSelection.imageRect.width;
        var scaleY = image.naturalHeight / cropSelection.imageRect.height;
        var sx = Math.round(cropSelection.left * scaleX);
        var sy = Math.round(cropSelection.top * scaleY);
        var sw = Math.round(cropSelection.width * scaleX);
        var sh = Math.round(cropSelection.height * scaleY);
        canvas.width = sw;
        canvas.height = sh;
        canvas.getContext("2d").drawImage(image, sx, sy, sw, sh, 0, 0, sw, sh);

        canvas.toBlob(function (blob) {
            if (!blob) {
                return;
            }
            var fileName = "aaj-ka-mudda-clip-page-" + (currentIndex + 1) + ".jpg";
            var url = URL.createObjectURL(blob);
            var link = document.createElement("a");
            link.href = url;
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(url);
            setCropMode(false);
        }, "image/jpeg", 0.92);
    }

    thumbs.forEach(function (thumb) {
        thumb.addEventListener("click", function () {
            renderPage(Number(thumb.dataset.pageIndex || 0));
        });
    });

    var prevButtons = Array.prototype.slice.call(document.querySelectorAll("[data-reader-prev]"));
    var nextButtons = Array.prototype.slice.call(document.querySelectorAll("[data-reader-next]"));
    var zoomIn = document.querySelector("[data-reader-zoom-in]");
    var zoomOut = document.querySelector("[data-reader-zoom-out]");
    var fitButtons = Array.prototype.slice.call(document.querySelectorAll("[data-reader-fit]"));
    var shareButtons = Array.prototype.slice.call(document.querySelectorAll("[data-share-url]"));
    var allPagesButton = document.querySelector("[data-all-pages]");
    var pageRail = document.querySelector(".page-rail");
    var editionSelects = Array.prototype.slice.call(document.querySelectorAll("[data-edition-select]"));

    prevButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            renderPage((currentIndex - 1 + pages.length) % pages.length);
        });
    });
    nextButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            renderPage((currentIndex + 1) % pages.length);
        });
    });
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
    fitButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            setZoom(100);
        });
    });

    cropButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            setCropMode(!cropMode);
        });
    });

    if (cropCancel) {
        cropCancel.addEventListener("click", function () {
            setCropMode(false);
        });
    }

    if (cropSave) {
        cropSave.addEventListener("click", saveCrop);
    }

    if (pageFrame && image) {
        pageFrame.addEventListener("pointerdown", function (event) {
            if (!cropMode || !image.complete) {
                return;
            }
            event.preventDefault();
            pageFrame.setPointerCapture(event.pointerId);
            cropStart = getPointInFrame(event);
            cropSelection = null;
            drawCropBox(cropStart, cropStart);
        });

        pageFrame.addEventListener("pointermove", function (event) {
            if (!cropMode || !cropStart) {
                return;
            }
            event.preventDefault();
            drawCropBox(cropStart, getPointInFrame(event));
        });

        pageFrame.addEventListener("pointerup", function (event) {
            if (!cropMode || !cropStart) {
                return;
            }
            event.preventDefault();
            var endPoint = getPointInFrame(event);
            var left = Math.min(cropStart.imageX, endPoint.imageX);
            var top = Math.min(cropStart.imageY, endPoint.imageY);
            var width = Math.abs(endPoint.imageX - cropStart.imageX);
            var height = Math.abs(endPoint.imageY - cropStart.imageY);
            cropSelection = {
                left: left,
                top: top,
                width: width,
                height: height,
                imageRect: endPoint.imageRect
            };
            cropStart = null;
            if (cropActions) {
                cropActions.classList.toggle("is-open", width >= 12 && height >= 12);
            }
        });
    }

    if (allPagesButton && pageRail) {
        allPagesButton.addEventListener("click", function () {
            pageRail.classList.toggle("is-open");
        });

        thumbs.forEach(function (thumb) {
            thumb.addEventListener("click", function () {
                pageRail.classList.remove("is-open");
            });
        });
    }

    editionSelects.forEach(function (editionSelect) {
        editionSelect.addEventListener("change", function () {
            if (editionSelect.value) {
                window.location.href = editionSelect.value;
            }
        });
    });

    calendarButtons.forEach(function (calendarButton) {
        calendarButton.addEventListener("click", openCalendar);
    });

    calendarInputs.forEach(function (calendarInput) {
        calendarInput.addEventListener("change", function () {
            goToEditionDate(calendarInput.value);
        });
    });

    shareButtons.forEach(function (shareButton) {
        shareButton.addEventListener("click", function () {
            var shareData = {
                title: shareButton.dataset.shareTitle || document.title,
                text: shareButton.dataset.shareText || "",
                url: shareButton.dataset.shareUrl || window.location.href
            };

            if (navigator.share) {
                navigator.share(shareData).catch(function () {});
                return;
            }

            if (navigator.clipboard) {
                navigator.clipboard.writeText(shareData.url).then(function () {
                    var oldText = shareButton.textContent;
                    shareButton.textContent = "Copied";
                    window.setTimeout(function () {
                        shareButton.textContent = oldText;
                    }, 1600);
                });
            }
        });
    });
})();
