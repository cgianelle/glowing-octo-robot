import json
import random
import cgi
import html
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

GAMES_DIR = Path(__file__).parent / "games"
GAMES_DIR.mkdir(exist_ok=True)


def choose_number(max_value: int) -> int:
    return random.randint(1, max_value)


def load_game(name: str) -> dict:
    game_file = GAMES_DIR / name
    return json.loads(game_file.read_text())


def render_page(body: str, status: str = "200 OK", headers=None):
    headers = headers or []
    headers.append(("Content-Type", "text/html; charset=utf-8"))
    return status, headers, body.encode("utf-8")


def index_page():
    items = []
    for p in GAMES_DIR.glob("*.json"):
        items.append(f"<li><a href='/play?game={p.name}'>Play {p.name}</a></li>")
    games_list = "\n".join(items) or "<li>No games uploaded</li>"
    body = f"""
    <h1>Adventure Games</h1>
    <ul>{games_list}</ul>
    <h2>Upload New Game</h2>
    <form method='POST' action='/upload' enctype='multipart/form-data'>
        <input type='file' name='file'/>
        <button type='submit'>Upload</button>
    </form>
    """
    return render_page(body)


def handle_upload(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ,
                            keep_blank_values=True)
    file_item = form['file']
    if file_item.filename:
        dest = GAMES_DIR / Path(file_item.filename).name
        dest.write_bytes(file_item.file.read())
        body = "<p>Upload successful.</p><a href='/'>Back to home</a>"
    else:
        body = "<p>No file uploaded.</p><a href='/'>Back to home</a>"
    return render_page(body)


def play_page(environ, params):
    game_name = params.get('game', [''])[0]
    section_name = params.get('section', ['start'])[0]
    choice_idx = params.get('choice', [None])[0]
    data = load_game(game_name)
    section = data.get(section_name)
    if not section:
        return render_page("<p>Section not found.</p>")

    parts = ["<h2>{}</h2>".format(section.get('name', section_name))]
    desc = section.get('description')
    if desc:
        parts.append(f"<p>{desc}</p>")

    if 'max_time' in section:
        time_val = choose_number(int(section['max_time']))
        parts.append(f"<p>max_time: {time_val} minutes</p>")
    if 'speed' in section:
        parts.append(f"<p>speed: {random.choice(section['speed'])}</p>")
    if 'intensity' in section:
        parts.append(f"<p>intensity: {random.choice(section['intensity'])}</p>")
    if 'count' in section:
        parts.append(f"<p>count: {choose_number(int(section['count']))}</p>")

    options = section.get('options')
    if not options:
        parts.append("<p>The end.</p><p><a href='/'>Back to home</a></p>")
        return render_page("".join(parts))

    # If the player has not chosen an option yet, show the list of choices.
    if choice_idx is None:
        items = []
        for idx, opt in enumerate(options):
            label = html.escape(opt.get('option', f'Option {idx + 1}'))
            items.append(
                f"<li><a href='/play?game={game_name}&section={section_name}&choice={idx}'>{label}</a></li>"
            )
        parts.append("<ul>" + "\n".join(items) + "</ul>")
        return render_page("".join(parts))

    # Validate the chosen index.
    try:
        idx = int(choice_idx)
        chosen = options[idx]
    except (ValueError, IndexError):
        parts.append("<p>Invalid choice.</p><p><a href='/'>Back to home</a></p>")
        return render_page("".join(parts))

    # Show the result of the chosen option.
    opt_desc = chosen.get('description')
    if opt_desc:
        parts.append(f"<p>{opt_desc}</p>")

    followup = chosen.get('followup')
    if followup:
        prompt = followup.get('prompt', '')
        followup_json = json.dumps(followup)
        body = "".join(parts) + f"""
        <form method='POST' action='/play'>
            <p>{html.escape(prompt)}</p>
            <input type='hidden' name='game' value='{game_name}'/>
            <input type='hidden' name='followup' value='{html.escape(followup_json)}'/>
            <input type='text' name='answer'/>
            <button type='submit'>Submit</button>
        </form>
        """
        return render_page(body)

    next_section = chosen.get('next')
    if not next_section:
        parts.append("<p>No next section. Game over.</p><p><a href='/'>Back to home</a></p>")
        return render_page("".join(parts))

    body = "".join(parts) + f"""
    <a href='/play?game={game_name}&section={next_section}'>Continue</a>
    """
    return render_page(body)


def handle_followup(params):
    game_name = params.get('game', [''])[0]
    followup_json = params.get('followup', [''])[0]
    answer = params.get('answer', [''])[0].strip().lower()
    try:
        followup = json.loads(followup_json)
    except json.JSONDecodeError:
        return render_page("<p>Error reading followup.</p>")
    responses = followup.get('responses', {})
    next_section = responses.get(answer) or responses.get('default')
    if not next_section:
        return render_page("<p>Unrecognized response and no default specified.</p>")
    headers = [('Location', f'/play?game={game_name}&section={next_section}')]
    return '303 See Other', headers, b''


def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD')
    if path == '/':
        status, headers, body = index_page()
    elif path == '/upload' and method == 'POST':
        status, headers, body = handle_upload(environ)
    elif path == '/play' and method == 'GET':
        params = parse_qs(environ.get('QUERY_STRING', ''))
        status, headers, body = play_page(environ, params)
    elif path == '/play' and method == 'POST':
        try:
            size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        body_bytes = environ['wsgi.input'].read(size)
        params = parse_qs(body_bytes.decode())
        status, headers, body = handle_followup(params)
    else:
        status, headers, body = render_page('<p>Not Found</p>', '404 Not Found')

    start_response(status, headers)
    return [body]


if __name__ == '__main__':
    with make_server('', 8000, application) as server:
        print("Serving on http://localhost:8000")
        server.serve_forever()
