from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from yt_dlp import YoutubeDL
import os

# Render uses the 'PORT' environment variable
port = int(os.environ.get("PORT", 5000))

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def soundcloud_search(query):
    try:
        ydl_opts = {"quiet": True, "noplaylist": True, "extract_flat": True, "http_headers": HEADERS}
        with YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"scsearch10:{query}", download=False)
            results = []
            for entry in search_results.get('entries', []):
                if entry:
                    results.append({
                        "id": entry.get("url"),
                        "title": entry.get("title"),
                        "artist": entry.get("uploader") or "SoundCloud Artist",
                        "thumbnail": entry.get("thumbnail") or "https://placehold.co/500x500?text=No+Cover+Art"
                    })
            return results
    except Exception as e:
        return []

@app.route("/api/search")
def search():
    query = request.args.get("q")
    return jsonify(soundcloud_search(query)) if query else jsonify([])

@app.route("/api/play", methods=["POST"])
def play():
    track_url = request.json.get("url")
    try:
        ydl_opts = {"format": "bestaudio/best", "quiet": True, "http_headers": HEADERS}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(track_url, download=False)
            return jsonify({"stream_url": info["url"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return send_from_directory(".", "tesst.html")

if __name__ == "__main__":
    # Important: bind to 0.0.0.0 for Render
    app.run(host="0.0.0.0", port=port)
