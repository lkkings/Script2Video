import os
import html
import logging
import asyncio
import base64
import pathlib
import requests
from typing import Optional, Dict

from .base import TTSProvider

logger = logging.getLogger(__name__)

class DashScopeTTSProvider(TTSProvider):
    """DashScope Qwen-Voice TTS provider with pre-enrolled voice support."""

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None, 
        default_speaker: str = "Cherry",
        vc_speaker_map: Optional[Dict] = None,
        vc_model: Optional[str] = None, 
        no_instruct_model: Optional[str] = None, 
        instruct_model: Optional[str] = None, 
    ):
        """
        初始化 DashScope TTS 提供商并在初始化时注册音色。

        Args:
            api_key: DashScope API Key (环境变量: DASHSCOPE_API_KEY)
            region: 基础 URL (默认: https://dashscope.aliyuncs.com)
            vc_speaker_map: 字典，格式为 {"角色名": "参考音频本地路径"}
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.base_url = (base_url or os.getenv("DASHSCOPE_BASE_URL") or "https://dashscope.aliyuncs.com").rstrip('/')
        self.vc_model = vc_model or os.getenv("DASHSCOPE_TTS_VC_MODEL","qwen3-tts-vc-2026-01-22")
        self.instruct_model = instruct_model or os.getenv("DASHSCOPE_TTS_INSTRUCT_MODEL","qwen3-tts-instruct-flash")
        self.no_instruct_model = no_instruct_model  or os.getenv("DASHSCOPE_TTS_MODEL","qwen3-tts-flash")
        self.default_speaker = default_speaker
        if not self.api_key:
            raise ValueError("DashScope API key is required.")

        try:
            import dashscope
            self.dashscope = dashscope
            # 设置 dashscope SDK 的基础 URL
            self.dashscope.base_http_api_url = f"{self.base_url}/api/v1"
            self.dashscope.api_key = self.api_key
        except ImportError:
            raise ImportError("dashscope is not installed. Install it with: pip install dashscope")

        self.vc_speaker_map = vc_speaker_map or {}
        # 存储注册成功后的 voice_id 映射
        self.enrolled_voices: Dict[str, str] = {}

        # 在初始化阶段直接完成音色注册
        if self.vc_speaker_map:
            self._enroll_all_voices()

    def _enroll_all_voices(self):
        """遍历 vc_speaker_map，将所有本地音频注册到 DashScope 控制台"""
        enroll_url = f"{self.base_url}/api/v1/services/audio/tts/customization"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        for speaker_id, audio_path in self.vc_speaker_map.items():
            try:
                path_obj = pathlib.Path(audio_path)
                if not path_obj.exists():
                    logger.error(f"音频文件不存在，跳过注册: {audio_path}")
                    continue

                # 准备 Data URI
                mime_type = "audio/mpeg" if audio_path.endswith(".mp3") else "audio/wav"
                base64_str = base64.b64encode(path_obj.read_bytes()).decode()
                data_uri = f"data:{mime_type};base64,{base64_str}"

                payload = {
                    "model": "qwen-voice-enrollment",
                    "input": {
                        "action": "create",
                        "target_model": "qwen3-tts-vc-2026-01-22",
                        "preferred_name": speaker_id,
                        "audio": {"data": data_uri}
                    }
                }

                logger.info(f"正在为角色 '{speaker_id}' 注册音色...")
                resp = requests.post(enroll_url, json=payload, headers=headers, timeout=30)
                
                if resp.status_code == 200:
                    voice_id = resp.json().get("output", {}).get("voice")
                    if voice_id:
                        self.enrolled_voices[speaker_id] = voice_id
                        logger.info(f"角色 '{speaker_id}' 注册成功，VoiceID: {voice_id}")
                else:
                    logger.error(f"角色 '{speaker_id}' 注册失败: {resp.text}")

            except Exception as e:
                logger.error(f"注册音色过程发生异常: {str(e)}")

    async def synthesize(
        self,
        text: str,
        output_path: str,
        speaker: Optional[str] = None,
        speed: float = 1.0,
        emotion: Optional[str] = None,
        **kwargs
    ) -> tuple[str, float]:
        """
        使用已注册的音色进行合成。
        """
        # 优先从已注册的音色中查找，如果没有则直接使用传入的参数名
        target_voice = self.enrolled_voices.get(speaker)
        
        loop = asyncio.get_event_loop()

        def _do_synthesize():
            if target_voice:
                # 音色克隆
                response = self.dashscope.MultiModalConversation.call(
                    model=self.vc_model,
                    api_key=self.api_key,
                    text=text,
                    voice=target_voice,
                    stream=False
                )
            else:
                voice = speaker or self.default_speaker
                if emotion:
                    response = self.dashscope.MultiModalConversation.call(
                        # 如需使用指令控制功能，请将model替换为qwen3-tts-instruct-flash
                        model=self.instruct_model,
                        # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
                        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key = "sk-xxx"
                        api_key=self.api_key,
                        text=text,
                        voice=voice,
                        instructions=emotion,
                        optimize_instructions=True,
                        stream=False
                    )
                else:
                    response = self.dashscope.MultiModalConversation.call(
                        # 如需使用指令控制功能，请将model替换为qwen3-tts-instruct-flash
                        model=self.instruct_model,
                        # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
                        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key = "sk-xxx"
                        api_key=self.api_key,
                        text=text,
                        voice=voice,
                        stream=False
                    )
            if response.status_code != 200:
                raise RuntimeError(f"TTS合成失败: {response.code} - {response.message}")
            print(response)
            output = response.get("output",{})
            if output:
                audio_url = output["audio"].get("url")
                if audio_url:
                    audio_data = requests.get(audio_url).content
                    with open(output_path, "wb") as f:
                        f.write(audio_data)
                    return output_path
            
            raise ValueError("接口响应中未包含音频内容")

        try:
            final_path = await loop.run_in_executor(None, _do_synthesize)
            # 建议使用具体库获取时长，这里暂时占位
            duration = self.get_audio_duration(final_path)
            return final_path, duration
        except Exception as e:
            logger.error(f"合成任务失败: {e}")
            raise