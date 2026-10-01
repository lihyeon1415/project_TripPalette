document.addEventListener("DOMContentLoaded", () => {
    const authPage = document.querySelector(".palette-auth-page");
    if (authPage) {
        window.requestAnimationFrame(() => {
            authPage.classList.add("is-copy-visible");
        });

        window.setTimeout(() => {
            authPage.classList.add("is-card-stack-visible");
        }, 650);

        window.setTimeout(() => {
            authPage.classList.add("is-cards-open");
        }, 1050);
    }

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        const input = document.getElementById(button.dataset.passwordToggle);
        if (!input) return;

        button.addEventListener("click", () => {
            const isVisible = input.type === "text";
            input.type = isVisible ? "password" : "text";
            button.classList.toggle("is-visible", !isVisible);
            button.setAttribute("aria-label", isVisible ? "비밀번호 보기" : "비밀번호 숨기기");
        });
    });

    const allTerms = document.querySelector("[data-terms-all]");
    const termItems = [...document.querySelectorAll("[data-terms-item]")];
    if (allTerms && termItems.length) {
        const syncAllTerms = () => {
            allTerms.checked = termItems.every((term) => term.checked);
            allTerms.indeterminate = !allTerms.checked && termItems.some((term) => term.checked);
        };

        allTerms.addEventListener("change", () => {
            termItems.forEach((item) => {
                item.checked = allTerms.checked;
            });
            allTerms.indeterminate = false;
        });

        termItems.forEach((item) => {
            item.addEventListener("change", syncAllTerms);
        });
    }

    const termsDialog = document.querySelector("[data-terms-dialog]");
    if (!termsDialog) return;

    const dialogTitle = termsDialog.querySelector("[data-terms-title]");
    const dialogContent = termsDialog.querySelector("[data-terms-content]");

    document.querySelectorAll("[data-terms-open]").forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            const template = document.getElementById(button.dataset.termsOpen);
            if (!template || !dialogContent) return;

            dialogTitle.textContent = button.dataset.termsOpen === "service-terms"
                ? "이용약관"
                : "개인정보 수집 및 이용";
            dialogContent.replaceChildren(template.content.cloneNode(true));
            termsDialog.showModal();
        });
    });

    termsDialog.querySelectorAll("[data-terms-close]").forEach((button) => {
        button.addEventListener("click", () => termsDialog.close());
    });

    termsDialog.addEventListener("click", (event) => {
        if (event.target === termsDialog) termsDialog.close();
    });
});
