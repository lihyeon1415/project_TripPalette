(() => {
    const page = document.querySelector(".pally-detail");
    if (!page) return;

    const productPrice = Number(page.dataset.productPrice || 0);
    const shippingFee = Number(page.dataset.shippingFee || 0);
    const quantityOutput = page.querySelector("[data-quantity-output]");
    const modal = page.querySelector("[data-buy-modal]");
    const modalQuantity = page.querySelector("[data-modal-quantity]");
    const productTotal = page.querySelector("[data-product-total]");
    const modalTotal = page.querySelector("[data-modal-total]");
    const formatWon = (value) => `${new Intl.NumberFormat("ko-KR").format(value)}원`;

    let quantity = Math.min(10, Math.max(1, Number(modalQuantity?.value || 1)));

    function updateQuantity(nextQuantity) {
        quantity = Math.min(10, Math.max(1, Number(nextQuantity) || 1));
        if (quantityOutput) quantityOutput.textContent = String(quantity);
        if (modalQuantity) modalQuantity.value = String(quantity);
        if (productTotal) productTotal.textContent = formatWon(productPrice * quantity);
        if (modalTotal) modalTotal.textContent = formatWon(productPrice * quantity + shippingFee);
    }

    page.querySelector("[data-quantity-minus]")?.addEventListener("click", () => {
        updateQuantity(quantity - 1);
    });
    page.querySelector("[data-quantity-plus]")?.addEventListener("click", () => {
        updateQuantity(quantity + 1);
    });
    modalQuantity?.addEventListener("input", () => updateQuantity(modalQuantity.value));

    function openModal(event) {
        event?.preventDefault();
        if (!modal) return;
        updateQuantity(quantity);
        if (typeof modal.showModal === "function") modal.showModal();
        else modal.setAttribute("open", "");
    }

    function closeModal() {
        if (!modal) return;
        if (typeof modal.close === "function") modal.close();
        else modal.removeAttribute("open");
    }

    page.querySelectorAll("[data-buy-modal-open]").forEach((button) => {
        button.addEventListener("click", openModal);
    });
    page.querySelectorAll("[data-buy-modal-close]").forEach((button) => {
        button.addEventListener("click", closeModal);
    });
    modal?.addEventListener("click", (event) => {
        const bounds = modal.getBoundingClientRect();
        const outside = event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom;
        if (outside) closeModal();
    });

    const mainImage = page.querySelector("#pally-product-image");
    page.querySelectorAll("[data-product-thumbnail]").forEach((thumbnail) => {
        thumbnail.addEventListener("click", () => {
            if (mainImage) mainImage.src = thumbnail.dataset.imageSrc;
            page.querySelectorAll("[data-product-thumbnail]").forEach((item) => {
                const active = item === thumbnail;
                item.classList.toggle("is-active", active);
                item.setAttribute("aria-pressed", String(active));
            });
        });
    });

    updateQuantity(quantity);
    if (modal?.dataset.autoOpen === "true") openModal();
})();
