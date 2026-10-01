document.addEventListener("DOMContentLoaded", () => {
    const menuToggle = document.querySelector(".menu-toggle");
    const navigation = document.querySelector("#primary-navigation");

    const closeMenu = () => {
        if (!menuToggle || !navigation) {
            return;
        }
        menuToggle.setAttribute("aria-expanded", "false");
        navigation.classList.remove("is-open");
    };

    if (menuToggle && navigation) {
        menuToggle.addEventListener("click", () => {
            const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
            menuToggle.setAttribute("aria-expanded", String(!isOpen));
            navigation.classList.toggle("is-open", !isOpen);
        });

        navigation.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", closeMenu);
        });
    }

    const mypageMenu = document.querySelector("[data-mypage-menu]");
    const mypageMenuToggle = document.querySelector("[data-mypage-menu-toggle]");

    const closeMypageMenu = (restoreFocus = false) => {
        if (!mypageMenu || !mypageMenuToggle) {
            return;
        }
        mypageMenu.hidden = true;
        mypageMenuToggle.setAttribute("aria-expanded", "false");
        if (restoreFocus) {
            mypageMenuToggle.focus();
        }
    };

    if (mypageMenu && mypageMenuToggle) {
        mypageMenuToggle.addEventListener("click", () => {
            const willOpen = mypageMenuToggle.getAttribute("aria-expanded") !== "true";
            mypageMenu.hidden = !willOpen;
            mypageMenuToggle.setAttribute("aria-expanded", String(willOpen));
        });

        mypageMenu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => closeMypageMenu());
        });

        document.addEventListener("click", (event) => {
            if (!event.target.closest(".mypage-menu")) {
                closeMypageMenu();
            }
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            const mobileMenuWasOpen =
                menuToggle?.getAttribute("aria-expanded") === "true";
            const mypageMenuWasOpen =
                mypageMenuToggle?.getAttribute("aria-expanded") === "true";
            closeMenu();
            closeMypageMenu(mypageMenuWasOpen);
            if (mobileMenuWasOpen) {
                menuToggle.focus();
            }
        }
    });
});
