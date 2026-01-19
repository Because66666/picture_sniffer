import os
import sys
from pathlib import Path
from tqdm import tqdm

# 确保可以导入 functions 模块
# 如果脚本在项目根目录下运行，通常不需要这行，但为了稳健加上
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from functions.cache import compress_to_webp

def generate_cache(source_dir: str, cache_dir: str):
    """
    遍历 source_dir 中的图片，检查 cache_dir 中是否存在对应的 webp 缩略图。
    如果不存在，则生成缩略图。
    保持子目录结构。
    """
    # 支持的图片扩展名
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

    source_path = Path(source_dir).resolve()
    cache_path = Path(cache_dir).resolve()

    if not source_path.exists():
        print(f"源目录不存在: {source_dir}")
        try:
            os.makedirs(source_path)
            print(f"已自动创建源目录: {source_dir}")
        except OSError as e:
            print(f"无法创建源目录: {e}")
        return

    if not cache_path.exists():
        try:
            os.makedirs(cache_path)
            print(f"创建缓存目录: {cache_dir}")
        except OSError as e:
            print(f"无法创建缓存目录: {e}")
            return

    print(f"开始扫描文件列表: {source_path} ...")
    
    # 第一步：收集所有待处理的图片文件
    all_image_files = []
    for root, dirs, files in os.walk(source_path):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in IMAGE_EXTENSIONS:
                all_image_files.append(file_path)

    total_files = len(all_image_files)
    if total_files == 0:
        print("未找到任何图片文件。")
        return

    print(f"找到 {total_files} 个图片文件，开始处理...")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0

    # 第二步：使用 tqdm 展示进度条进行处理
    with tqdm(total=total_files, unit="img", desc="处理进度") as pbar:
        for file_path in all_image_files:
            try:
                # 计算相对路径，以便在 cache 中保持结构
                try:
                    relative_path = file_path.relative_to(source_path)
                except ValueError:
                    # 理论上不会发生
                    pbar.update(1)
                    continue
                
                # 构建目标 webp 路径
                target_relative_path = relative_path.with_suffix('.webp')
                target_path = cache_path / target_relative_path

                # 检查缓存是否存在
                if target_path.exists():
                    skipped_count += 1
                    pbar.update(1)
                    continue

                # 确保目标文件的父目录存在
                if not target_path.parent.exists():
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                # 调用压缩函数
                success = compress_to_webp(str(file_path), str(target_path))
                
                if success:
                    processed_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1
            finally:
                pbar.update(1)

    print("-" * 30)
    print(f"处理完成。")
    print(f"新增生成: {processed_count}")
    print(f"跳过已有: {skipped_count}")
    print(f"处理失败: {error_count}")
    print("-" * 30)

if __name__ == "__main__":
    # 定义路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pictures_dir = os.path.join(base_dir, "pictures")
    cache_dir = os.path.join(base_dir, "cache")

    generate_cache(pictures_dir, cache_dir)
