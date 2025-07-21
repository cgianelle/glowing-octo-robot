import argparse
import concurrent.futures
import sys
import threading
from pathlib import Path
from urllib.request import urlopen


def print_progress(completed: int, total: int, active: set[str]) -> None:
    """Print a simple progress bar with active downloads."""
    bar_length = 40
    filled = int(bar_length * completed / total) if total else bar_length
    bar = "#" * filled + "-" * (bar_length - filled)
    active_list = ", ".join(sorted(active)) or "none"
    sys.stdout.write(
        f"\r[{bar}] {completed}/{total} Downloading: {active_list}".ljust(bar_length + 40)
    )
    sys.stdout.flush()
    if completed == total:
        print()


def download_image(
    url: str,
    dest: Path,
    total: int,
    counter: list[int],
    active: set[str],
    lock: threading.Lock,
) -> None:
    """Download a single image to the destination directory."""
    dest.mkdir(parents=True, exist_ok=True)
    filename = url.split('/')[-1] or 'image'
    target = dest / filename

    with lock:
        active.add(filename)
        print_progress(counter[0], total, active)

    try:
        with urlopen(url) as response, open(target, "wb") as out_file:
            out_file.write(response.read())
    finally:
        with lock:
            active.discard(filename)
            counter[0] += 1
            print_progress(counter[0], total, active)


def main(urls_file: Path, output_dir: Path, workers: int) -> None:
    urls = [line.strip() for line in urls_file.read_text().splitlines() if line.strip()]
    total = len(urls)
    counter = [0]
    active: set[str] = set()
    lock = threading.Lock()

    print_progress(0, total, active)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(download_image, url, output_dir, total, counter, active, lock)
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
