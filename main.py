from flask import Flask, request, jsonify
import requests
import time
import logging
import uuid

app = Flask(__name__)

EXTERNAL_API_URL = "https://riffit-song-server-qb66e4cj5q-uc.a.run.app/videoSong"
STORAGE_BASE_URL = "https://video-song-renderer-bucket-prod.storage.googleapis.com/"

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def generate_uid():
    return str(uuid.uuid4())


def check_song_ready(uid):
    song_url = f"{STORAGE_BASE_URL}{uid}/index.m3u8"
    logging.info(f"Checking song availability: {song_url}")
    while True:
        try:
            response = requests.head(song_url, timeout=5)
            if response.status_code == 200:
                logging.info("Song is ready.")
                return song_url
        except requests.RequestException as e:
            logging.error(f"Error checking song status: {e}")
        time.sleep(5)


@app.route("/music", methods=["POST"])
def create_music():
    data = request.json
    if not data or "lyrics" not in data:
        logging.error("Invalid request: Missing lyrics")
        return jsonify({"error": "Lyrics are required"}), 400

    title = data.get("title", "Untitled")
    lyrics = data["lyrics"]
    uid = generate_uid()

    logging.info(f"Received request to create music: Title={title}, UID={uid}")

    payload = {
        "text": lyrics,
        "genre": "Indie",
        "voice": "Natalie",
        "tempo": 117,
        "pitch": 0,
        "volume": 1,
        "accompanimentVolume": 1,
        "image": "",
        "project": "songr",
        "uid": uid
    }

    try:
        response = requests.post(EXTERNAL_API_URL, json=payload, timeout=10)
        if response.status_code != 200:
            logging.error(f"Failed to create song: {response.text}")
            return jsonify({"error": "Failed to create song"}), 500
    except requests.RequestException as e:
        logging.error(f"Request to external API failed: {e}")
        return jsonify({"error": "External API request failed"}), 500

    song_url = check_song_ready(uid)
    return jsonify({"songUrl": song_url})


if __name__ == "__main__":
    app.run(debug=True)
