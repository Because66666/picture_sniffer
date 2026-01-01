import requests
import json
from typing import Dict, Any, Optional


class ImageAnalyzer:
    def __init__(self, api_key: str, api_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"):
        self.api_key = api_key
        self.api_url = api_url

    def analyze_image(self, image_url: str) -> Optional[Dict[str, Any]]:
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
- 赛博朋克立面
- 赛博朋克街区
- 粗野主义建筑
- 东南亚风格建筑
- 波斯风格建筑
- 伊斯兰风格建筑
- 玛雅-阿兹特克/美洲原住民建筑
- 古埃及建筑
- 童话/奇幻风格建筑
- 自然野性建筑
- 科幻建筑
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
- description：简洁描述图片核心内容（如“《我的世界》中由方块搭建的中式宫殿，带飞檐和庭院”“现实中的现代公寓照片，无游戏相关元素”），10-50字为宜。

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
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            "thinking": {
                "type": "enabled"
            }
        }
        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        try:
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
            print(f"分析图片失败: {e}")
            print(f"将返回的内容保存到了response.json")
            with open("response.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            return None
