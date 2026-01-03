import asyncio
import websockets
import json
from functions.config_loader import load_config
from functions.logger_config import setup_logger
from main import PictureSniffer


logger = setup_logger("ws_server")

async def main():
    """
    主函数，用于连接到 NapCat WebSocket 服务器并处理消息。
    复用了大部分 PictureSniffer 的功能，仅对图片消息进行处理。
    """
    config = load_config("config.json")
    sniffer = PictureSniffer(config)
    sniffer.thread_pool_size = 1
    uri = config.get("napcat_ws_uri")
    token = config.get("napcat_token")
    if not token:
        logger.error("napcat_token 未配置")
        raise ValueError("napcat_token 未配置")
    if not uri:
        logger.error("napcat_ws_uri 未配置")
        raise ValueError("napcat_ws_uri 未配置")
    additional_headers = {"Authorization": f"Bearer {token}"}
    logger.info("尝试连接到 %s ，使用 token 进行认证", uri)
    async with websockets.connect(uri, additional_headers=additional_headers) as ws:
        # 接收响应或事件
        while True:
            msg = await ws.recv()
            try:
                message = json.loads(msg)
            except json.JSONDecodeError:
                logger.warning("收到非JSON消息：%s", msg)
                continue
            message_bodies = message.get("message", [])
            if not message_bodies:
                continue
            image_messages = sniffer.data_fetcher.extract_image_messages([message])
            for image_message in image_messages:
                sniffer.image_queue.put(image_message)
            sniffer.process_image_queue()

asyncio.run(main())