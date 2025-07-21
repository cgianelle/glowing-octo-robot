import argparse
import concurrent.futures
import os
import sys
import threading
from pathlib import Path
from urllib.request import urlopen


_PRINT_LOCK = threading.Lock()
_PREV_LINES = 0


def _render_bar(fraction: float, length: int = 40) -> str:
    filled = int(length * fraction)
    return "#" * filled + "-" * (length - filled)


def print_progress(completed: int, total: int, progress: dict[str, tuple[int, int]]) -> None:
    """Render overall and per-file progress."""
    global _PREV_LINES
    with _PRINT_LOCK:
        if _PREV_LINES:
            sys.stdout.write(f"\033[{_PREV_LINES}A")
        for _ in range(_PREV_LINES):
            sys.stdout.write("\033[2K\n")
        if _PREV_LINES:
            sys.stdout.write(f"\033[{_PREV_LINES}A")

        lines = []
        overall_bar = _render_bar(completed / total if total else 1.0)
        lines.append(f"[{overall_bar}] {completed}/{total}")
        lines.append("------")
        for name, (done, size) in progress.items():
            frac = done / size if size else 0.0
            bar = _render_bar(frac)
            size_display = f"{done}/{size}" if size else f"{done}/?"
            lines.append(f"{name}: [{bar}] {size_display}")

        output = "\n".join(lines)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()
        _PREV_LINES = len(lines)
        if completed == total:
            print()


def download_image(
    url: str,
    dest: Path,
    total: int,
    counter: list[int],
    progress: dict[str, list[int]],
    lock: threading.Lock,
) -> None:
    """Download a single image to the destination directory."""
    dest.mkdir(parents=True, exist_ok=True)
    original_name = url.split("/")[-1] or "image"
    base, ext = os.path.splitext(original_name)
    filename = original_name
    target: Path | None = None

    try:
        with urlopen(url) as response:
            size = int(response.headers.get("Content-Length", "0") or 0)
            with lock:
                name = filename
                i = 1
                while name in progress or (dest / name).exists():
                    name = f"{base}_{i}{ext}"
                    i += 1
                filename = name
                target = dest / filename
                progress[filename] = [0, size]
                print_progress(counter[0], total, progress)

            bytes_read = 0
            with open(target, "wb") as out_file:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    bytes_read += len(chunk)
                    with lock:
                        progress[filename][0] = bytes_read
                        print_progress(counter[0], total, progress)
    finally:
        with lock:
            counter[0] += 1
            progress.pop(filename, None)
            print_progress(counter[0], total, progress)


def main(urls_file: Path, output_dir: Path, workers: int) -> None:
    urls = [line.strip() for line in urls_file.read_text().splitlines() if line.strip()]
    total = len(urls)
    counter = [0]
    progress: dict[str, list[int]] = {}
    lock = threading.Lock()

    print_progress(0, total, progress)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(download_image, url, output_dir, total, counter, progress, lock)
        for url in urls
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallel image downloader")
    parser.add_argument("urls_file", type=Path, help="Path to text file containing image URLs")
    parser.add_argument("output_dir", type=Path, help="Directory where images will be saved")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent workers")
    args = parser.parse_args()
    main(args.urls_file, args.output_dir, args.workers)
