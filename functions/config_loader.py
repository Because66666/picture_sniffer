import json
import os


def load_config(config_path: str = "config.json") -> dict:
    """
    从配置文件加载配置
    
    Args:
        config_path: 配置文件路径，默认为"config.json"
    
    Returns:
        dict: 配置字典，包含所有配置项
    
    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置文件缺少必需的键
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    required_keys = [
        "natcat_base_url",
        "natcat_token",
        "openai_token"
    ]
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"配置文件缺少必需的键: {key}")
    
    config.setdefault("openai_base_url", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
    config.setdefault("db_path", "picture_sniffer.db")
    config.setdefault("pictures_dir", "pictures")
    
    return config
