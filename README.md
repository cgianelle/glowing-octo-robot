# glowing-octo-robot
Codex sandbox

## Image Downloader

`image_downloader.py` is a simple script that downloads images in parallel.

It now displays a simple progress bar using only the Python standard library.
The first line shows overall completion, followed by a separator and one line
per active download with its own bar.

### Usage

1. Create a text file with one image URL per line.
2. Run the script specifying the URL file and destination directory:

```bash
python3 image_downloader.py urls.txt downloaded_images
```

Use `--workers` to control the number of concurrent downloads.
