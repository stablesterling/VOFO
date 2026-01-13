from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from yt_dlp import YoutubeDL
import os

port = int(os.environ.get("PORT", 5000))
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def soundcloud_search(query):
    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "extract_flat": True,
            "http_headers": HEADERS
        }
        with YoutubeDL(ydl_opts) as ydl:
            r = ydl.extract_info(f"scsearch10:{query}", download=False)
            results = []
            for e in r.get("entries", []):
                if not e: continue
                results.append({
                    "id": e.get("url"),
                    "title": e.get("title"),
                    "artist": e.get("uploader") or "SoundCloud Artist",
                    "thumbnail": e.get("thumbnail") or "https://placehold.co/50x50?text=No+Cover"
                })
            return results
    except:
        return []

@app.route("/api/search")
def search():
    q = request.args.get("q")
    return jsonify(soundcloud_search(q)) if q else jsonify([])

@app.route("/api/play", methods=["POST"])
def play():
    track_url = request.json.get("url")
    try:
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best",
            "quiet": True,
            "http_headers": HEADERS
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(track_url, download=False)
            return jsonify({
                "stream_url": info["url"],
                "ext": info.get("ext", "")
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
