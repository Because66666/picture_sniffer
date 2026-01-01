from types import NoneType
import requests
import os
from datetime import datetime
from typing import Dict, Any
from database import DatabaseManager


class DataStorage:
    def __init__(self, db_manager: DatabaseManager, pictures_dir: str = "pictures"):
        self.db_manager = db_manager
        self.pictures_dir = pictures_dir
        self._ensure_pictures_dir()

    def _ensure_pictures_dir(self):
        if not os.path.exists(self.pictures_dir):
            os.makedirs(self.pictures_dir)

    def download_image(self, url: str, group_id: str, message_id: str) -> str:
        filename = f"{group_id}_{message_id}.jpg"
        file_path = os.path.join(self.pictures_dir, filename)
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            return file_path
        except requests.exceptions.RequestException as e:
            print(f"下载图片失败: {url}, 错误: {e}")
            return ""

    def save_image_info(
        self,
        image_id: str,
        image_path: str,
        category: str,
        description: str,
        create_time: str|NoneType = None
    ):
        if create_time is None:
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.db_manager.insert_image(image_id, image_path, category, description, create_time)

    def process_and_save_image(
        self,
        image_data: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> bool:
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
        self.db_manager.update_group_last_message_id(group_id, last_message_id)

    def insert_group(self, group_id: str, last_message_id: str):
        self.db_manager.insert_group(group_id, last_message_id)
