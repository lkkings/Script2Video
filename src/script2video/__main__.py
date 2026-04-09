"""
CLI entrypoint for Script2Video.
"""
import argparse
from .api.draft import VideoDraft


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Script2Video - JSON-driven video editor"
    )
    parser.add_argument(
        "--json",
        required=True,
        help="Path to input JSON timeline file"
    )
    parser.add_argument(
        "--output",
        default="output.mp4",
        help="Path to output video file (default: output.mp4)"
    )
    args = parser.parse_args()

    # Load timeline from JSON
    print(f"Loading timeline from: {args.json}")
    draft = VideoDraft.from_json(args.json)

    # Render video
    print(f"Rendering video to: {args.output}")
    draft.render(args.output)

    print("Done!")


if __name__ == "__main__":
    main()
