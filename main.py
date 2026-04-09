from src.script2video import VideoDraft, ImageTrackBuilder, VideoTrackBuilder, VoiceTrackBuilder

# 1. 初始化草稿：竖屏 1080x1920
draft = VideoDraft.create(resolution=(1080, 1920), fps=30, tags=["3D手办"])

# --- 场景 1：梦想照进现实（开场） ---
scene1 = draft.add_scene(scene_type="HOOK", key_point="打破次元壁", emotion="积极",duration=8)
scene1.add_track(
    ImageTrackBuilder()
    .add_clip(
        # desc 作为提示词：高质量、二次元、原画感
        desc="Masterpiece, best quality, anime style, 1girl, vibrant colors, fantasy outfit, glowing background, looking at viewer", 
        source=r"assets/anime_waifu.png", 
        start=0,
        fit_mode="cover",
        opacity=1
    )
    .build()
).add_track(
    VoiceTrackBuilder()
    .add_clip(
        desc="配音1", 
        text="还在为抢不到心仪的手办而遗憾吗？别让你的热爱，只停留在二次元的屏幕里。", 
        start=0
    )
    .build()
)

# --- 场景 2：工业级精度（核心工艺） ---
scene2 = draft.add_scene(scene_type="TECH", key_point="打印细节", emotion="专业",duration=10)
scene2.add_track(
    ImageTrackBuilder()
    .desc("图片展示打印细节")
    .add_clip(
        # desc 作为提示词：机械感、微距、红蜡材质、精密
        desc="Close-up shot of a 3D printer nozzle, red resin material, intricate figurine details emerging, cinematic lighting, 8k resolution, photorealistic", 
        source=r"assets/printing_process.png", 
        start=0,
        fit_mode="cover"
    )
    .build()
).add_track(
    ImageTrackBuilder()
    .add_clip(
        desc="Extreme close up of anime figurine face, flawless resin texture, professional craftsmanship", 
        source=r"assets/detail_zoom.png", 
        start=2,
        fit_mode="contain",
        transform={"position":{"x":0.5,"y":0.15}} # 放在上半部展示细节
    )
    .build()
).add_track(
    VoiceTrackBuilder()
    .add_clip(
        desc="配音2", 
        text="我们采用工业级高精度红蜡打印，0.02毫米层厚，发丝级细节还原。每一处纹理，都经得起放大检视。", 
        start=0
    )
    .build()
)

# --- 场景 3：成品展示与号召（转化） ---
scene3 = draft.add_scene(scene_type="OUTRO", key_point="成品下单", emotion="热情",duration=10)
scene3.add_track(
    ImageTrackBuilder()
    .add_clip(
        # desc 作为提示词：完成品、专业摄影、工作室环境
        desc="Completed painted anime figurine, professional studio lighting, depth of field, bokeh, high-end collectible, luxury display case", 
        source=r"assets/final_product.png", 
        start=0,
        fit_mode="cover"
    )
    .build()
).add_track(
    VoiceTrackBuilder()
    .add_clip(
        desc="配音3", 
        text="现在私信客服发送照片，开启你的私人定制之旅。把你的本命角色，带回家吧！", 
        start=0
    )
    .build()
)

# --- 4. 生成 ---
draft.export_json("3d_print_ad.json")
# draft.render('3d_print_ad.mp4')

print("提示词式广告脚本已构建完成！")