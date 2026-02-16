console.log("APP JS SAFE VERSION");

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".share-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const title = btn.getAttribute("data-title");
            const videoId = btn.getAttribute("data-id");

            const text = encodeURIComponent(title);
            const url = encodeURIComponent(`https://www.youtube.com/watch?v=${videoId}`);

            window.open(
                `https://twitter.com/intent/tweet?text=${text}&url=${url}`,
                "_blank",
                "noopener"
            );
        });
    });
});