import argparse
import concurrent.futures
from pathlib import Path
from urllib.request import urlopen
from typing import Dict, List


def download_image(key: int, url: str, dest: Path, progress: Dict[int, List[int]]) -> None:
    """Download a single image to the destination directory with progress tracking."""
    dest.mkdir(parents=True, exist_ok=True)
    filename = url.split('/')[-1] or f'image_{key}'
    target = dest / filename
    with urlopen(url) as response, open(target, 'wb') as out_file:
        size = int(response.getheader('Content-Length', 0))
        progress[key] = [0, size]
        bytes_read = 0
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            out_file.write(chunk)
            bytes_read += len(chunk)
            progress[key][0] = bytes_read
            print(f"{filename}: {bytes_read}/{size if size else '?'} bytes", end='\r')
        progress.pop(key, None)
    print(f"{filename}: Download complete{' ' * 20}")


def main(urls_file: Path, output_dir: Path, workers: int) -> None:
    urls = [line.strip() for line in urls_file.read_text().splitlines() if line.strip()]
    progress: Dict[int, List[int]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(download_image, i, url, output_dir, progress)
            for i, url in enumerate(urls)
        ]
        for future in futures:
            future.result()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallel image downloader")
    parser.add_argument("urls_file", type=Path, help="Path to text file containing image URLs")
    parser.add_argument("output_dir", type=Path, help="Directory where images will be saved")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent workers")
    args = parser.parse_args()
    main(args.urls_file, args.output_dir, args.workers)
