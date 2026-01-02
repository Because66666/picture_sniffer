from flask import Flask, jsonify, send_from_directory, request
import os
from functions.database import DatabaseManager
from functions.image_analyzer import ImageAnalyzer
from functions.config_loader import load_config
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
CORS(app)

db_manager = DatabaseManager()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURES_DIR = os.path.join(BASE_DIR, 'pictures')
STATIC_DIR = os.path.join(BASE_DIR, 'website', 'dist')

config = load_config()
image_analyzer = ImageAnalyzer(api_key=config['openai_token'], api_url=config['openai_base_url'])

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

# @app.route('/api/describe-image', methods=['POST'])
def describe_image():
    """
    描述图片（暂时不实现，等待之后的密钥登录功能实现）
    
    Args:
        image_id: 图片ID（消息ID）
    
    Returns:
        JSON响应，包含图片描述
    """
    data = request.get_json()
    
    if not data or 'image_id' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing image_id in request body'
        }), 400
    
    image_id = data['image_id']
    
    image_record = db_manager.get_image_by_id(image_id)
    
    if not image_record:
        return jsonify({
            'success': False,
            'message': 'Image not found'
        }), 404
    
    relative_path = image_record['image_path']
    absolute_path = os.path.join(BASE_DIR, relative_path)
    
    description = image_analyzer.describe_image(absolute_path)
    
    if description is None:
        return jsonify({
            'success': False,
            'message': 'Failed to analyze image'
        }), 500
    
    db_manager.update_image_description(image_id, description)
    
    return jsonify({
        'success': True,
        'data': description
    })

@app.route('/api/search', methods=['GET'])
def search_images():
    keyword = request.args.get('keyword')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))
    
    if not keyword:
        return jsonify({
            'success': False,
            'message': 'Missing keyword in query parameter'
        }), 400
    
    images = db_manager.search_images(keyword, offset, limit)
    return jsonify({
        'success': True,
        'data': images
    })

@app.route('/pictures/<filename>', methods=['GET'])
def serve_picture(filename):
    return send_from_directory(PICTURES_DIR, filename)

if __name__ == '__main__':
    print(f"服务器启动，监听端口 5000")
    serve(app, host='0.0.0.0', port=5000, threads=4)
