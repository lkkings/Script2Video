# Script2Video MCP Server 完整指南

## 概述

Script2Video MCP Server 是一个基于 Model Context Protocol (MCP) 的视频编辑服务,允许 LLM 通过标准化接口创建和渲染视频。

## 项目结构

```
Script2Video/
├── src/script2video/
│   ├── mcp_server.py          # MCP 服务器实现
│   ├── api/
│   │   ├── draft.py           # VideoDraft API
│   │   └── builders.py        # Track builders
│   ├── models/                # Pydantic 数据模型
│   ├── renderer/              # 视频渲染引擎
│   └── tts/                   # TTS 语音合成
├── run_mcp_server.py          # 服务器启动脚本
├── test_mcp_server.py         # 测试脚本
├── mcp_config.json            # Claude Desktop 配置
└── README_MCP.md              # MCP 使用文档
```

## 已实现的 MCP 工具

### 1. 草稿管理工具

#### `create_draft`
创建新的视频草稿

**参数:**
- `resolution_width`: 视频宽度 (默认: 1920)
- `resolution_height`: 视频高度 (默认: 1080)
- `fps`: 帧率 (默认: 30)
- `title`: 视频标题 (默认: "Untitled Video")

**返回:** 包含 draft_id 和配置信息的字典

#### `list_drafts`
列出所有活动草稿

**返回:** 所有草稿的列表及其详细信息

#### `get_draft_info`
获取草稿的详细信息

**参数:**
- `draft_id`: 草稿 ID

**返回:** 草稿的完整信息,包括场景和轨道

### 2. 场景管理工具

#### `add_scene`
向草稿添加新场景

**参数:**
- `draft_id`: 草稿 ID
- `duration`: 场景时长(秒)
- `scene_type`: 场景类型 (HOOK/INTRO/OUTRO/DEFAULT)
- `key_point`: 关键叙事点 (可选)
- `emotion`: 情感基调 (可选)

### 3. 轨道添加工具

#### `add_image_track`
添加图片轨道

**参数:**
- `draft_id`: 草稿 ID
- `scene_index`: 场景索引
- `clips`: 图片片段列表,每个包含:
  - `desc`: 描述/提示词
  - `source`: 图片文件路径
  - `start`: 开始时间(秒)
  - `opacity`: 不透明度 (0-1)
  - `fit_mode`: 适配模式 (cover/contain/fill)
  - `transform`: 变换参数 (可选)
  - `animation`: 动画效果 (可选)

#### `add_video_track`
添加视频轨道

**参数:**
- `draft_id`: 草稿 ID
- `scene_index`: 场景索引
- `clips`: 视频片段列表,每个包含:
  - `desc`: 描述
  - `source`: 视频文件路径
  - `start`: 开始时间(秒)
  - `in_time`: 源视频内的开始时间
  - `opacity`: 不透明度
  - `fit_mode`: 适配模式
  - `volume`: 音量(dB)
  - `transform`: 变换参数 (可选)
  - `animation`: 动画效果 (可选)

#### `add_voice_track`
添加语音/TTS 轨道

**参数:**
- `draft_id`: 草稿 ID
- `scene_index`: 场景索引
- `clips`: 语音片段列表,每个包含:
  - `desc`: 语音风格描述
  - `text`: 要合成的文本 (≤10 个中文字符)
  - `start`: 开始时间(秒)
  - `tts_config`: TTS 配置 (可选)
  - `volume`: 音量(dB)
  - `add_subtitle`: 是否添加字幕 (默认: True)

#### `add_bgm_track`
添加背景音乐轨道

**参数:**
- `draft_id`: 草稿 ID
- `scene_index`: 场景索引
- `clips`: BGM 片段列表,每个包含:
  - `desc`: 音乐描述
  - `source`: 音频文件路径
  - `start`: 开始时间(秒)
  - `end`: 结束时间(秒)
  - `volume`: 音量(dB, 默认: -12)
  - `fade_in`: 淡入时长 (默认: 0)
  - `fade_out`: 淡出时长 (默认: 0)
  - `loop`: 是否循环 (默认: False)

#### `add_text_track`
添加文字叠加轨道

**参数:**
- `draft_id`: 草稿 ID
- `scene_index`: 场景索引
- `clips`: 文字片段列表,每个包含:
  - `desc`: 文字用途描述
  - `text`: 文字内容 (1-5 个词)
  - `start`: 开始时间(秒)
  - `end`: 结束时间(秒)
  - `style`: 样式参数 (可选)
  - `animation`: 动画效果 (可选)

#### `add_effect_track`
添加视觉效果轨道

**参数:**
- `draft_id`: 草稿 ID
- `scene_index`: 场景索引
- `clips`: 效果片段列表,每个包含:
  - `desc`: 效果描述
  - `effect_type`: 效果类型 (blur/brightness/contrast/grayscale/vignette)
  - `start`: 开始时间(秒)
  - `end`: 结束时间(秒)
  - `params`: 效果参数 (可选)

### 4. 导出和渲染工具

#### `export_json`
导出草稿为 JSON 文件

**参数:**
- `draft_id`: 草稿 ID
- `output_path`: 输出 JSON 文件路径

#### `render_video`
渲染视频文件

**参数:**
- `draft_id`: 草稿 ID
- `output_path`: 输出视频文件路径 (如 output.mp4)
- `verbose`: 是否显示详细日志 (默认: True)

#### `load_from_json`
从 JSON 文件加载草稿

**参数:**
- `json_path`: JSON 文件路径
- `draft_id`: 自定义草稿 ID (可选,默认使用文件名)

## 运行服务器

### 方式 1: Streamable HTTP (开发推荐)

```bash
# 使用 uv 运行
uv run python run_mcp_server.py

# 或直接运行
python run_mcp_server.py
```

服务器将在 `http://127.0.0.1:8000` 启动

### 方式 2: Stdio (Claude Desktop 集成)

```bash
python run_mcp_server.py stdio
```

## Claude Desktop 配置

将以下配置添加到 Claude Desktop 的 MCP 设置中 (`~/.claude/mcp_config.json` 或通过 UI):

```json
{
  "mcpServers": {
    "script2video": {
      "command": "python",
      "args": ["-m", "src.script2video.mcp_server"],
      "cwd": "D:\\Project\\Script2Video",
      "env": {}
    }
  }
}
```

## 使用示例

### 示例 1: 创建简单的竖屏视频

```python
# 1. 创建竖屏草稿 (1080x1920)
create_draft(
    resolution_width=1080,
    resolution_height=1920,
    fps=30,
    title="My Vertical Video"
)

# 2. 添加开场场景
add_scene(
    draft_id="my_vertical_video",
    duration=8,
    scene_type="HOOK",
    key_point="吸引注意",
    emotion="积极"
)

# 3. 添加背景图片
add_image_track(
    draft_id="my_vertical_video",
    scene_index=0,
    clips=[{
        "desc": "Anime style background",
        "source": "assets/background.png",
        "start": 0,
        "fit_mode": "cover"
    }]
)

# 4. 添加配音
add_voice_track(
    draft_id="my_vertical_video",
    scene_index=0,
    clips=[{
        "desc": "Opening narration",
        "text": "欢迎来到我的频道",
        "start": 0
    }]
)

# 5. 渲染视频
render_video(
    draft_id="my_vertical_video",
    output_path="output.mp4"
)
```

### 示例 2: 多场景广告视频

```python
# 创建草稿
create_draft(
    resolution_width=1080,
    resolution_height=1920,
    title="Product Ad"
)

# 场景 1: 开场
add_scene(draft_id="product_ad", duration=5, scene_type="HOOK")
add_image_track(
    draft_id="product_ad",
    scene_index=0,
    clips=[{"desc": "Product hero", "source": "assets/hero.png", "start": 0}]
)
add_voice_track(
    draft_id="product_ad",
    scene_index=0,
    clips=[{"desc": "Hook", "text": "还在为此烦恼吗", "start": 0}]
)

# 场景 2: 产品展示
add_scene(draft_id="product_ad", duration=8, scene_type="DEMO")
add_video_track(
    draft_id="product_ad",
    scene_index=1,
    clips=[{
        "desc": "Product demo",
        "source": "assets/demo.mp4",
        "start": 0,
        "in_time": 0
    }]
)
add_voice_track(
    draft_id="product_ad",
    scene_index=1,
    clips=[{"desc": "Features", "text": "我们的产品特点", "start": 0}]
)

# 场景 3: 行动号召
add_scene(draft_id="product_ad", duration=5, scene_type="OUTRO")
add_image_track(
    draft_id="product_ad",
    scene_index=2,
    clips=[{"desc": "CTA", "source": "assets/cta.png", "start": 0}]
)
add_voice_track(
    draft_id="product_ad",
    scene_index=2,
    clips=[{"desc": "CTA", "text": "立即下单购买", "start": 0}]
)

# 添加背景音乐 (贯穿全片)
add_bgm_track(
    draft_id="product_ad",
    scene_index=0,
    clips=[{
        "desc": "Upbeat background music",
        "source": "assets/bgm.mp3",
        "start": 0,
        "end": 18,
        "volume": -12,
        "fade_in": 1,
        "fade_out": 2
    }]
)

# 渲染
render_video(draft_id="product_ad", output_path="ad.mp4")
```

### 示例 3: 从现有 JSON 加载并修改

```python
# 加载现有 JSON
load_from_json(
    json_path="3d_print_ad.json",
    draft_id="modified_ad"
)

# 获取草稿信息
info = get_draft_info(draft_id="modified_ad")
print(f"Loaded: {info['title']}, {len(info['scenes'])} scenes")

# 添加新场景
add_scene(
    draft_id="modified_ad",
    duration=5,
    scene_type="BONUS"
)

# 渲染修改后的视频
render_video(
    draft_id="modified_ad",
    output_path="modified_ad.mp4"
)
```

## 测试

运行测试脚本验证所有功能:

```bash
uv run python test_mcp_server.py
```

测试脚本会:
1. 创建草稿
2. 添加场景
3. 添加图片和语音轨道
4. 列出所有草稿
5. 获取草稿详情
6. 导出为 JSON

## 架构说明

### 核心组件

1. **FastMCP**: MCP Python SDK 的高级 API,提供装饰器风格的工具定义
2. **VideoDraft API**: 流式视频编辑接口,提供链式调用
3. **Track Builders**: 构建器模式创建各类轨道
4. **MoviePy**: 底层视频渲染引擎
5. **Pydantic Models**: 类型安全的数据模型

### 数据流

```
MCP Tool Call → VideoDraft API → Track Builders → Pydantic Models → Renderer → MoviePy → Video File
```

### 状态管理

服务器使用内存字典 `_drafts` 存储活动草稿。在生产环境中,应该使用:
- Redis 用于会话存储
- PostgreSQL 用于持久化
- S3/OSS 用于媒体资源

## 故障排除

### 问题: 服务器无法启动

**解决方案:**
```bash
# 检查依赖
uv sync

# 检查 Python 版本
uv run python --version  # 应该 >= 3.13

# 测试导入
uv run python -c "from src.script2video.mcp_server import mcp; print('OK')"
```

### 问题: 渲染失败

**可能原因:**
1. 资源文件路径不正确
2. MoviePy 未正确安装
3. 缺少系统依赖 (ffmpeg)

**解决方案:**
```bash
# 检查 ffmpeg
ffmpeg -version

# 启用详细日志
render_video(draft_id="...", output_path="...", verbose=True)
```

### 问题: TTS 失败

**可能原因:**
1. 网络连接问题 (edge-tts 需要网络)
2. TTS 配置错误

**解决方案:**
- 检查网络连接
- 验证 TTS 配置参数
- 查看详细错误日志

## 扩展开发

### 添加新工具

在 `src/script2video/mcp_server.py` 中:

```python
@mcp.tool()
def my_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    """Tool description for LLM"""
    # Implementation
    return {"result": "success"}
```

### 添加新轨道类型

1. 在 `models/clips.py` 中定义新的 Clip 模型
2. 在 `api/builders.py` 中创建对应的 Builder
3. 在 `renderer/processors/` 中实现处理器
4. 在 `mcp_server.py` 中添加对应的 MCP 工具

## 性能优化

### 渲染优化

- 使用较低的 CRF 值 (18-23) 平衡质量和文件大小
- 对于预览,使用较低的分辨率和帧率
- 启用硬件加速 (如果可用)

### 内存优化

- 及时关闭 MoviePy clips
- 清理临时 TTS 音频文件
- 对于大型项目,考虑分段渲染

## 安全考虑

1. **路径验证**: 验证所有文件路径,防止路径遍历攻击
2. **资源限制**: 限制视频时长、分辨率和文件大小
3. **输入验证**: 使用 Pydantic 模型验证所有输入
4. **权限控制**: 在生产环境中添加身份验证和授权

## 参考资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [FastMCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MoviePy 文档](https://zulko.github.io/moviepy/)
- [Pydantic 文档](https://docs.pydantic.dev/)

## 许可证

参见项目根目录的 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request!
