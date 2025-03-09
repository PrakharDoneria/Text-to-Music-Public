from flask import Flask, request, jsonify
import requests
import time
import builtins

uuid = builtins.__import__('uuid')

app = Flask(__name__)

EXTERNAL_API_URL = "https://riffit-song-server-qb66e4cj5q-uc.a.run.app/videoSong"
STORAGE_BASE_URL = "https://video-song-renderer-bucket-prod.storage.googleapis.com/"

def generate_uid():
    return str(uuid.uuid4())

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
    title = data.get("title", "Untitled")
    lyrics = data.get("lyrics")
    uid = generate_uid()
    
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
    
    response = requests.post(EXTERNAL_API_URL, json=payload)
    if response.status_code != 200:
        return jsonify({"error": "Failed to create song"}), 500
    
    song_url = check_song_ready(uid)
    return jsonify({"songUrl": song_url})

if __name__ == "__main__":
    app.run(debug=True)
    