# Adventure Game DSL Specification

This document describes the JSON-based domain specific language (DSL) used by
`adventure_game.py` and `web_app.py` to define text adventures.

## Overview

A game file is a JSON object where each key is the name of a **section**. The
value for each section is an object describing the scene, available options and
other attributes. Gameplay always begins in the section named `"start"`.
Sections may transfer control to any other section by name.

The minimal game consists of a `start` section with no options, which immediately
ends the game. Most games will include multiple sections connected through
options.

## Section Fields

A section object may contain the following fields:

| Field       | Type          | Description |
|-------------|---------------|-------------|
| `name`      | string        | Optional display name. Defaults to the section key. |
| `description` | string      | Text shown to the player when the section is entered. |
| `max_time`  | number        | If present, a random integer from `1` to `max_time` is generated and displayed as the time spent in this section. |
| `speed`     | array<string> | List of possible speed values. One is chosen at random and displayed. |
| `intensity` | array<string> | List of possible intensity values. One is chosen at random and displayed. |
| `count`     | number        | Maximum count. A random integer from `1` to `count` is chosen and displayed. |
| `options`   | array<object> | List of options that can be selected from this section. If omitted or empty, the section ends the game. |

### Options

Each entry in the `options` array describes a possible action. The command line
and web versions randomly pick one option when a section is processed.

Option fields:

| Field        | Type   | Description |
|--------------|--------|-------------|
| `option`     | string | Name of the option, shown to the player. |
| `description`| string | Optional text describing the outcome when the option is chosen. |
| `next`       | string | Name of the next section. Omit when using a `followup` block. |
| `followup`   | object | Optional follow-up prompt. See below. |

### Follow‑up Blocks

A `followup` block allows the game to ask the player a question and branch based
on the response. When a `followup` block is present, the option's `next` field is
typically omitted because the follow-up responses determine the next section.

The `followup` object contains:

| Field       | Type            | Description |
|-------------|-----------------|-------------|
| `prompt`    | string          | Text of the question shown to the player. |
| `responses` | object<string,string> | Mapping of user responses to the name of the next section. A `default` entry may be provided for unrecognized input. |

If the player's input does not match any key in `responses`, the `default`
entry is used. If no `default` is provided and the input is unrecognized, the
game ends with an error.

## Game Flow

1. The game starts in the `start` section.
2. The engine prints the section's description and any randomly chosen values
   (`max_time`, `speed`, `intensity`, `count`).
3. An option is selected at random from the section's `options` array.
4. If the option includes a `followup` block, the player is prompted for input
   and the response determines the next section.
5. Otherwise the engine waits for the user to press Enter and then moves to the
   section named in the option's `next` field.
6. Reaching a section with no `options` ends the game. By convention a section
   named `end` serves as the game's conclusion, though any section without
   options will end play.

## Example

```
{
  "start": {
    "name": "Start",
    "description": "The adventure begins.",
    "options": [
      {"option": "Go", "next": "end"}
    ]
  },
  "end": {
    "name": "End",
    "description": "The story is over."
  }
}
```

This JSON represents the simplest possible adventure: choosing the only option
transitions from `start` to `end`.

