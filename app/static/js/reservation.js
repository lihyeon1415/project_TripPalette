(function () {
    "use strict";

    const form = document.querySelector("[data-reservation-form]");
    if (!form) return;

    const checkIn = form.querySelector("[data-check-in]");
    const checkOut = form.querySelector("[data-check-out]");
    const nightCount = form.querySelector("[data-night-count]");
    const totalPrice = form.querySelector("[data-total-price]");
    const nightlyPrice = Number(form.dataset.nightlyPrice || 0);

    function updateEstimate() {
        if (!checkIn.value || !checkOut.value) return;

        checkOut.min = checkIn.value;
        const start = new Date(`${checkIn.value}T00:00:00`);
        const end = new Date(`${checkOut.value}T00:00:00`);
        const nights = Math.round((end - start) / 86400000);

        if (nights < 1) {
            nightCount.textContent = "날짜 확인";
            totalPrice.textContent = "–";
            return;
        }

        nightCount.textContent = `${nights}박`;
        totalPrice.textContent = `₩ ${(nightlyPrice * nights).toLocaleString("ko-KR")}`;
    }

    checkIn.addEventListener("change", updateEstimate);
    checkOut.addEventListener("change", updateEstimate);
    updateEstimate();
})();
