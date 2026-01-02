import requests
import json
from typing import Dict, Any, Optional
from .logger_config import setup_logger


class ImageAnalyzer:
    def __init__(self, api_key: str, api_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"):
        """
        初始化ImageAnalyzer实例
        
        Args:
            api_key: OpenAI API密钥
            api_url: API端点URL，默认为智谱AI的API地址
        """
        self.logger = setup_logger("image_analyzer")
        self.api_key = api_key
        self.api_url = api_url

    def analyze_image(self, image_url: str) -> Optional[Dict[str, Any]]|int:
        """
        分析图片内容，判断是否为Minecraft相关图片
        
        Args:
            image_url: 图片URL地址
        
        Returns:
            Optional[Dict[str, Any]]: 分析结果字典，包含：
                - is_mc_pic: 是否为Minecraft图片（布尔值）
                - category: 图片分类（字符串）
                - description: 图片描述（字符串）
            如果分析失败则返回None
        """
        return self._analyze_with_content(image_url, is_url=True)

    def analyze_image_base64(self, base64_image: str) -> Optional[Dict[str, Any]]|int:
        """
        分析base64编码的图片内容，判断是否为Minecraft相关图片
        
        Args:
            base64_image: 图片的base64编码字符串
        
        Returns:
            Optional[Dict[str, Any]]: 分析结果字典，包含：
                - is_mc_pic: 是否为Minecraft图片（布尔值）
                - category: 图片分类（字符串）
                - description: 图片描述（字符串）
            如果分析失败则返回None
        """
        return self._analyze_with_content(base64_image, is_url=False)

    def _analyze_with_content(self, content: str, is_url: bool = True) -> Optional[Dict[str, Any]]|int:
        """
        内部方法：分析图片内容，判断是否为Minecraft相关图片
        
        Args:
            content: 图片URL或base64编码字符串
            is_url: 是否为URL，True表示URL，False表示base64编码
        
        Returns:
            Optional[Dict[str, Any]]: 分析结果字典，包含：
                - is_mc_pic: 是否为Minecraft图片（布尔值）
                - category: 图片分类（字符串）
                - description: 图片描述（字符串）
            如果分析失败则返回None
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        image_content = {
            "type": "image_url",
            "image_url": {
                "url": content
            }
        } if is_url else {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{content}"
            }
        }

        payload = {
            "model": "glm-4.6v-flash",
            "messages": [
                {
                    "role": "system",
                    "content": """
你是专业的图片分析人士，核心任务是：1. 判断图片是否为《我的世界》（Minecraft）相关图片；2. 按要求格式输出结果。

### 关键规则（必须严格遵守）：
1. 格式要求：仅返回JSON字符串，无任何额外文字、解释、注释或格式修饰（如代码块、引号嵌套错误等），字段不可缺失、不可新增。
2. 分类约束：category字段仅能从以下47个选项中选择，无匹配项时强制选「其他」，严禁超出范围：
- 内饰
- 自然废墟
- 废土/后启示录
- 奇幻中式建筑
- 小比例中式写实建筑
- 大比例中式写实建筑
- 日式建筑
- 乡野建筑
- 体素艺术
- 工厂建筑
- 工业巨构
- 树木
- 罗马式欧式建筑
- 哥特式欧式建筑
- 巴洛克式欧式建筑
- 中世纪式欧式建筑
- 新奥斯曼式欧式建筑
- 维多利亚式欧式建筑
- 蒸汽朋克风格
- 现代街区
- 玻璃幕墙摩天楼
- 日式现代城市
- 中式现代城市
- 交通基础设施
- 道路与桥梁
- 大型地形场景
- 赛博朋克大型场景
- 赛博朋克建筑
- 赛博朋克街区
- 粗野主义建筑
- 东南亚风格建筑
- 波斯风格建筑
- 伊斯兰风格建筑
- 玛雅-阿兹特克/美洲原住民建筑
- 古埃及建筑
- 童话/奇幻风格建筑
- 自然野性建筑
- 未来主义
- 太空建筑
- 车辆载具
- 科幻载具
- 大型机器人
- 自然地形
- 雕塑
- 旗帜和图案
- 仿真建筑
- 其他

3. 判断依据：
   - 是《我的世界》图片：需包含游戏核心特征（方块像素风格、游戏内特有场景/物品/生物、玩家搭建的建筑等）；
   - 非《我的世界》图片：无上述核心特征，直接判定is_mc_pic为false，category固定填「其他」。

### 输出字段说明：
- is_mc_pic：布尔值（true/false），仅判断是否为《我的世界》相关图片；
- category：严格遵循上述47个选项，非《我的世界》图片统一填「其他」；
- description：简洁描述图片核心内容（如"《我的世界》中由方块搭建的中式宫殿，带飞檐和庭院""现实中的现代公寓照片，无游戏相关元素"），10-50字为宜。

### 示例（仅作参考，需按实际图片输出）：
示例1（是MC图-古代中式风格）：
{"is_mc_pic":true,"category":"古代中式风格","description":"《我的世界》中玩家搭建的中式四合院，有青砖黛瓦和月亮门"}

示例2（是MC图-其他风格）：
{"is_mc_pic":true,"category":"其他","description":"《我的世界》中由红石元件组成的自动农场，含活塞和水流装置"}

示例3（非MC图）：
{"is_mc_pic":false,"category":"其他","description":"现实中的哥特式教堂照片，石质结构和尖顶设计"}
"""
                },
                {
                    "role": "user",
                    "content": [
                        image_content
                    ]
                }
            ],
            "thinking": {
                "type": "disabled"
            }
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            if response.status_code == 400:
                # 这种情况一般是 动图，或者不合法的图片，前者大模型不支持，后者大模型会报错。而且GIF动图和普通的图片无法从消息体进行区分。
                self.logger.error(f"图片不合法，大模型返回：\n状态码: {response.status_code}\n响应内容: {response.text}\n") 
                # 这种情况下就不要引发错误，重试了。
                return -1
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                try:
                    analysis_data = json.loads(content)
                    
                    is_mc_pic = analysis_data.get("is_mc_pic", False)
                    category = analysis_data.get("category", "")
                    description = analysis_data.get("description", "")
                    
                    return {
                        "is_mc_pic": is_mc_pic,
                        "category": category,
                        "description": description
                    }
                except json.JSONDecodeError:
                    return None
            
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"分析图片失败: {e}")
            return None

    def describe_image(self, image_path: str) -> str|None:
        """
        分析图片并返回更加细致的描述。

        Args:
            image_path: 图片绝对路径
        
        Returns:
            图片的详细描述，或者None
        """
        import base64

        # 读取图片，转换为base64编码
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

        payload = {
            "model": "glm-4.6v-flash",
            "messages": [
                {
                    "role": "system",
                    "content": """
### 一、核心身份与任务
你是精通《我的世界》方块机制、建筑逻辑、场景创作的专业玩家+图片分析师，需对给定图片进行**一段式连贯描述**（拒绝分点、列表、序号等结构化表达），同时兼顾“整体风格+核心定位+细节亮点”，突出画面记忆点。

### 二、分步执行指令（智能体内部执行逻辑，输出时需整合为一段）
#### 1. 第一步：核心定位判断（先明确画面主体）
- 要求：精准区分是「单个建筑」还是「整体风景」，并快速锁定核心类型（附具体分类示例）：
  - 单个建筑：中世纪城堡、赛博朋克红石机械、生存原木小屋、糖果风别墅、末地风格堡垒等；
  - 整体风景：樱花林村落群、沙漠绿洲全景、针叶林峡谷地貌、下界堡垒生态、雪地渔村等。

#### 2. 第二步：整体风格把控（再定画面基调）
- 要求：提炼画面核心风格，结合《我的世界》特色材质/色彩/氛围，示例参考：
  - 风格类型：复古像素风（低饱和材质、怀旧方块拼接）、写实生存风（质朴材质、贴近现实场景）、奇幻童话风（高饱和色彩、创意材质组合）、史诗宏大风（大尺度结构、震撼场景）、赛博朋克风（霓虹红石元素、机械感材质）等；
  - 描述要点：用1-2个关键词定调，再补充风格对应的视觉特征（如“写实生存风的质朴厚重”“奇幻童话风的色彩斑斓”）。

#### 3. 第三步：细节特色深挖（按主体类型针对性展开）
- 若为「单个建筑」，聚焦3个维度：
  - 材质与纹理：方块拼接方式（如石砖+橡木撞色、下界石英+玻璃反光）、材质质感（如藤蔓覆盖的复古感、混凝土的光滑度）；
  - 结构与布局：整体造型（如尖顶塔楼、弧形拱门）、功能分区设计（如隐藏式红石机房、延伸式走廊）、比例与层次感（如多层塔楼的错落分布）；
  - 装饰与亮点：灯光搭配（南瓜灯暖光、萤石冷光）、装饰元素（自定义花纹、羊毛球点缀、红石装置外露/隐藏设计）。
- 若为「整体风景」，聚焦3个维度：
  - 地形与建筑融合：地形利用方式（依山建、沿河分布、峡谷嵌入）、建筑群落的布局逻辑（分散/集中、高低错落）；
  - 环境与植被：植被选择（樱花树、仙人掌、针叶林）、环境适配性（沙漠-砂岩/仙人掌、雪地-雪块/云杉）；
  - 氛围与光影：自然光影（日落余晖、雨夜反光）、人工光影（红石灯闪烁、萤石点缀）、氛围营造（云雾、粒子效果、色彩基调）。

### 三、输出格式与示例规范
1. 必须用**一段式文字**整合所有信息，逻辑顺序：核心定位→整体风格→细节特色→亮点总结；
2. 示例1（单个建筑）：“这是一张写实生存风格的单个建筑图片，整体以深橡木与原石为核心材质，呈现出质朴厚重的乡村小屋质感，屋顶用浅灰色台阶方块模拟瓦片，一侧延伸出木质走廊，栏杆由栅栏方块拼接而成，下方悬挂的南瓜灯散发暖光，小屋周围散落着小麦和甜菜田，后方紧挨着缓坡林地，橡木树叶的绿色与建筑深棕色形成自然呼应，细节处的木门雕花、窗户内侧的书架摆放，以及墙角蔓延的藤蔓，都凸显出生存玩家的细腻创作巧思”；
3. 示例2（整体风景）：“这是一幅奇幻童话风的整体风景图，以粉色樱花林为基底，樱花树用粉色羊毛与树叶方块叠加出蓬松质感，林间蜿蜒着石英小径，旁侧点缀着发光萤石灯，远处矗立着糖果色城堡，城墙由淡紫色混凝土与白色玻璃拼接，塔顶装饰彩色羊毛球，背景是云雾缭绕的雪山（雪块与下界冰方块构建），整体色彩明快柔和，建筑与自然景观高度融合，加上萤石灯的暖光与樱花的粉色碰撞，充满梦幻治愈的氛围”。
"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_image
                            }
                        }
                    ]
                }
            ],
            "thinking": {
                "type": "disabled"
            }
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            if response.status_code == 400:
                # 这种情况一般是 动图，或者不合法的图片，前者大模型不支持，后者大模型会报错。而且GIF动图和普通的图片无法从消息体进行区分。
                self.logger.error(f"图片不合法，大模型返回：\n状态码: {response.status_code}\n响应内容: {response.text}\n图片地址: {image_path}\n") 
                # 这种情况下就不要引发错误，重试了。
                return None
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return content
            
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"分析图片失败: {e}")
            return None
