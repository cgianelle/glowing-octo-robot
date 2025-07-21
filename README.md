# glowing-octo-robot
Codex sandbox

## Image Downloader

`image_downloader.py` is a simple script that downloads images in parallel.

### Usage

1. Create a text file with one image URL per line.
2. Run the script specifying the URL file and destination directory:

```bash
python3 image_downloader.py urls.txt downloaded_images
```

Use `--workers` to control the number of concurrent downloads.
