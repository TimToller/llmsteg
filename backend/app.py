# app.py
from flask import Flask, request, jsonify

# Import your encoding and decoding functions
from stegano import encode_message, decode_message

app = Flask(__name__)


@app.route("/encode", methods=["POST"])
def encode():
    data = request.json
    message = data.get("message")
    prompt = data.get("prompt", "Once upon a time, Jim")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        cover_text = encode_message(message=message, prompt=prompt)
        return jsonify({"cover_text": cover_text}), 200
        # return jsonify({"cover_text": "test"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/decode", methods=["POST"])
def decode():
    data = request.json
    cover_text = data.get("cover_text")
    prompt = data.get("prompt", "Once upon a time, Jim")

    if not cover_text:
        return jsonify({"error": "No cover text provided"}), 400

    try:
        secret_message = decode_message(encoded_text=cover_text, prompt=prompt)
        return jsonify({"secret_message": secret_message}), 200
        # return jsonify({"secret_message": "test"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def health():
    return "Hello, world!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
