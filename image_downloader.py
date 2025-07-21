import argparse
import concurrent.futures
from pathlib import Path
from urllib.request import urlopen


def download_image(url: str, dest: Path) -> None:
    """Download a single image to the destination directory."""
    dest.mkdir(parents=True, exist_ok=True)
    filename = url.split('/')[-1] or 'image'
    target = dest / filename
    with urlopen(url) as response, open(target, 'wb') as out_file:
        out_file.write(response.read())


def main(urls_file: Path, output_dir: Path, workers: int) -> None:
    urls = [line.strip() for line in urls_file.read_text().splitlines() if line.strip()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for url in urls:
            executor.submit(download_image, url, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallel image downloader")
    parser.add_argument("urls_file", type=Path, help="Path to text file containing image URLs")
    parser.add_argument("output_dir", type=Path, help="Directory where images will be saved")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent workers")
    args = parser.parse_args()
    main(args.urls_file, args.output_dir, args.workers)
