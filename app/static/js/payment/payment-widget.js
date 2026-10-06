(() => {
    const frames = document.querySelectorAll("[data-payment-widget]");
    if (!frames.length || typeof TossPayments !== "function") return;

    frames.forEach((frame) => {
        const method = frame.querySelector("[data-payment-method]");
        const agreement = frame.querySelector("[data-payment-agreement]");
        const button = frame.querySelector("[data-payment-submit]");
        const errorBox = frame.querySelector("[data-payment-error]");
        const amount = Number(frame.dataset.amount);

        if (!method || !agreement || !button || !errorBox || !Number.isFinite(amount)) return;

        const showError = (error, fallback) => {
            errorBox.textContent = error?.message || fallback;
            errorBox.hidden = false;
        };

        const tossPayments = TossPayments(frame.dataset.clientKey);
        const widgets = tossPayments.widgets({ customerKey: frame.dataset.customerKey });

        button.addEventListener("click", async () => {
            button.disabled = true;
            errorBox.hidden = true;
            try {
                const paymentRequest = {
                    orderId: frame.dataset.orderId,
                    orderName: frame.dataset.orderName,
                    successUrl: frame.dataset.successUrl,
                    failUrl: frame.dataset.failUrl,
                    customerEmail: frame.dataset.customerEmail,
                    customerName: frame.dataset.customerName,
                };
                if (!window.matchMedia("(max-width: 767px)").matches) {
                    paymentRequest.windowTarget = "iframe";
                }
                await widgets.requestPayment(paymentRequest);
            } catch (error) {
                showError(error, "결제창을 열지 못했습니다.");
                button.disabled = false;
            }
        });

        widgets.setAmount({ currency: "KRW", value: amount })
            .then(() => Promise.all([
                widgets.renderPaymentMethods({ selector: `#${method.id}`, variantKey: "DEFAULT" }),
                widgets.renderAgreement({ selector: `#${agreement.id}`, variantKey: "AGREEMENT" }),
            ]))
            .catch((error) => {
                showError(error, "결제수단을 불러오지 못했습니다.");
                button.disabled = true;
            });
    });
})();
