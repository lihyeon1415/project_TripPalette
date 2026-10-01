document.addEventListener("DOMContentLoaded", () => {
    const carousel = document.querySelector("[data-hero-carousel]");

    if (!carousel) {
        return;
    }

    const track = carousel.querySelector("[data-hero-track]");
    const slides = Array.from(track.children);
    const dots = Array.from(carousel.querySelectorAll("[data-hero-dot]"));
    const previousButton = carousel.querySelector("[data-hero-prev]");
    const nextButton = carousel.querySelector("[data-hero-next]");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const intervalMilliseconds = 3000;
    let currentIndex = 0;
    let physicalIndex = 1;
    let timerId = null;
    let isAnimating = false;

    if (slides.length < 2) {
        carousel.querySelector(".hero__controls")?.setAttribute("hidden", "");
        return;
    }

    const firstClone = slides[0].cloneNode(true);
    const lastClone = slides[slides.length - 1].cloneNode(true);
    firstClone.setAttribute("aria-hidden", "true");
    lastClone.setAttribute("aria-hidden", "true");
    firstClone.dataset.heroClone = "first";
    lastClone.dataset.heroClone = "last";
    track.append(firstClone);
    track.prepend(lastClone);

    const updateControls = () => {
        slides.forEach((slide, slideIndex) => {
            slide.setAttribute("aria-hidden", String(slideIndex !== currentIndex));
        });

        firstClone.setAttribute("aria-hidden", "true");
        lastClone.setAttribute("aria-hidden", "true");

        dots.forEach((dot, dotIndex) => {
            const isCurrent = dotIndex === currentIndex;
            dot.classList.toggle("is-active", isCurrent);
            dot.toggleAttribute("aria-current", isCurrent);
        });
    };

    const setTrackPosition = (index, animate = true) => {
        if (!animate || reduceMotion.matches) {
            track.style.transition = "none";
        }
        track.style.transform = `translateX(-${index * 100}%)`;

        if (!animate || reduceMotion.matches) {
            track.getBoundingClientRect();
            track.style.transition = "";
        }
    };

    const normalizeClonePosition = () => {
        if (physicalIndex === 0) {
            physicalIndex = slides.length;
            setTrackPosition(physicalIndex, false);
        } else if (physicalIndex === slides.length + 1) {
            physicalIndex = 1;
            setTrackPosition(physicalIndex, false);
        }
        isAnimating = false;
    };

    const moveBy = (direction) => {
        if (isAnimating) {
            return;
        }

        isAnimating = true;
        currentIndex =
            (currentIndex + direction + slides.length) % slides.length;
        physicalIndex += direction;
        updateControls();
        setTrackPosition(physicalIndex);

        if (reduceMotion.matches) {
            normalizeClonePosition();
        }
    };

    const showSlide = (index) => {
        if (isAnimating) {
            return;
        }

        const nextIndex = (index + slides.length) % slides.length;
        if (nextIndex === currentIndex) {
            return;
        }

        isAnimating = true;
        currentIndex = nextIndex;
        physicalIndex = currentIndex + 1;
        updateControls();
        setTrackPosition(physicalIndex);

        if (reduceMotion.matches) {
            normalizeClonePosition();
        }
    };

    const stopAutoplay = () => {
        if (timerId !== null) {
            window.clearInterval(timerId);
            timerId = null;
        }
    };

    const startAutoplay = () => {
        stopAutoplay();

        if (!reduceMotion.matches && !document.hidden) {
            timerId = window.setInterval(() => moveBy(1), intervalMilliseconds);
        }
    };

    const selectSlide = (index) => {
        showSlide(index);
        startAutoplay();
    };

    previousButton.addEventListener("click", () => {
        moveBy(-1);
        startAutoplay();
    });
    nextButton.addEventListener("click", () => {
        moveBy(1);
        startAutoplay();
    });
    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => selectSlide(index));
    });

    track.addEventListener("transitionend", (event) => {
        if (event.propertyName === "transform") {
            normalizeClonePosition();
        }
    });

    carousel.addEventListener("mouseenter", stopAutoplay);
    carousel.addEventListener("mouseleave", startAutoplay);
    carousel.addEventListener("focusin", stopAutoplay);
    carousel.addEventListener("focusout", (event) => {
        if (!carousel.contains(event.relatedTarget)) {
            startAutoplay();
        }
    });
    document.addEventListener("visibilitychange", startAutoplay);
    reduceMotion.addEventListener("change", () => {
        normalizeClonePosition();
        startAutoplay();
    });

    updateControls();
    setTrackPosition(physicalIndex, false);
    startAutoplay();
});

document.addEventListener("DOMContentLoaded", () => {
    const initializeTabs = ({
        tabSelector,
        panelSelector,
        tabDataKey,
        panelDataKey,
    }) => {
        const tabs = Array.from(document.querySelectorAll(tabSelector));
        const panels = Array.from(document.querySelectorAll(panelSelector));

        if (!tabs.length || !panels.length) {
            return;
        }

        const activate = (key, focusTab = false) => {
            tabs.forEach((tab) => {
                const isActive = tab.dataset[tabDataKey] === key;
                tab.classList.toggle("is-active", isActive);
                tab.setAttribute("aria-selected", String(isActive));
                tab.tabIndex = isActive ? 0 : -1;

                if (isActive && focusTab) {
                    tab.focus();
                }
            });

            panels.forEach((panel) => {
                const isActive = panel.dataset[panelDataKey] === key;
                panel.hidden = !isActive;
                panel.classList.remove("is-entering");

                if (isActive) {
                    window.requestAnimationFrame(() => {
                        panel.classList.add("is-entering");
                    });
                }
            });
        };

        tabs.forEach((tab, index) => {
            tab.addEventListener("click", () => {
                activate(tab.dataset[tabDataKey]);
            });

            tab.addEventListener("keydown", (event) => {
                let nextIndex = null;

                if (event.key === "ArrowRight" || event.key === "ArrowDown") {
                    nextIndex = (index + 1) % tabs.length;
                } else if (
                    event.key === "ArrowLeft"
                    || event.key === "ArrowUp"
                ) {
                    nextIndex = (index - 1 + tabs.length) % tabs.length;
                } else if (event.key === "Home") {
                    nextIndex = 0;
                } else if (event.key === "End") {
                    nextIndex = tabs.length - 1;
                }

                if (nextIndex !== null) {
                    event.preventDefault();
                    activate(tabs[nextIndex].dataset[tabDataKey], true);
                }
            });
        });

        const initialTab =
            tabs.find((tab) => tab.getAttribute("aria-selected") === "true")
            || tabs[0];
        activate(initialTab.dataset[tabDataKey]);
    };

    initializeTabs({
        tabSelector: "[data-region-tab]",
        panelSelector: "[data-region-panel]",
        tabDataKey: "regionTab",
        panelDataKey: "regionPanel",
    });

    initializeTabs({
        tabSelector: "[data-companion-tab]",
        panelSelector: "[data-companion-panel]",
        tabDataKey: "companionTab",
        panelDataKey: "companionPanel",
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const revealGroups = [
        {
            section: ".popular-section",
            targets: [".section-heading", ".destination-card"],
        },
        {
            section: ".regional-section",
            targets: [".section-heading", ".regional-content"],
        },
        {
            section: ".companion-section",
            targets: [".section-heading", ".companion-layout"],
        },
        {
            section: ".fall-section",
            targets: [".fall-section__content"],
        },
        {
            section: ".taste-section",
            targets: [".section-heading", ".taste-card"],
        },
        {
            section: ".recommendation-cta",
            targets: [".recommendation-cta__inner > div"],
        },
    ];
    const revealItems = [];

    revealGroups.forEach(({ section, targets }) => {
        const sectionElement = document.querySelector(section);

        if (!sectionElement) {
            return;
        }

        let itemIndex = 0;
        targets.forEach((selector) => {
            sectionElement.querySelectorAll(selector).forEach((item) => {
                item.classList.add("main-scroll-reveal");
                item.style.setProperty(
                    "--reveal-delay",
                    `${Math.min(itemIndex * 70, 280)}ms`,
                );
                revealItems.push(item);
                itemIndex += 1;
            });
        });
    });

    if (!revealItems.length) {
        return;
    }

    const revealAll = () => {
        revealItems.forEach((item) => item.classList.add("is-revealed"));
    };

    if (reduceMotion.matches || !("IntersectionObserver" in window)) {
        revealAll();
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                entry.target.classList.add("is-revealed");
                observer.unobserve(entry.target);
            });
        },
        {
            threshold: 0.12,
            rootMargin: "0px 0px -10% 0px",
        },
    );

    revealItems.forEach((item) => {
        if (item.getBoundingClientRect().bottom < 0) {
            item.classList.add("is-revealed");
        } else {
            observer.observe(item);
        }
    });
});
