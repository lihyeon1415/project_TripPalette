(() => {
    const page = document.querySelector("[data-cart-page]");
    if (!page) return;

    const itemChecks = [...page.querySelectorAll("[data-cart-select]")];
    const selectAll = page.querySelector("[data-cart-select-all]");
    const checkoutButton = page.querySelector("[data-checkout-open]");
    const shippingFee = Number(page.dataset.shippingFee || 0);
    const won = (amount) => `${new Intl.NumberFormat("ko-KR").format(amount)}원`;

    function selectedItems() {
        return itemChecks.filter((check) => check.checked).map((check) => check.closest("[data-cart-item]"));
    }

    function refreshSummary() {
        const selected = selectedItems();
        const amount = selected.reduce((sum, item) => sum + Number(item.dataset.itemPrice) * Number(item.dataset.itemQuantity), 0);
        const delivery = selected.length ? shippingFee : 0;
        page.querySelector("[data-selected-count]").textContent = String(selected.length);
        page.querySelector("[data-selected-amount]").textContent = won(amount);
        page.querySelector("[data-shipping-amount]").textContent = won(delivery);
        page.querySelector("[data-selected-total]").textContent = won(amount + delivery);
        const dialogTotal = page.querySelector("[data-shipping-total]");
        if (dialogTotal) dialogTotal.textContent = won(amount + delivery);
        if (checkoutButton) checkoutButton.disabled = selected.length === 0;
        if (selectAll) {
            selectAll.checked = itemChecks.length > 0 && selected.length === itemChecks.length;
            selectAll.indeterminate = selected.length > 0 && selected.length < itemChecks.length;
        }
    }

    selectAll?.addEventListener("change", () => {
        itemChecks.forEach((check) => { check.checked = selectAll.checked; });
        refreshSummary();
    });
    itemChecks.forEach((check) => check.addEventListener("change", refreshSummary));

    page.querySelector("[data-delete-selected]")?.addEventListener("submit", (event) => {
        const form = event.currentTarget;
        form.querySelectorAll('input[name="cart_item_ids"]').forEach((input) => input.remove());
        const selected = itemChecks.filter((check) => check.checked);
        if (!selected.length) {
            event.preventDefault();
            return;
        }
        selected.forEach((check) => {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "cart_item_ids";
            input.value = check.value;
            form.append(input);
        });
    });

    page.querySelectorAll("[data-quantity-form]").forEach((form) => {
        const input = form.querySelector('input[name="quantity"]');
        form.querySelector("[data-quantity-minus]")?.addEventListener("click", () => {
            input.value = String(Math.max(Number(input.min), Number(input.value) - 1));
            form.submit();
        });
        form.querySelector("[data-quantity-plus]")?.addEventListener("click", () => {
            input.value = String(Math.min(Number(input.max), Number(input.value) + 1));
            form.submit();
        });
    });

    refreshSummary();
})();
