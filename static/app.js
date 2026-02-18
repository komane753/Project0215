
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".share-btn").forEach(btn => {
        btn.addEventListener("click", () => {

            const title = btn.getAttribute("data-title");
            const videoId = btn.getAttribute("data-id");

            const hashtags = "#炎上 #YouTube #話題";

            const tweetText = `
🔥 ${title}

炎上度チェック結果はこちら👇
https://www.youtube.com/watch?v=${videoId}

${hashtags}
            `;

            const encodedText = encodeURIComponent(tweetText);

            window.open(
                `https://twitter.com/intent/tweet?text=${encodedText}`,
                "_blank",
                "noopener"
            );
        });
    });
});
