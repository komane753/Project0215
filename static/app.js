function shareToX(title, videoId) {

    const text = `この動画の炎上度をチェックしました🔥\n${title}`;
    const url = `https://www.youtube.com/watch?v=${videoId}`;

    const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;

    window.open(shareUrl, "_blank", "noopener,noreferrer");
}

document.addEventListener("DOMContentLoaded", function () {
    const gauges = document.querySelectorAll(".gauge-fill");

    gauges.forEach(gauge => {
        const width = gauge.dataset.width;
        const color = gauge.dataset.color;

        gauge.style.width = width + "%";
        gauge.style.background = color;
    });
});