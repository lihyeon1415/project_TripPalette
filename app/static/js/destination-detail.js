document.addEventListener("DOMContentLoaded", () => {
    const galleryItems = Array.from(
        document.querySelectorAll(".destination-gallery__item"),
    );
    const lightbox = document.querySelector(".destination-lightbox");

    if (!galleryItems.length || !lightbox) {
        return;
    }

    const lightboxImage = lightbox.querySelector(".destination-lightbox__image");
    const lightboxPanel = lightbox.querySelector(".destination-lightbox__panel");
    const lightboxCaption = lightbox.querySelector(".destination-lightbox__caption");
    const lightboxCounter = lightbox.querySelector(".destination-lightbox__counter");
    const closeButton = lightbox.querySelector(".destination-lightbox__close");
    const previousButton = lightbox.querySelector(".destination-lightbox__nav--prev");
    const nextButton = lightbox.querySelector(".destination-lightbox__nav--next");
    let currentIndex = 0;
    let lastFocusedElement = null;

    const showImage = (index) => {
        currentIndex = (index + galleryItems.length) % galleryItems.length;
        const item = galleryItems[currentIndex];
        const source = item.dataset.gallerySrc;
        const alt = item.dataset.galleryAlt || "여행지 사진";

        lightboxImage.src = source;
        lightboxImage.alt = alt;
        lightboxCaption.textContent = alt;
        lightboxCounter.textContent = `${currentIndex + 1} / ${galleryItems.length}`;
    };

    const openLightbox = (index) => {
        lastFocusedElement = document.activeElement;
        showImage(index);
        lightbox.showModal();
        document.body.classList.add("destination-lightbox-open");
        closeButton.focus();
    };

    const closeLightbox = () => {
        if (!lightbox.open) {
            return;
        }

        lightbox.close();
        document.body.classList.remove("destination-lightbox-open");
        lightboxImage.src = "";

        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
    };

    galleryItems.forEach((item, index) => {
        item.addEventListener("click", () => openLightbox(index));
    });

    closeButton.addEventListener("click", closeLightbox);
    previousButton.addEventListener("click", () => showImage(currentIndex - 1));
    nextButton.addEventListener("click", () => showImage(currentIndex + 1));

    lightbox.addEventListener("click", (event) => {
        if (event.target === lightbox || event.target === lightboxPanel) {
            closeLightbox();
        }
    });

    lightbox.addEventListener("cancel", (event) => {
        event.preventDefault();
        closeLightbox();
    });

    document.addEventListener("keydown", (event) => {
        if (!lightbox.open) {
            return;
        }

        if (event.key === "ArrowLeft") {
            showImage(currentIndex - 1);
        } else if (event.key === "ArrowRight") {
            showImage(currentIndex + 1);
        }
    });

    if (galleryItems.length < 2) {
        previousButton.hidden = true;
        nextButton.hidden = true;
    }
});
