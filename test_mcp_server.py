#!/usr/bin/env python
"""
Test script for Script2Video MCP Server.
Demonstrates basic usage of all MCP tools.
"""
import sys
sys.path.insert(0, 'src')

from script2video.mcp_server import (
    create_draft,
    add_scene,
    add_image_track,
    add_voice_track,
    list_drafts,
    get_draft_info,
    export_json
)

def test_basic_workflow():
    """Test basic video creation workflow."""
    print("=" * 60)
    print("Testing Script2Video MCP Server")
    print("=" * 60)

    # 1. Create draft
    print("\n1. Creating draft...")
    result = create_draft(
        resolution_width=1080,
        resolution_height=1920,
        fps=30,
        title="Test Video"
    )
    print(f"   OK {result['message']}")
    draft_id = result['draft_id']

    # 2. Add scene
    print("\n2. Adding scene...")
    result = add_scene(
        draft_id=draft_id,
        duration=8,
        scene_type="INTRO",
        key_point="Opening scene",
        emotion="积极"
    )
    print(f"   OK {result['message']}")

    # 3. Add image track
    print("\n3. Adding image track...")
    result = add_image_track(
        draft_id=draft_id,
        scene_index=0,
        clips=[{
            "desc": "Background image",
            "source": "assets/anime_waifu.png",
            "start": 0,
            "fit_mode": "cover",
            "opacity": 1.0
        }]
    )
    print(f"   OK {result['message']}")

    # 4. Add voice track
    print("\n4. Adding voice track...")
    result = add_voice_track(
        draft_id=draft_id,
        scene_index=0,
        clips=[{
            "desc": "Opening narration",
            "text": "欢迎观看测试视频",
            "start": 0
        }]
    )
    print(f"   OK {result['message']}")

    # 5. List drafts
    print("\n5. Listing all drafts...")
    result = list_drafts()
    print(f"   OK Found {result['total_count']} draft(s)")

    # 6. Get draft info
    print("\n6. Getting draft details...")
    result = get_draft_info(draft_id=draft_id)
    print(f"   OK Title: {result['title']}")
    print(f"   OK Resolution: {result['resolution']['width']}x{result['resolution']['height']}")
    print(f"   OK FPS: {result['fps']}")
    print(f"   OK Scenes: {len(result['scenes'])}")

    # 7. Export JSON
    print("\n7. Exporting to JSON...")
    result = export_json(
        draft_id=draft_id,
        output_path="test_output.json"
    )
    print(f"   OK {result['message']}")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Review test_output.json")
    print("  - Run: render_video(draft_id='test_video', output_path='test.mp4')")
    print("  - Start MCP server: python run_mcp_server.py")

if __name__ == "__main__":
    test_basic_workflow()
