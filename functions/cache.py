import os
from PIL import Image

def compress_to_webp(input_path: str, output_path: str, max_size_kb: int = 50) -> bool:
    """
    将输入图片压缩为WebP缩略图，并保存到指定路径。
    如果文件大小超过限制，会自动降低质量或缩小尺寸。

    :param input_path: 输入图片的绝对路径
    :param output_path: 输出图片的保存路径
    :param max_size_kb: 最大文件大小限制（KB），默认为50KB
    :return: 成功返回True，失败返回False
    """
    try:
        if not os.path.exists(input_path):
            print(f"错误: 输入文件不存在 - {input_path}")
            return False

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with Image.open(input_path) as img:
            # 格式转换：处理特殊模式
            if img.mode in ('P', 'CMYK'):
                img = img.convert('RGB')
            
            # 1. 初始预处理：如果图片非常大，先缩放到合理尺寸（例如长边不超过800）
            # 这可以显著提高后续处理速度，并更接近目标大小
            max_initial_dimension = 800
            width, height = img.size
            if width > max_initial_dimension or height > max_initial_dimension:
                ratio = min(max_initial_dimension / width, max_initial_dimension / height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 2. 循环调整质量和尺寸直到满足大小要求
            quality = 80
            target_size_bytes = max_size_kb * 1024
            
            while True:
                # 保存当前状态
                img.save(output_path, 'WEBP', quality=quality)
                
                # 检查大小
                file_size = os.path.getsize(output_path)
                if file_size <= target_size_bytes:
                    return True
                
                # 策略调整
                if quality > 30:
                    # 优先降低质量
                    quality -= 10
                else:
                    # 质量已降至低位，开始缩小尺寸
                    w, h = img.size
                    if w < 100 or h < 100:
                        # 尺寸过小，无法继续压缩，返回当前结果
                        print(f"警告: 无法压缩至 {max_size_kb}KB 以下，当前大小: {file_size/1024:.2f}KB")
                        return True
                    
                    # 每次缩小 20%
                    new_w, new_h = int(w * 0.8), int(h * 0.8)
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    # 尺寸缩小后，质量不需要设得太低，可以保持或微调，这里保持当前低质量以确保变小
    
    except ImportError:
        print("错误: 未安装 Pillow 库。请运行 `pip install Pillow` 安装。")
        return False
    except Exception as e:
        print(f"压缩图片时发生未知错误: {e}")
        return False
