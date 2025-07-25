import json
import random
from email.parser import BytesParser
from email.policy import default
import os
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
from jinja2 import Environment, FileSystemLoader, select_autoescape

GAMES_DIR = Path(__file__).parent / "games"
GAMES_DIR.mkdir(exist_ok=True)

TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def choose_number(max_value: int) -> int:
    return random.randint(1, max_value)


def load_game(name: str) -> dict:
    game_file = GAMES_DIR / name
    return json.loads(game_file.read_text())


def render_page(body: str, status: str = "200 OK", headers=None):
    headers = headers or []
    headers.append(("Content-Type", "text/html; charset=utf-8"))
    return status, headers, body.encode("utf-8")


def render_template(template: str, status: str = "200 OK", headers=None, **context):
    body = env.get_template(template).render(**context)
    return render_page(body, status, headers)


def index_page():
    games = [p.name for p in GAMES_DIR.glob("*.json")]
    return render_template("index.html", title="Adventure Games", games=games)


def parse_multipart(environ):
    """Parse multipart/form-data from a WSGI environ.

    Returns a mapping of field name to a dict with optional ``filename`` and
    ``content`` keys. Only the request body is read, so callers should not read
    from ``wsgi.input`` afterwards.
    """
    content_type = environ.get('CONTENT_TYPE', '')
    if not content_type.startswith('multipart/form-data'):
        return {}

    content_length = int(environ.get('CONTENT_LENGTH', 0))
    body = environ['wsgi.input'].read(content_length)

    parser = BytesParser(policy=default)
    message = parser.parsebytes(
        f"Content-Type: {content_type}\r\n\r\n".encode() + body
    )

    form = {}
    for part in message.iter_parts():
        name = part.get_param('name', header='content-disposition')
        if not name:
            continue
        form[name] = {
            'filename': part.get_filename(),
            'content': part.get_payload(decode=True),
        }
    return form


def handle_upload(environ):
    form = parse_multipart(environ)
    file_item = form.get('file')
    if file_item and file_item.get('filename'):
        dest = GAMES_DIR / Path(file_item['filename']).name
        dest.write_bytes(file_item['content'])
        message = "Upload successful."
    else:
        message = "No file uploaded."
    return render_template(
        "message.html",
        title="Upload",
        message=message,
        home_link=True,
    )


def play_page(environ, params):
    game_name = params.get('game', [''])[0]
    section_name = params.get('section', ['start'])[0]
    data = load_game(game_name)
    section = data.get(section_name)
    if not section:
        return render_template(
            "message.html",
            title="Error",
            message="Section not found.",
            home_link=True,
        )

    context = {
        "title": section.get("name", section_name),
        "section": section,
        "section_name": section_name,
        "game": game_name,
        "time": choose_number(int(section["max_time"])) if "max_time" in section else None,
        "speed": random.choice(section["speed"]) if "speed" in section else None,
        "intensity": random.choice(section["intensity"]) if "intensity" in section else None,
        "count": choose_number(int(section["count"])) if "count" in section else None,
    }

    options = section.get("options")
    if not options:
        context["end"] = True
        return render_template("play.html", **context)

    chosen = random.choice(options)
    context["chosen_option"] = chosen.get("option")
    context["option_description"] = chosen.get("description")

    followup = chosen.get("followup")
    if followup:
        context["followup"] = followup
        context["followup_json"] = json.dumps(followup)
        return render_template("play.html", **context)

    next_section = chosen.get("next")
    if not next_section:
        context["next_section"] = None
        return render_template("play.html", **context)

    context["next_section"] = next_section
    return render_template("play.html", **context)


def handle_followup(params):
    game_name = params.get('game', [''])[0]
    followup_json = params.get('followup', [''])[0]
    answer = params.get('answer', [''])[0].strip().lower()
    try:
        followup = json.loads(followup_json)
    except json.JSONDecodeError:
        return render_template(
            "message.html",
            title="Error",
            message="Error reading followup.",
            home_link=True,
        )
    responses = followup.get('responses', {})
    next_section = responses.get(answer) or responses.get('default')
    if not next_section:
        return render_template(
            "message.html",
            title="Error",
            message="Unrecognized response and no default specified.",
            home_link=True,
        )
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
    port = int(os.environ.get('PORT', '8000'))
    with make_server('', port, application) as server:
        print(f"Serving on http://localhost:{port}")
        server.serve_forever()
