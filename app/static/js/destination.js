document.addEventListener("DOMContentLoaded", () => {
    const filterForm = document.querySelector(".destination-filter");
    const resetLink = document.querySelector(".destination-filter a");

    // 검색어가 비어 있을 때 검색 방지
    if (filterForm) {
        filterForm.addEventListener("submit", (event) => {
            const keywordInput = document.querySelector("#keyword");

            if (keywordInput && keywordInput.value.trim() === "") {
                keywordInput.value = "";
            }
        });
    }

    // 필터 초기화
    if (resetLink) {
        resetLink.addEventListener("click", () => {
            // GET 방식의 초기화 링크를 그대로 사용
            window.location.href = resetLink.href;
        });
    }
});