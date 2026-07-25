import argparse
import json
import re
from pathlib import Path

from app.services.vision.openai_provider import OpenAIVisionProvider
from app.services.vision.frame_pack import FrameReference


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one real GPT-5.6 multimodal vision test.")
    parser.add_argument("images", type=Path, nargs="+", help="One or more local image paths")
    parser.add_argument("--prompt", default=None, help="Optional replacement for the safe default prompt")
    parser.add_argument("--model", default=None, help="Optional model override, defaults to OPENAI_MODEL")
    parser.add_argument("--contact-sheet", action="store_true", help="Pack frames into one labeled image")
    parser.add_argument("--context", default="", help="Optional title/OCR/transcript context")
    args = parser.parse_args()

    provider = OpenAIVisionProvider(model=args.model) if args.model else OpenAIVisionProvider()
    if args.contact_sheet:
        frames = [
            FrameReference(path=image, timestamp_seconds=_timestamp_from_name(image, index))
            for index, image in enumerate(args.images, start=1)
        ]
        result = provider.analyze_frame_pack(frames, args.context, args.prompt)
    else:
        result = provider.analyze_image_files(args.images, args.prompt)
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    return 0


def _timestamp_from_name(path: Path, fallback: int) -> float:
    match = re.search(r"_(\d+(?:\.\d+)?)s", path.name)
    return float(match.group(1)) if match else float(fallback)


if __name__ == "__main__":
    raise SystemExit(main())
