(() => {
    const dialogs = [...document.querySelectorAll("[data-shipping-dialog]")];
    if (!dialogs.length) return;

    const openDialog = (dialog) => {
        if (!dialog || dialog.open) return;
        dialog.dispatchEvent(new CustomEvent("shipping-dialog:beforeopen"));
        if (typeof dialog.showModal === "function") dialog.showModal();
        else dialog.setAttribute("open", "");
    };

    const closeDialog = (dialog) => {
        if (!dialog) return;
        if (typeof dialog.close === "function") dialog.close();
        else dialog.removeAttribute("open");
    };

    document.querySelectorAll("[data-shipping-open]").forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            const selector = button.dataset.shippingOpen;
            openDialog(selector ? document.querySelector(selector) : dialogs[0]);
        });
    });

    dialogs.forEach((dialog) => {
        dialog.querySelector("[data-shipping-close]")?.addEventListener("click", () => closeDialog(dialog));
        dialog.addEventListener("click", (event) => {
            const bounds = dialog.getBoundingClientRect();
            if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) closeDialog(dialog);
        });
        if (dialog.dataset.autoOpen === "true") openDialog(dialog);
    });
})();
