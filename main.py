import time
from database import DatabaseManager
from data_fetcher import DataFetcher
from image_analyzer import ImageAnalyzer
from data_storage import DataStorage
from config_loader import load_config


class PictureSniffer:
    def __init__(self, config: dict):
        self.db_manager = DatabaseManager(config.get("db_path", "picture_sniffer.db"))
        self.data_fetcher = DataFetcher(
            config["natcat_base_url"],
            config["natcat_token"]
        )
        self.image_analyzer = ImageAnalyzer(
            config["openai_token"],
            config.get("openai_base_url", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
        )
        self.data_storage = DataStorage(
            self.db_manager,
            config.get("pictures_dir", "pictures")
        )

    def process_group(self, group_id: str):
        print(f"\n=====================\n处理群: {group_id}")
        
        if self.db_manager.group_exists(group_id):
            print(f"群 {group_id} 已存在，获取新消息...")
            last_message_id = self.db_manager.get_group_last_message_id(group_id)
            
            if last_message_id:
                messages = self.data_fetcher.get_new_messages(group_id, last_message_id, 15)
                print(f"获取到 {len(messages)} 条新消息")
            else:
                messages = self.data_fetcher.get_initial_messages(group_id, 100)
                print(f"获取到 {len(messages)} 条历史消息")
        else:
            print(f"群 {group_id} 第一次初始化，获取历史消息...")
            messages = self.data_fetcher.get_initial_messages(group_id, 100)
            print(f"获取到 {len(messages)} 条历史消息")
        
        if not messages:
            print(f"群 {group_id} 没有消息")
            return
        
        image_messages = self.data_fetcher.extract_image_messages(messages)
        print(f"发现 {len(image_messages)} 张图片")
        
        for idx, image_msg in enumerate(image_messages, 1):
            print(f"  处理图片 {idx}/{len(image_messages)}: {image_msg['message_id']}")
            
            if self.db_manager.image_exists(image_msg["message_id"]):
                print(f"    图片已存在，跳过")
                continue
            
            analysis_result = self.image_analyzer.analyze_image(image_msg["url"])
            
            if analysis_result:
                is_mc_pic = analysis_result.get("is_mc_pic", False)
                print(f"    是否为MC图片: {is_mc_pic}")
                
                if is_mc_pic:
                    success = self.data_storage.process_and_save_image(image_msg, analysis_result)
                    if success:
                        print(f"    图片已保存")
                    else:
                        print(f"    图片保存失败")
                else:
                    print(f"    不是MC图片，忽略")
            else:
                print(f"    图片分析失败")
            
            time.sleep(1)
        
        if messages:
            latest_message_id = str(messages[0].get("message_id", ""))
            if self.db_manager.group_exists(group_id):
                self.data_storage.update_group_last_message_id(group_id, latest_message_id)
            else:
                self.data_storage.insert_group(group_id, latest_message_id)
            print(f"更新群 {group_id} 的最新消息ID: {latest_message_id}")

    def run(self):
        print("开始运行 Picture Sniffer...")
        
        result = self.data_fetcher.get_group_list()
        
        if result.get("status") != "ok":
            print("获取群列表失败")
            return
        
        groups = result.get("data", [])
        print(f"找到 {len(groups)} 个群")
        
        for group in groups:
            group_id = str(group.get("group_id", ""))
            group_name = group.get("group_name", "")
            print(f"\n群 {group_id} ({group_name})")
            
            try:
                self.process_group(group_id)
            except Exception as e:
                print(f"处理群 {group_id} 时出错: {e}")
                continue
        
        print("\n运行完成!")


if __name__ == "__main__":
    config = load_config("config.json")
    sniffer = PictureSniffer(config)
    sniffer.run()
