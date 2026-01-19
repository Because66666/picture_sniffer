from flask import Flask, jsonify, send_from_directory, request, g
import os
from functools import wraps
from functions.database import DatabaseManager
from functions.make_cache import generate_cache
from functions.image_analyzer import ImageAnalyzer
from functions.config_loader import load_config
from functions.zip import compress_two_folders
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
CORS(app)

db_manager = DatabaseManager()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURES_DIR = os.path.join(BASE_DIR, 'pictures')
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
ZIP_FILE_PATH = os.path.join(BASE_DIR, 'zip')
STATIC_DIR = os.path.join(BASE_DIR, 'website', 'dist')

config = load_config()
image_analyzer = ImageAnalyzer(api_key=config['openai_token'], api_url=config['openai_base_url'])
WEBUI_TOKEN = config.get('webui_token', 'your_webui_token')

# 下载API的全局状态变量，防止多次访问的抖动问题
DOWNLOADING = False

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'message': 'Missing authorization header'
            }), 401
        
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Invalid authorization header format'
            }), 401
        
        token = auth_header[7:]
        
        if token != WEBUI_TOKEN:
            return jsonify({
                'success': False,
                'message': '密钥错误'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing token in request body'
        }), 400
    
    token = data['token']
    
    if token == WEBUI_TOKEN:
        return jsonify({
            'success': True,
            'message': '成功登录'
        })
    else:
        return jsonify({
            'success': False,
            'message': '密钥错误'
        }), 401

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')


@app.route('/login')
def login_page():
    return send_from_directory(STATIC_DIR, 'login.html')


@app.route('/search')
def search_page():
    return send_from_directory(STATIC_DIR, 'search.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)

# TODO：使用缓存。
@app.route('/api/random-image', methods=['GET'])
@require_auth
def get_random_image():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 20, type=int)
    images = db_manager.get_random_images(offset=offset, limit=limit)
    if images:
        return jsonify({
            'success': True,
            'data': images
        })
    return jsonify({
        'success': False,
        'message': 'No images found'
    }), 404

@app.route('/api/describe-image', methods=['POST'])
@require_auth
def describe_image():
    """
    描述图片（需要登录）
    
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

# TODO：使用缓存。
@app.route('/api/search', methods=['GET'])
@require_auth
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

@app.route('/api/image/<image_id>', methods=['GET'])
@require_auth
def get_image_by_id(image_id):
    """
    根据图片ID获取图片记录
    
    Args:
        image_id: 图片ID（消息ID）
    
    Returns:
        JSON响应，包含图片记录
    """
    image_record = db_manager.get_image_by_id(image_id)
    
    if not image_record:
        return jsonify({
            'success': False,
            'message': 'Image not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': image_record
    })

@app.route('/api/delete_image/<image_id>', methods=['DELETE'])
@require_auth
def delete_image(image_id):
    """
    删除图片
    
    Args:
        image_id: 图片ID
    """
    # 检查图片是否存在
    if not db_manager.image_exists(image_id):
        return jsonify({
            'success': False,
            'message': 'Image not found'
        }), 404
    
    # 删除图片
    try:
        db_manager.delete_image(image_id)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to delete image: {str(e)}'
        }), 500

    return jsonify({
        'success': True,
        'message': 'Image deleted successfully'
    })

# TODO：使用缓存。
@app.route('/api/images_by_time', methods=['GET'])
@require_auth
def get_images_list():
    """
    获取图片列表（按时间倒序）
    
    Query Args:
        offset: 偏移量
        limit: 数量
    """
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # get_images_by_id 已被修改为按 create_time 倒序返回
    images = db_manager.get_images_by_id(offset=offset, limit=limit)
    
    return jsonify({
        'success': True,
        'data': images
    })

@app.route('/pictures/<filename>', methods=['GET'])
def serve_picture(filename):
    return send_from_directory(PICTURES_DIR, filename)

@app.route('/cache/<filename>', methods=['GET'])
def serve_cache_picture(filename):
    return send_from_directory(CACHE_DIR, filename)


@app.route("/api/download_images", methods=['GET'])
@require_auth
def download_images():
    """
    下载图片（需要登录）
    
    """
    if DOWNLOADING:
        return jsonify({
            'success': False,
            'message': '正在压缩中。'
        }), 400
    
    DOWNLOADING = True
    try:
        # 已经设计防止抖动：如果压缩包存在并且修改日期距离现在不超过24小时，则直接返回文件。需要注意该设计需要保持压缩包的名称不变为固定值。
        compress_two_folders(PICTURES_DIR, CACHE_DIR, ZIP_FILE_PATH)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'压缩图片失败，请联系Because检查日志: {str(e)}'
        }), 500
    finally:
        DOWNLOADING = False
    
    return send_from_directory(os.path.dirname(ZIP_FILE_PATH), os.path.basename(ZIP_FILE_PATH), as_attachment=True)

if __name__ == '__main__':
    print("进入预检：检查图片缓存中。")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pictures_dir = os.path.join(base_dir, "pictures")
    cache_dir = os.path.join(base_dir, "cache")
    generate_cache(pictures_dir, cache_dir)

    print(f"服务器启动，监听端口 5000")
    serve(app, host='0.0.0.0', port=5000, threads=10)
