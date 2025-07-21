import argparse
import json
import random
from pathlib import Path


def choose_number(max_value: int) -> int:
    """Return a random integer between 1 and max_value, inclusive."""
    return random.randint(1, max_value)


def print_section(name: str, section: dict) -> str | None:
    """Print details for a game section and return the next section."""

    print("#" * 30)
    print(f"Section: {name}")
    desc = section.get("description")
    if desc:
        print(f"Description: {desc}")

    if "max_time" in section:
        time_val = choose_number(int(section["max_time"]))
        print(f"max_time: {time_val} minutes")
    if "speed" in section:
        speed_val = random.choice(section["speed"])
        print(f"speed: {speed_val}")
    if "intensity" in section:
        intensity_val = random.choice(section["intensity"])
        print(f"intensity: {intensity_val}")
    if "count" in section:
        count_val = choose_number(int(section["count"]))
        print(f"count: {count_val}")

    options = section.get("options")
    if not options:
        return None

    chosen = random.choice(options)
    option_name = chosen.get("option", "")
    print(f"Option: {option_name}")
    option_desc = chosen.get("description")
    if option_desc:
        print(f"Description: {option_desc}")
    input("Press enter when ready to move on\n")

    return chosen.get("next")


def run_game(data: dict) -> None:
    current = "start"
    while True:
        section = data.get(current)
        if section is None:
            print(f"Section '{current}' not found. Exiting.")
            return

        name = section.get("name") or current
        next_section = print_section(name, section)

        if current == "end":
            return

        if not next_section:
            print("Next section not specified. Exiting.")
            return
        current = next_section


def main(json_file: Path) -> None:
    data = json.loads(json_file.read_text())
    run_game(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Command line adventure game")
    parser.add_argument("json_file", type=Path, help="Path to JSON game file")
    args = parser.parse_args()
    main(args.json_file)
