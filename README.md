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

### Branching follow-up options

Options can include a `followup` section to ask the player a question and
branch based on the response. Each follow-up contains a `prompt` and a
`responses` mapping from player input to the next section. If the input
isn't recognized, a `default` entry may specify where to go next.

Example:

```json
{
  "option": "Open the door",
  "followup": {
    "prompt": "Were you able to open the door? (yes/no)",
    "responses": {
      "yes": "alpha",
      "no": "beta",
      "default": "end"
    }
  }
}
```

When a `followup` block is provided, the option does not need its own
`next` field because the responses determine the next section.

## Web Interface

`web_app.py` provides a minimal web interface using only the Python standard library.
It lets you upload new game JSON files and play them in the browser.
Each section displays its available options so you can choose how the story proceeds.
Run the server with:

```bash
python3 web_app.py
```

Then open `http://localhost:8000` in your browser.  Uploaded games are
stored in the `games/` directory. When a game ends, the page includes a
"Back to home" link so you can return to the list of games.
