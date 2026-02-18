from flask import Flask, render_template, request
from googleapiclient.discovery import build
import math
import os
import re
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# =========================
# 環境変数
# =========================
API_KEY = os.getenv("YOUTUBE_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY が設定されていません")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL が設定されていません")

# =========================
# DB接続
# =========================
def get_connection():
    return psycopg2.connect(DATABASE_URL)

# =========================
# DB初期化
# =========================
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rankings (
            video_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            fire_score REAL NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# =========================
# ネガティブワード
# =========================
NEGATIVE_WORDS = [ 
    # 強い炎上系 
    "炎上", "謝罪", "最低", "最悪", "終わり", "引退", "許さない", 
    "許せない", "ひどい", "酷い", "ありえない", "あり得ない", "失望", 
    "がっかり", "裏切り", "嘘", "詐欺", "犯罪", "違法",
]

# =========================
# URL検証
# =========================
def is_valid_youtube_url(url):
    parsed = urlparse(url)
    return parsed.netloc in ["www.youtube.com", "youtube.com", "youtu.be"]

# =========================
# 動画ID抽出
# =========================
def extract_video_id(url):
    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# =========================
# YouTube API
# =========================
def get_youtube_comments(video_id, max_comments=300):
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        comments = []
        next_page_token = None

        while True:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                order="time"
            )
            response = request.execute()

            for item in response["items"]:
                text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(text)

                if len(comments) >= max_comments:
                    break

            if len(comments) >= max_comments:
                break

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return comments

    except Exception as e:
        print("YouTube API Error:", e)
        return []

def get_video_title(video_id):
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()

        if response["items"]:
            return response["items"][0]["snippet"]["title"]
        return "タイトル取得失敗"
    except:
        return "タイトル取得失敗"

# =========================
# 分析処理
# =========================
def analyze_video(video_url):
    if not is_valid_youtube_url(video_url):
        return None

    video_id = extract_video_id(video_url)
    if not video_id:
        return None

    title = get_video_title(video_id)
    comments = get_youtube_comments(video_id)

    total = len(comments)
    negative_count = sum(
        1 for text in comments
        if any(word in text for word in NEGATIVE_WORDS)
    )

    negative_rate = round((negative_count / total) * 100, 2) if total > 0 else 0
    fire_score = round(negative_rate * math.log(total + 1), 2) if total > 0 else 0

    save_ranking(video_id, title, fire_score)

    return {
        "video_id": video_id,
        "title": title,
        "total": total,
        "negative_rate": negative_rate,
        "fire_score": fire_score
    }

# =========================
# DB保存（UPSERT）
# =========================
def save_ranking(video_id, title, score):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO rankings (video_id, title, fire_score)
        VALUES (%s, %s, %s)
        ON CONFLICT (video_id)
        DO UPDATE SET
            title = EXCLUDED.title,
            fire_score = EXCLUDED.fire_score
    """, (video_id, title, score))

    conn.commit()
    cur.close()
    conn.close()

# =========================
# ランキング取得
# =========================
def get_top_rankings():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT video_id, title, fire_score
        FROM rankings
        ORDER BY fire_score DESC
        LIMIT 10
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows

# =========================
# ゲージ色
# =========================
def get_color(score):
    if score <= 30:
        return "linear-gradient(90deg, #22c55e, #16a34a)"
    elif score <= 60:
        return "linear-gradient(90deg, #eab308, #facc15)"
    elif score <= 80:
        return "linear-gradient(90deg, #f97316, #ea580c)"
    else:
        return "linear-gradient(90deg, #ef4444, #b91c1c)"

# =========================
# ルート
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        video_url = request.form.get("video_url", "")
        result = analyze_video(video_url)

    rankings = get_top_rankings()
    color = get_color(result["fire_score"]) if result else None

    return render_template(
        "index.html",
        result=result,
        rankings=rankings,
        color=color
    )

# =========================
# 本番起動
# =========================
if __name__ == "__main__":
    app.run(debug=False)
