document.addEventListener("DOMContentLoaded", () => {
    const gallery = document.querySelector("[data-accommodation-gallery]");

    if (!gallery) {
        return;
    }

    const mainImage = gallery.querySelector("[data-accommodation-main-image]");
    const thumbnails = Array.from(
        gallery.querySelectorAll("[data-accommodation-thumbnail]"),
    );
    const viewport = gallery.querySelector("[data-gallery-viewport]");
    const previousButton = gallery.querySelector("[data-gallery-previous]");
    const nextButton = gallery.querySelector("[data-gallery-next]");

    if (!mainImage || !thumbnails.length) {
        return;
    }

    let currentIndex = Math.max(
        thumbnails.findIndex((thumbnail) => thumbnail.classList.contains("is-active")),
        0,
    );

    const showImage = (index) => {
        currentIndex = (index + thumbnails.length) % thumbnails.length;
        const thumbnail = thumbnails[currentIndex];
        const source = thumbnail.dataset.gallerySrc;

        if (!source) {
            return;
        }

        mainImage.src = source;
        mainImage.alt = thumbnail.dataset.galleryAlt || "숙소 전경";
        mainImage.hidden = false;

        thumbnails.forEach((item, itemIndex) => {
            const selected = itemIndex === currentIndex;
            item.classList.toggle("is-active", selected);
            item.setAttribute("aria-pressed", String(selected));
        });

        if (viewport) {
            const targetLeft = thumbnail.offsetLeft
                - (viewport.clientWidth - thumbnail.offsetWidth) / 2;
            viewport.scrollTo({ left: targetLeft, behavior: "smooth" });
        }
    };

    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener("click", () => showImage(index));
    });

    if (!previousButton || !nextButton) {
        return;
    }

    previousButton.addEventListener("click", () => showImage(currentIndex - 1));
    nextButton.addEventListener("click", () => showImage(currentIndex + 1));
});
