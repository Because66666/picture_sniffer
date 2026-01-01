from flask import Flask, jsonify, send_from_directory
import os
from functions.database import DatabaseManager
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db_manager = DatabaseManager()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURES_DIR = os.path.join(BASE_DIR, 'pictures')
STATIC_DIR = os.path.join(BASE_DIR, 'website', 'dist')

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)

@app.route('/api/images', methods=['GET'])
def get_images():
    images = db_manager.get_all_images()
    return jsonify({
        'success': True,
        'data': images
    })

@app.route('/api/random-image', methods=['GET'])
def get_random_image():
    images = db_manager.get_random_images(limit=10)
    if images:
        return jsonify({
            'success': True,
            'data': images
        })
    return jsonify({
        'success': False,
        'message': 'No images found'
    }), 404

@app.route('/pictures/<filename>', methods=['GET'])
def serve_picture(filename):
    return send_from_directory(PICTURES_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
