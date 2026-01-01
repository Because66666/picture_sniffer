import time
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from functions import DatabaseManager, DataFetcher, ImageAnalyzer, DataStorage, load_config, setup_logger


class PictureSniffer:
    def __init__(self, config: dict):
        """
        初始化PictureSniffer实例
        
        Args:
            config: 配置字典，包含数据库路径、API密钥、日志配置等信息
        """
        self.logger = setup_logger(
            name="picture_sniffer",
            log_file=config.get("log_file", "logs/picture_sniffer.log"),
            level=config.get("log_level", "INFO")
        )
        
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
            self.data_fetcher,
            config.get("pictures_dir", "pictures")
        )
        self.image_queue = queue.Queue()
        self.max_retries = 3 # 失败重试次数
        self.thread_pool_size = 3 # 线程池大小

    def process_group(self, group_id: str):
        """
        处理指定群组，获取消息并提取图片信息
        
        Args:
            group_id: 群组ID
        """
        self.logger.debug(f"\n处理群: {group_id}")
        
        if self.db_manager.group_exists(group_id):
            self.logger.debug(f"群 {group_id} 已存在，获取新消息...")
            last_message_id = self.db_manager.get_group_last_message_id(group_id)
            
            if last_message_id:
                messages = self.data_fetcher.get_new_messages(group_id, last_message_id, 15)
                self.logger.debug(f"获取到 {len(messages)} 条新消息")
            else:
                messages = self.data_fetcher.get_initial_messages(group_id, 100)
                self.logger.debug(f"获取到 {len(messages)} 条历史消息")
        else:
            self.logger.debug(f"群 {group_id} 第一次初始化，获取历史消息...")
            messages = self.data_fetcher.get_initial_messages(group_id, 100)
            self.logger.debug(f"获取到 {len(messages)} 条历史消息")
        
        if not messages:
            self.logger.debug(f"群 {group_id} 没有消息")
            return
        
        image_messages = self.data_fetcher.extract_image_messages(messages)
        self.logger.debug(f"发现 {len(image_messages)} 张图片")
        
        for image_msg in image_messages:
            self.image_queue.put(image_msg)
        
        if messages:
            latest_message_id = str(messages[-1].get("message_id", ""))
            if self.db_manager.group_exists(group_id):
                self.data_storage.update_group_last_message_id(group_id, latest_message_id)
            else:
                self.data_storage.insert_group(group_id, latest_message_id)
            self.logger.debug(f"更新群 {group_id} 的最新消息ID: {latest_message_id}")

    def process_single_image(self, image_msg: dict):
        """
        处理单张图片，包括分析和保存
        
        Args:
            image_msg: 图片消息字典，包含message_id、group_id、url等信息
        """
        retry_count = image_msg.get("retry_count", 1)
        self.logger.debug(f"处理图片: {image_msg['message_id']}, 重试次数: {retry_count}")
        
        if self.db_manager.image_exists(image_msg["message_id"]):
            self.logger.debug(f"图片已存在，跳过")
            return
        
        analysis_result = self.image_analyzer.analyze_image(image_msg["url"])
        
        if isinstance(analysis_result, dict):
            is_mc_pic = analysis_result.get("is_mc_pic", False)
            self.logger.debug(f"是否为MC图片: {is_mc_pic}")
            
            if is_mc_pic:
                success = self.data_storage.process_and_save_image(image_msg, analysis_result)
                if success:
                    self.logger.debug(f"图片已保存")
                else:
                    self.logger.warning(f"图片保存失败")
            else:
                self.logger.debug(f"不是MC图片，忽略")
        elif analysis_result == -1:
            self.logger.debug(f"图片不合法，忽略")
        else:
            self.logger.warning(f"图片分析失败")
            if retry_count <= self.max_retries:
                image_msg["retry_count"] = retry_count + 1
                self.image_queue.put(image_msg)
                self.logger.warning(f"重新放入队列, 群ID: {image_msg['group_id']}, 消息ID: {image_msg['message_id']}, 重试次数: {retry_count + 1}/{self.max_retries}")
            else:
                self.logger.error(f"已达到最大重试次数，放弃, 群ID: {image_msg['group_id']} ,消息ID: {image_msg['message_id']}")
            raise Exception(f"图片分析失败，重试次数: {retry_count}/{self.max_retries}")

    def process_image_queue(self):
        """
        使用线程池处理图片队列中的所有图片
        
        使用5个线程并发处理图片队列，支持动态调整进度条总数
        """
        self.logger.info(f"启动 {self.thread_pool_size} 个线程处理图片队列")
        
        initial_queue_size = self.image_queue.qsize()
        total_processed = 0
        
        with ThreadPoolExecutor(max_workers=self.thread_pool_size) as executor:
            futures = []
            
            with tqdm(total=initial_queue_size, desc="处理图片", unit="张") as pbar:
                while True:
                    try:
                        image_msg = self.image_queue.get(timeout=1)
                        future = executor.submit(self.process_single_image, image_msg)
                        futures.append(future)
                        
                        current_queue_size = self.image_queue.qsize()
                        if pbar.total < total_processed + current_queue_size + 1:
                            pbar.total = total_processed + current_queue_size + 1
                            pbar.refresh()
                        
                        self.image_queue.task_done()
                    except queue.Empty:
                        break
                
                for future in as_completed(futures):
                    try:
                        future.result()
                        total_processed += 1
                        pbar.update(1)
                    except Exception as e:
                        self.logger.error(f"处理图片时发生异常: {e}")
                        # 此时进度条应当保持不变
                        pbar.update(0)

    def run(self):
        """
        运行图片嗅探器主程序
        
        获取所有群组列表，逐个处理群组中的图片消息
        """
        self.logger.info("开始运行 Picture Sniffer...")
        
        result = self.data_fetcher.get_group_list()
        
        if result.get("status") != "ok":
            self.logger.error("获取群列表失败")
            return
        
        groups = result.get("data", [])
        self.logger.info(f"找到 {len(groups)} 个群")
        
        for group in tqdm(groups, desc="处理群组", unit="个"):
            group_id = str(group.get("group_id", ""))
            group_name = group.get("group_name", "")
            self.logger.debug(f"\n====================\n群 {group_id} ({group_name})")
            
            try:
                self.process_group(group_id)
                
            except Exception as e:
                self.logger.error(f"处理群 {group_id} 时出错: {e}")
                continue
        self.process_image_queue()

        self.logger.info("运行完成!")


if __name__ == "__main__":
    config = load_config("config.json")
    sniffer = PictureSniffer(config)
    sniffer.run()
