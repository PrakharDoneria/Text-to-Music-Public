from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

EXTERNAL_API_URL = "https://riffit-song-server-qb66e4cj5q-uc.a.run.app/videoSong"
STORAGE_BASE_URL = "https://video-song-renderer-bucket-prod.storage.googleapis.com/"


def check_song_ready(uid):
    song_url = f"{STORAGE_BASE_URL}{uid}/index.m3u8"
    while True:
        response = requests.head(song_url)
        if response.status_code == 200:
            return song_url
        time.sleep(5)


@app.route("/music", methods=["POST"])
def create_music():
    data = request.json
    title = data.get("title")
    lyrics = data.get("lyrics")

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
        "uid": "36f1e55c-1977-4b47-9988-bc915c82b441"
    }

    response = requests.post(EXTERNAL_API_URL, json=payload)
    if response.status_code != 200:
        return jsonify({"error": "Failed to create song"}), 500

    response_data = response.json()
    uid = response_data.get("uid")

    song_url = check_song_ready(uid)
    return jsonify({"songUrl": song_url})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
