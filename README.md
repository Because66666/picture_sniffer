# Picture Sniffer

一个基于 napcatqq 框架的 Minecraft 图片采集与分析工具，用于自动记录、分析和保存 QQ 群中的 Minecraft 建筑图片和设计图。

## 功能特性

- **自动采集**：通过 napcatqq 框架自动获取 QQ 群消息，提取其中的图片
- **实时监听**：通过 WebSocket 实时监听 QQ 群消息，即时处理新图片
- **智能分析**：使用智谱 AI (GLM-4.6v-Flash) 模型分析图片内容，判断是否为 Minecraft 相关图片
- **自动分类**：支持 47 种 Minecraft 建筑风格分类，包括：
  - 中式建筑（古代、大比例、小比例、奇幻、乡野等）
  - 欧式建筑（罗马式、哥特式、巴洛克式、中世纪、维多利亚等）
  - 现代建筑（玻璃幕墙、日式现代、中式现代、赛博朋克等）
  - 自然场景（树木、地形、废墟等）
  - 特殊建筑（工业、科幻、太空、载具等）
  - 其他分类（内饰、雕塑、旗帜等）
- **智能描述**：自动生成图片的中文描述
- **前端展示**：提供静态网页界面，展示所收集的 Minecraft 建筑图片，提供建筑灵感
- **多线程处理**：使用线程池并发处理图片，提高效率
- **进度显示**：实时显示处理进度
- **完整日志**：记录详细的运行日志，便于调试和追踪
- **数据持久化**：使用 SQLite 数据库存储图片信息和元数据
- **错误重试**：支持失败任务自动重试，最大重试次数可配置
- **400 错误处理**：遇到图片下载 400 错误时自动获取新的消息体重试

## 项目结构

```
picture_sniffer/
├── main.py                      # 主程序入口
├── server.py                    # Flask 服务器（前端 API）
├── ws_server.py                 # WebSocket 服务器（实时监听）
├── config.json                  # 配置文件
├── requirements.txt             # 依赖包列表
├── functions/                   # 功能模块
│   ├── __init__.py
│   ├── database.py             # 数据库管理
│   ├── data_fetcher.py         # 数据获取
│   ├── image_analyzer.py       # 图片分析
│   ├── data_storage.py         # 数据存储
│   ├── config_loader.py        # 配置加载
│   └── logger_config.py        # 日志配置
├── website/                     # 前端静态网页
│   ├── src/                    # 源代码
│   │   ├── app/               # Next.js 应用
│   │   ├── components/        # React 组件
│   │   ├── lib/               # 工具库和 API 服务
│   │   └── types/             # TypeScript 类型定义
│   ├── dist/                  # 构建输出目录
│   ├── public/                # 静态资源
│   └── package.json           # 前端依赖配置
├── pictures/                    # 图片存储目录
├── logs/                        # 日志文件目录
├── error/                       # 错误响应保存目录
└── test/                        # 测试文件
```

## 安装说明

### 环境要求

- Python 3.8+
- napcatqq 框架
- 智谱 AI API Key

### 安装步骤

1. 克隆项目

```bash
git clone <repository-url>
cd picture_sniffer
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 安装前端依赖（可选，如需修改前端）

```bash
cd website
npm install
```

4. 配置文件

复制 `config.json.example` 为 `config.json`，并填写配置信息：

```json
{
  "napcat_base_url": "http://localhost:6111",
  "napcat_token": "your_napcat_token",
  "napcat_ws_uri": "ws://localhost:3001",
  "openai_token": "your_zhipu_ai_api_key",
  "openai_base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
  "db_path": "picture_sniffer.db",
  "pictures_dir": "pictures",
  "log_file": "logs/picture_sniffer.log",
  "log_level": "INFO",
  "webui_token": "your_webui_token"
}
```

配置项说明：

- `napcat_base_url`: napcatqq 框架的 API 地址
- `napcat_token`: napcatqq 的认证令牌
- `napcat_ws_uri`: napcatqq 的 WebSocket 地址（用于实时监听）
- `openai_token`: 智谱 AI 的 API Key
- `openai_base_url`: 智谱 AI 的 API 地址（默认即可）
- `db_path`: SQLite 数据库文件路径
- `pictures_dir`: 图片存储目录
- `log_file`: 日志文件路径
- `log_level`: 日志级别（DEBUG、INFO、WARNING、ERROR）
- `webui_token`: 前端网页的认证令牌（用于登录验证）



## 使用方法

### 运行程序

**运行主程序（采集图片）**

```bash
python main.py
```
**运行主程序（导入图片）**

```bash
python main.py --folder <folder_path>
```

**运行 WebSocket 服务器（实时监听）**

```bash
python ws_server.py
```

此程序会通过 WebSocket 实时监听 QQ 群消息，即时处理新发送的图片。

**运行前端服务器**

```bash
python server.py
```

启动后，在浏览器中访问 `http://localhost:5000` 即可查看前端网页。

### 程序流程

**主程序 (main.py)**

1. 获取所有 QQ 群列表
2. 逐个处理每个群组：
   - 获取群组消息（首次运行获取历史消息，后续运行获取新消息）
   - 提取图片消息
   - 使用 AI 分析图片内容
   - 保存 Minecraft 相关图片
   - 更新群组的最新消息 ID
3. 显示处理进度和统计信息

**WebSocket 服务器 (ws_server.py)**

1. 连接到 NapCat WebSocket 服务器
2. 实时监听群消息事件
3. 提取图片消息
4. 使用 AI 分析图片内容
5. 保存 Minecraft 相关图片
6. 持续运行，即时处理新消息

### 数据库结构

**groups 表**：存储群组信息

| 字段 | 类型 | 说明 |
|------|------|------|
| group_id | TEXT | 群组 ID（主键） |
| last_message_id | TEXT | 最新消息 ID |

**images 表**：存储图片信息

| 字段 | 类型 | 说明 |
|------|------|------|
| image_id | TEXT | 图片 ID（消息 ID，主键） |
| image_path | TEXT | 图片文件路径 |
| category | TEXT | 图片分类 |
| description | TEXT | 图片描述 |
| create_time | TEXT | 创建时间 |

## 技术栈

- **Python 3.8+**: 主要编程语言
- **SQLite**: 数据库存储
- **Flask**: Web 服务器和 API
- **WebSocket**: 实时消息监听
- **Next.js**: 前端框架
- **React**: 前端 UI 库
- **TypeScript**: 前端类型系统
- **Tailwind CSS**: 前端样式框架
- **requests**: HTTP 请求
- **智谱 AI (GLM-4.6v-Flash)**: 图片分析
- **ThreadPoolExecutor**: 多线程处理
- **tqdm**: 进度条显示
- **logging**: 日志系统

## 开发计划

- [x] 实现图片下载以及AI处理工作流
- [x] 实现图片导入功能
- [x] 实现实时分析新消息，持续运行
- [x] 开发前端静态网页，用于展示和浏览图片
- [x] 实现分类筛选功能
- [x] 实现关键词搜索功能
- [x] 添加图片分类系统
- [ ] 添加图片质量评估
- [x] 优化前端性能和用户体验

## 注意事项

1. 请确保 napcatqq 框架正常运行
2. 请妥善保管 API Key，不要将其提交到版本控制系统
3. 首次运行主程序会获取历史消息，后续运行只获取新消息
4. WebSocket 服务器会持续运行，实时监听新消息
5. 图片分析需要网络连接，请确保网络通畅
6. 建议定期备份数据库文件
7. 前端服务器默认运行在 `http://localhost:5000`，可在 server.py 中修改端口配置
8. 前端网页需要后端 API 支持，请确保 server.py 正在运行
9. WebSocket 服务器需要配置 `napcat_ws_uri` 和 `napcat_token`

## 许可证

本项目采用 Apache License 2.0 开源协议。

```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件

## 致谢

- [napcatqq](https://github.com/NapNeko/NapCatQQ) - QQ 机器人框架
- [智谱 AI](https://bigmodel.cn/) - 提供图片分析 API
- 所有贡献者
