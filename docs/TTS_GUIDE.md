# TTS 功能说明

## 概述

Script2Video 现在支持完整的 TTS（文本转语音）功能，可以将文本自动转换为语音并添加到视频中。

## 支持的 TTS 提供商

### 1. EdgeTTS（默认）

**特点：**
- 免费使用
- 无需 API 密钥
- 支持多种语言和声音
- 基于 Microsoft Edge 的在线 TTS 服务

**配置示例：**
```python
from script2video import VideoDraft

draft = VideoDraft.create(resolution=(1920, 1080))

# 配置 EdgeTTS（默认）
draft.draft.config.tts.provider = "edge-tts"
draft.draft.config.tts.default_speaker = "zh-CN-XiaoxiaoNeural"
draft.draft.config.tts.default_speed = 1.1
```

**可用的中文声音：**
- `zh-CN-XiaoxiaoNeural` - 晓晓（女声，通用）
- `zh-CN-YunxiNeural` - 云希（男声，通用）
- `zh-CN-YunyangNeural` - 云扬（男声，新闻播报）
- `zh-CN-XiaoyiNeural` - 晓伊（女声，温柔）
- `zh-CN-YunjianNeural` - 云健（男声，运动）
- `zh-CN-XiaoxuanNeural` - 晓萱（女声，客服）

### 2. Azure TTS（云服务）

**特点：**
- 企业级质量
- 支持情感表达（cheerful, sad, angry 等）
- 需要 Azure 订阅和 API 密钥

**配置示例：**
```python
# 设置环境变量
# export AZURE_TTS_KEY="your-api-key"
# export AZURE_TTS_REGION="eastus"

draft.draft.config.tts.provider = "azure"
draft.draft.config.tts.default_speaker = "zh-CN-XiaoxiaoNeural"
```

## 使用方法

### 方法 1：使用 TrackBuilder

```python
from script2video import VideoDraft, TrackBuilder

draft = VideoDraft.create(resolution=(1920, 1080))
scene = draft.add_scene(scene_type="INTRO")

# 添加语音轨道
voice_track = (
    TrackBuilder()
    .voice(
        text="欢迎观看我的视频！",
        start=0,
        tts_config={
            "speaker": "zh-CN-XiaoxiaoNeural",
            "speed": 1.1,
            "emotion": "cheerful"  # 仅 Azure 支持
        },
        volume=-6  # 音量（dB）
    )
    .build()
)

scene.tracks.append(voice_track)
draft.render("output.mp4")
```

### 方法 2：从 JSON 加载

```json
{
  "title": "我的视频",
  "config": {
    "resolution": {"w": 1920, "h": 1080},
    "fps": 30,
    "tts": {
      "provider": "edge-tts",
      "default_speaker": "zh-CN-XiaoxiaoNeural",
      "default_speed": 1.1
    }
  },
  "scenes": [{
    "type": "INTRO",
    "tracks": [{
      "type": "voice",
      "clips": [{
        "start": 0,
        "text": "欢迎观看我的视频！",
        "tts_config": {
          "speaker": "zh-CN-XiaoxiaoNeural",
          "speed": 1.1
        },
        "volume": -6
      }]
    }]
  }]
}
```

```python
from script2video import VideoDraft

draft = VideoDraft.from_json("script.json")
draft.render("output.mp4")
```

## TTS 配置参数

### GlobalConfig.tts

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `provider` | str | "edge-tts" | TTS 提供商（"edge-tts" 或 "azure"） |
| `default_speaker` | str | "zh-CN-XiaoxiaoNeural" | 默认说话人声音 |
| `default_speed` | float | 1.0 | 默认语速（0.5-2.0） |
| `default_emotion` | str | None | 默认情感（仅 Azure） |

### VoiceClip.tts_config

| 参数 | 类型 | 说明 |
|------|------|------|
| `speaker` | str | 说话人声音（覆盖默认值） |
| `speed` | float | 语速（0.5-2.0，覆盖默认值） |
| `emotion` | str | 情感风格（仅 Azure，如 "cheerful", "sad"） |

## 功能特性

### 1. 自动字幕生成

语音轨道会自动生成字幕，字幕样式可通过 `SubtitleConfig` 配置：

```python
draft.draft.config.subtitle.width_ratio = 0.8  # 字幕宽度占 80%
draft.draft.config.subtitle.font_size_ratio = 0.04  # 字体大小占高度 4%
draft.draft.config.subtitle.default_color = "#FFFFFF"  # 白色
```

### 2. 音量控制

支持 dB 音量控制：

```python
voice_track = TrackBuilder().voice(
    text="...",
    start=0,
    tts_config={...},
    volume=-6  # -6dB（降低音量）
)
```

### 3. 语速调节

支持 0.5-2.0 倍速：

```python
tts_config = {
    "speaker": "zh-CN-XiaoxiaoNeural",
    "speed": 1.2  # 1.2 倍速
}
```

### 4. 情感表达（仅 Azure）

Azure TTS 支持情感风格：

```python
tts_config = {
    "speaker": "zh-CN-XiaoxiaoNeural",
    "speed": 1.0,
    "emotion": "cheerful"  # 欢快
}
```

可用情感：`cheerful`, `sad`, `angry`, `fearful`, `disgruntled`, `serious`, `gentle`

## 故障处理

### 1. TTS 失败回退

如果 TTS 合成失败，系统会自动回退到：
- 仅显示字幕
- 根据文字长度估算时长（约 150 字/分钟）

### 2. 临时文件清理

TTS 生成的临时音频文件会在渲染完成后自动清理。

### 3. 日志输出

使用 Python logging 模块输出详细日志：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 性能优化

1. **缓存机制**：相同文本的 TTS 结果可以复用（需自行实现）
2. **并行处理**：多个语音片段可以并行合成（需自行实现）
3. **音频格式**：EdgeTTS 输出 MP3 格式，体积小，加载快

## 示例项目

查看 `examples/tts_example.py` 获取完整示例代码。

## 常见问题

**Q: EdgeTTS 需要网络连接吗？**
A: 是的，EdgeTTS 使用 Microsoft Edge 的在线服务，需要互联网连接。

**Q: 如何获取 Azure TTS API 密钥？**
A: 访问 [Azure Portal](https://portal.azure.com)，创建 Cognitive Services 资源，获取 API 密钥。

**Q: 支持其他语言吗？**
A: 是的，EdgeTTS 和 Azure TTS 都支持多种语言。查看官方文档获取完整语音列表。

**Q: 可以使用本地 TTS 吗？**
A: 可以通过实现 `TTSProvider` 抽象类来添加自定义 TTS 提供商。

## 扩展自定义 TTS

实现自定义 TTS 提供商：

```python
from script2video.renderer.tts import TTSProvider

class MyTTSProvider(TTSProvider):
    async def synthesize(self, text, output_path, speaker=None, speed=1.0, emotion=None, **kwargs):
        # 实现你的 TTS 逻辑
        # 返回 (audio_file_path, duration_in_seconds)
        pass

# 注册提供商
from script2video.renderer.tts import get_tts_provider
# 修改 get_tts_provider 函数添加你的提供商
```
