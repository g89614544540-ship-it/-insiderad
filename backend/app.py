from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "message": "InsiderAd API is running"
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
