# Script2Video MCP Server

这是一个基于 Model Context Protocol (MCP) 的视频编辑服务器,允许 LLM 通过标准化接口创建和渲染视频。

## 功能特性

### 核心工具

1. **create_draft** - 创建新的视频草稿
2. **add_scene** - 添加场景到草稿
3. **add_image_track** - 添加图片轨道
4. **add_video_track** - 添加视频轨道
5. **add_voice_track** - 添加语音/TTS 轨道
6. **add_bgm_track** - 添加背景音乐轨道
7. **add_text_track** - 添加文字叠加轨道
8. **add_effect_track** - 添加视觉效果轨道
9. **export_json** - 导出草稿为 JSON
10. **render_video** - 渲染视频文件
11. **load_from_json** - 从 JSON 加载草稿
12. **list_drafts** - 列出所有活动草稿
13. **get_draft_info** - 获取草稿详细信息

## 安装

确保已安装所有依赖:

```bash
uv sync
```

## 运行服务器

### 方式 1: Streamable HTTP (推荐用于开发)

```bash
uv run run_mcp_server.py
```

服务器将在 `http://127.0.0.1:8000` 启动

### 方式 2: Stdio (用于 Claude Desktop 集成)

```bash
python run_mcp_server.py stdio
```

## Claude Desktop 配置

将以下配置添加到 Claude Desktop 的 MCP 设置中:

```json
{
  "mcpServers": {
    "script2video": {
      "command": "python",
      "args": [
        "run_mcp_server.py",
        "stdio"
      ],
      "cwd": "D:\\Project\\Script2Video"
    }
  }
}
```

## 使用示例

### 示例 1: 创建简单视频

```python
# 1. 创建草稿
create_draft(
    resolution_width=1080,
    resolution_height=1920,
    fps=30,
    title="My Video"
)

# 2. 添加场景
add_scene(
    draft_id="my_video",
    duration=10,
    scene_type="INTRO"
)

# 3. 添加图片轨道
add_image_track(
    draft_id="my_video",
    scene_index=0,
    clips=[{
        "desc": "Background image",
        "source": "assets/background.png",
        "start": 0,
        "fit_mode": "cover"
    }]
)

# 4. 添加语音轨道
add_voice_track(
    draft_id="my_video",
    scene_index=0,
    clips=[{
        "desc": "Narration",
        "text": "欢迎观看我的视频",
        "start": 0
    }]
)

# 5. 渲染视频
render_video(
    draft_id="my_video",
    output_path="output.mp4"
)
```

### 示例 2: 从 JSON 加载并渲染

```python
# 加载现有 JSON
load_from_json(
    json_path="3d_print_ad.json",
    draft_id="ad_video"
)

# 渲染
render_video(
    draft_id="ad_video",
    output_path="ad_output.mp4"
)
```

## 轨道类型说明

### Image Track (图片轨道)
- 静态图片展示
- 支持 transform (位置、缩放、旋转)
- 支持动画效果 (fade_in, slide_in 等)
- fit_mode: cover/contain/fill

### Video Track (视频轨道)
- 视频片段播放
- 支持裁剪 (in_time)
- 支持音量控制
- 支持 transform 和动画

### Voice Track (语音轨道)
- TTS 文字转语音
- 自动生成字幕
- 支持多种语音风格

### BGM Track (背景音乐轨道)
- 背景音乐播放
- 支持淡入淡出
- 支持循环播放
- 音量控制 (dB)

### Text Track (文字轨道)
- 文字叠加显示
- 自定义字体、颜色、位置
- 支持动画效果

### Effect Track (效果轨道)
- 视觉效果: blur, brightness, contrast, grayscale, vignette
- 时间范围控制

## 架构说明

服务器基于 `main.py` 中的实现,使用:
- **FastMCP**: MCP Python SDK 的高级 API
- **VideoDraft API**: 流式视频编辑接口
- **Track Builders**: 构建器模式创建轨道
- **MoviePy**: 底层视频渲染引擎

## 开发

### 添加新工具

在 `src/script2video/mcp_server.py` 中使用 `@mcp.tool()` 装饰器:

```python
@mcp.tool()
def my_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    """Tool description"""
    # Implementation
    return {"result": "success"}
```

### 测试

```bash
# 运行服务器
python run_mcp_server.py

# 在另一个终端测试工具
curl -X POST http://127.0.0.1:8000/tools/create_draft \
  -H "Content-Type: application/json" \
  -d '{"resolution_width": 1920, "resolution_height": 1080}'
```

## 故障排除

### 问题: 服务器无法启动
- 检查是否安装了所有依赖: `uv sync`
- 检查 Python 版本 >= 3.13

### 问题: 渲染失败
- 确保所有资源文件路径正确
- 检查 MoviePy 是否正确安装
- 查看详细日志: `render_video(..., verbose=True)`

### 问题: TTS 失败
- 检查网络连接 (edge-tts 需要网络)
- 验证 TTS 配置是否正确

## 参考

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [FastMCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MoviePy 文档](https://zulko.github.io/moviepy/)
