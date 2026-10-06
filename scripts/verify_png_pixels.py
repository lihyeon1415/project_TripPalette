"""Compare decoded PNG pixels between two directory trees.

This is a development utility for proving that lossless PNG optimization did
not change dimensions, color mode, animation frames, or decoded pixel bytes.
Files with a .png suffix that are not valid PNG images are compared byte for
byte instead.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decoded_fingerprint(path: Path) -> tuple[object, ...]:
    try:
        with Image.open(path) as image:
            frames: list[tuple[object, ...]] = []
            frame_count = getattr(image, "n_frames", 1)
            for frame_number in range(frame_count):
                image.seek(frame_number)
                image.load()
                frames.append(
                    (
                        image.size,
                        image.mode,
                        hashlib.sha256(image.tobytes()).hexdigest(),
                    )
                )
            return ("decoded", image.format, frame_count, tuple(frames))
    except (UnidentifiedImageError, OSError):
        return ("binary", file_hash(path))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()

    before_files = {
        path.relative_to(args.before)
        for path in args.before.rglob("*")
        if path.is_file() and path.suffix.lower() == ".png"
    }
    after_files = {
        path.relative_to(args.after)
        for path in args.after.rglob("*")
        if path.is_file() and path.suffix.lower() == ".png"
    }

    failures: list[str] = []
    if before_files != after_files:
        for path in sorted(before_files - after_files):
            failures.append(f"missing after optimization: {path}")
        for path in sorted(after_files - before_files):
            failures.append(f"new after optimization: {path}")

    decoded_count = 0
    binary_count = 0
    for relative_path in sorted(before_files & after_files):
        before = decoded_fingerprint(args.before / relative_path)
        after = decoded_fingerprint(args.after / relative_path)
        if before[0] == "decoded":
            decoded_count += 1
        else:
            binary_count += 1
        if before != after:
            failures.append(f"content mismatch: {relative_path}")

    print(
        f"checked={len(before_files & after_files)} "
        f"decoded_png={decoded_count} binary_fallback={binary_count} "
        f"mismatches={len(failures)}"
    )
    for failure in failures:
        print(failure)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
