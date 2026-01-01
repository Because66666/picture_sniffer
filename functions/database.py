import sqlite3
import os
from typing import Optional, List, Dict, Any


class DatabaseManager:
    def __init__(self, db_path: str = "picture_sniffer.db"):
        """
        初始化DatabaseManager实例
        
        Args:
            db_path: SQLite数据库文件路径，默认为"picture_sniffer.db"
        """
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """
        获取数据库连接
        
        Returns:
            sqlite3.Connection: 数据库连接对象
        """
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """
        初始化数据库架构，创建必要的表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT PRIMARY KEY,
                last_message_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                image_id TEXT PRIMARY KEY,
                image_path TEXT,
                category TEXT,
                description TEXT,
                create_time TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def group_exists(self, group_id: str) -> bool:
        """
        检查群组是否存在于数据库中
        
        Args:
            group_id: 群组ID
        
        Returns:
            bool: 存在返回True，否则返回False
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM groups WHERE group_id = ?', (group_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def insert_group(self, group_id: str, last_message_id: str):
        """
        插入或更新群组记录
        
        Args:
            group_id: 群组ID
            last_message_id: 最新消息ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO groups (group_id, last_message_id) VALUES (?, ?)',
            (group_id, last_message_id)
        )
        conn.commit()
        conn.close()

    def update_group_last_message_id(self, group_id: str, last_message_id: str):
        """
        更新群组的最新消息ID
        
        Args:
            group_id: 群组ID
            last_message_id: 最新消息ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE groups SET last_message_id = ? WHERE group_id = ?',
            (last_message_id, group_id)
        )
        conn.commit()
        conn.close()

    def get_group_last_message_id(self, group_id: str) -> Optional[str]:
        """
        获取群组的最新消息ID
        
        Args:
            group_id: 群组ID
        
        Returns:
            Optional[str]: 最新消息ID，如果群组不存在则返回None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT last_message_id FROM groups WHERE group_id = ?', (group_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def insert_image(self, image_id: str, image_path: str, category: str, description: str, create_time: str):
        """
        插入或更新图片记录
        
        Args:
            image_id: 图片ID（消息ID）
            image_path: 图片文件路径
            category: 图片分类
            description: 图片描述
            create_time: 创建时间
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO images (image_id, image_path, category, description, create_time) VALUES (?, ?, ?, ?, ?)',
            (image_id, image_path, category, description, create_time)
        )
        conn.commit()
        conn.close()

    def image_exists(self, image_id: str) -> bool:
        """
        检查图片是否存在于数据库中
        
        Args:
            image_id: 图片ID（消息ID）
        
        Returns:
            bool: 存在返回True，否则返回False
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM images WHERE image_id = ?', (image_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def get_all_groups(self) -> List[Dict[str, Any]]:
        """
        获取所有群组记录
        
        Returns:
            List[Dict[str, Any]]: 群组列表，每个群组包含group_id和last_message_id
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT group_id, last_message_id FROM groups')
        results = cursor.fetchall()
        conn.close()
        return [{'group_id': row[0], 'last_message_id': row[1]} for row in results]

    def get_all_images(self) -> List[Dict[str, Any]]:
        """
        获取所有图片记录
        
        Returns:
            List[Dict[str, Any]]: 图片列表，每个图片包含image_id、image_path、category、description和create_time
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT image_id, image_path, category, description, create_time FROM images')
        results = cursor.fetchall()
        conn.close()
        return [{
            'image_id': row[0],
            'image_path': row[1],
            'category': row[2],
            'description': row[3],
            'create_time': row[4]
        } for row in results]
