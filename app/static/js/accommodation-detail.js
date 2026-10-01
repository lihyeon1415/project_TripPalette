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

    thumbnails.forEach((thumbnail) => {
        thumbnail.addEventListener("click", () => {
            const source = thumbnail.dataset.gallerySrc;
            if (!source || mainImage.getAttribute("src") === source) {
                return;
            }

            mainImage.src = source;
            mainImage.alt = thumbnail.dataset.galleryAlt || "숙소 전경";
            mainImage.hidden = false;

            thumbnails.forEach((item) => {
                const selected = item === thumbnail;
                item.classList.toggle("is-active", selected);
                item.setAttribute("aria-pressed", String(selected));
            });
        });
    });

    if (!viewport || !previousButton || !nextButton) {
        return;
    }

    const updateArrowState = () => {
        const maximumScroll = viewport.scrollWidth - viewport.clientWidth;
        previousButton.disabled = viewport.scrollLeft <= 2;
        nextButton.disabled = viewport.scrollLeft >= maximumScroll - 2;
    };

    previousButton.addEventListener("click", () => {
        viewport.scrollBy({ left: -viewport.clientWidth, behavior: "smooth" });
    });

    nextButton.addEventListener("click", () => {
        viewport.scrollBy({ left: viewport.clientWidth, behavior: "smooth" });
    });

    viewport.addEventListener("scroll", updateArrowState, { passive: true });
    window.addEventListener("resize", updateArrowState);
    updateArrowState();
});
