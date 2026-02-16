console.log("APP JS NEW VERSION");

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".share-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const title = this.dataset.title;
            const videoId = this.dataset.id;
            shareToX(title, videoId);
        });
    });
});

function shareToX(title, videoId) {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=https://www.youtube.com/watch?v=${videoId}`;
    window.open(url, "_blank");
}
