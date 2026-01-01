from types import NoneType
import requests
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from .database import DatabaseManager
from .logger_config import setup_logger


class DataStorage:
    def __init__(self, db_manager: DatabaseManager, data_fetcher, pictures_dir: str = "pictures"):
        """
        初始化DataStorage实例
        
        Args:
            db_manager: 数据库管理器实例
            data_fetcher: 数据获取器实例
            pictures_dir: 图片存储目录，默认为"pictures"
        """
        self.logger = setup_logger("data_storage")
        self.db_manager = db_manager
        self.data_fetcher = data_fetcher
        self.pictures_dir = pictures_dir
        self._ensure_pictures_dir()

    def _ensure_pictures_dir(self):
        """
        确保图片存储目录存在，如果不存在则创建
        """
        if not os.path.exists(self.pictures_dir):
            os.makedirs(self.pictures_dir)

    def download_image(self, url: str, group_id: str, message_id: str) -> str:
        """
        下载图片到本地
        
        Args:
            url: 图片URL地址
            group_id: 群组ID
            message_id: 消息ID
        
        Returns:
            str: 图片文件路径，下载失败则返回空字符串
        """
        filename = f"{group_id}_{message_id}.jpg"
        file_path = os.path.join(self.pictures_dir, filename)

        response = requests.get(url, timeout=30)
        try:
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            return file_path
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                self.logger.warning(f"遇到400错误，尝试获取新的消息体: {url}")
                message_body = self.data_fetcher.fetch_message_body(message_id)
                if message_body:
                    try:
                        message_data = message_body # 这个类型是列表类型
                        messages = message_data if isinstance(message_data, list) else message_data.get("message", [])
                        for msg in messages:
                            if msg.get("type") == "image":
                                new_url = msg.get("data", {}).get("url", "")
                                if new_url and new_url != url:
                                    self.logger.info(f"获取到新的URL: {new_url}")
                                    try:
                                        new_response = requests.get(new_url, timeout=30)
                                        new_response.raise_for_status()
                                        with open(file_path, "wb") as f:
                                            f.write(new_response.content)
                                        return file_path
                                    except requests.exceptions.RequestException as new_e:
                                        self.logger.error(f"使用新URL下载失败: {new_e}")
                    except json.JSONDecodeError as json_e:
                        self.logger.error(f"解析消息体失败: {json_e}")
            self.logger.error(f"下载图片失败: {url}, 错误: {e}")
            return ""
        except requests.exceptions.RequestException as e:
            self.logger.error(f"下载图片失败: {url}, 错误: {e}")
            return ""

    def save_image_info(
        self,
        image_id: str,
        image_path: str,
        category: str,
        description: str,
        create_time: str|NoneType = None
    ):
        """
        保存图片信息到数据库
        
        Args:
            image_id: 图片ID（消息ID）
            image_path: 图片文件路径
            category: 图片分类
            description: 图片描述
            create_time: 创建时间，如果为None则使用当前时间
        """
        if create_time is None:
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.db_manager.insert_image(image_id, image_path, category, description, create_time)

    def process_and_save_image(
        self,
        image_data: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> bool:
        """
        处理并保存图片，包括下载和数据库存储
        
        Args:
            image_data: 图片数据字典，包含message_id、group_id、url等信息
            analysis_result: 图片分析结果，包含is_mc_pic、category、description等
        
        Returns:
            bool: 处理成功返回True，失败返回False
        """
        if not analysis_result.get("is_mc_pic", False):
            return False
        
        image_id = image_data.get("message_id", "")
        group_id = image_data.get("group_id", "")
        url = image_data.get("url", "")
        time_str = image_data.get("time", "")
        
        if self.db_manager.image_exists(image_id):
            return True
        
        image_path = self.download_image(url, group_id, image_id)
        if not image_path:
            return False
        
        category = analysis_result.get("category", "")
        description = analysis_result.get("description", "")
        
        self.save_image_info(image_id, image_path, category, description, time_str)
        return True

    def update_group_last_message_id(self, group_id: str, last_message_id: str):
        """
        更新群组的最新消息ID
        
        Args:
            group_id: 群组ID
            last_message_id: 最新消息ID
        """
        self.db_manager.update_group_last_message_id(group_id, last_message_id)

    def insert_group(self, group_id: str, last_message_id: str):
        """
        插入新群组记录到数据库
        
        Args:
            group_id: 群组ID
            last_message_id: 最新消息ID
        """
        self.db_manager.insert_group(group_id, last_message_id)
