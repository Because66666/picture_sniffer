import os
import zipfile
import logging

def compress_two_folders(folder1_path, folder2_path, output_dir, zip_filename="archive.zip"):
    """
    将两个指定的文件夹路径压缩成一个zip压缩包，然后放在指定的文件夹路径下。

    :param folder1_path: 第一个文件夹的绝对路径
    :param folder2_path: 第二个文件夹的绝对路径
    :param output_dir: 存放生成的zip文件的目录路径
    :param zip_filename: 生成的zip文件名（包含后缀），默认为 "archive.zip"
    :return: bool 任务执行成功返回 True，失败返回 False
    """
    try:
        # 检查源文件夹是否存在
        if not os.path.isdir(folder1_path):
            logging.error(f"文件夹不存在: {folder1_path}")
            return False
        if not os.path.isdir(folder2_path):
            logging.error(f"文件夹不存在: {folder2_path}")
            return False

        # 确保输出目录存在，如果不存在则创建
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                logging.error(f"无法创建输出目录 {output_dir}: {e}")
                return False

        # 构建完整的输出文件路径
        zip_file_path = os.path.join(output_dir, zip_filename)

        # 检查文件路径是否存在。如果存在并且修改日期距离现在不超过24小时，则直接返回文件。
        if os.path.exists(zip_file_path):
            file_mod_time = os.path.getmtime(zip_file_path)
            current_time = time.time()
            if current_time - file_mod_time < 24 * 60 * 60:
                logging.debug(f"压缩文件已存在，且距离上次修改不足24小时，直接返回: {zip_file_path}")
                return True

        # 创建并写入 Zip 文件
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder_path in [folder1_path, folder2_path]:
                # 获取文件夹名称，用于在 zip 文件内部保持结构
                # 使用 os.path.normpath 处理路径末尾可能存在的斜杠
                base_folder_name = os.path.basename(os.path.normpath(folder_path))
                
                # 获取父目录路径，用于计算相对路径
                parent_dir = os.path.dirname(os.path.normpath(folder_path))

                # 遍历文件夹中的所有文件
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        abs_file_path = os.path.join(root, file)
                        # 计算文件在 zip 包内的相对路径
                        # 例如：如果压缩 D:/data/images，文件是 D:/data/images/1.jpg
                        # parent_dir 是 D:/data
                        # rel_path 将是 images/1.jpg
                        rel_path = os.path.relpath(abs_file_path, parent_dir)
                        zipf.write(abs_file_path, rel_path)

        logging.info(f"成功将文件夹压缩至: {zip_file_path}")
        return True

    except Exception as e:
        logging.exception(f"压缩过程中发生错误: {e}")
        return False
