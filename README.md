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
If multiple images share a filename, the downloader will append a numerical
suffix (e.g. `image_1.jpg`) so that all files are saved without overwriting
each other.

## Adventure Game

`adventure_game.py` is a small command line adventure engine.
It loads a game description from a JSON file and uses random "dice"
rolls to determine how long to perform tasks and which option to
follow next.

### Usage

Run the script with a path to a JSON file:

```bash
python3 adventure_game.py sample_game.json
```

A sample game definition is provided in `sample_game.json`.
