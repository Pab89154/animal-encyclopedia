#!/usr/bin/env python3
"""Insert 99 new animals into index.html from animals_99.jsonl."""

import json
import re
from pathlib import Path

INDEX = Path(__file__).parent / "index.html"
JSONL = Path(__file__).parent / "animals_99.jsonl"


def json_escape(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def format_animal_block(animal):
    lines = [
        "        {",
        f'          id: "{json_escape(animal["id"])}",',
        f'          name: "{json_escape(animal["name"])}",',
        f'          emoji: "{json_escape(animal["emoji"])}",',
        f'          type: "{json_escape(animal["type"])}",',
        f'          habitat: "{json_escape(animal["habitat"])}",',
        f'          livesIn: "{json_escape(animal["livesIn"])}",',
        f'          diet: "{json_escape(animal["diet"])}",',
        f'          size: "{json_escape(animal["size"])}",',
        f'          funFact: "{json_escape(animal["funFact"])}",',
        f'          extraFact: "{json_escape(animal["extraFact"])}",',
    ]
    for key in (
        "funFacts",
        "didYouKnowFacts",
        "livesInFacts",
        "dietFacts",
        "sizeFacts",
    ):
        lines.append(f"          {key}: [")
        for fact in animal[key]:
            lines.append(f'            "{json_escape(fact)}",')
        lines.append("          ],")
    lines.append("")
    lines.append("")
    lines.append("        },")
    return "\n".join(lines)


def load_existing():
    text = INDEX.read_text(encoding="utf-8")
    start = text.index("const ANIMALS = [")
    i = start + len("const ANIMALS = [")
    depth = 1
    while i < len(text) and depth:
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
        i += 1
    block = text[start:i]
    ids = {m[0] for m in re.findall(r'id:\s*"([^"]+)"', block)}
    names = {m[1].lower() for m in re.findall(r'name:\s*"([^"]+)"', block)}
    return text, start, i, ids, names


def main():
    if not JSONL.exists():
        raise SystemExit(f"Missing {JSONL.name} — run build_animals_99_jsonl.py first.")

    text, start, end, existing_ids, existing_names = load_existing()
    animals = []
    for line in JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        animals.append(json.loads(line))

    if len(animals) != 99:
        raise SystemExit(f"Expected 99 animals in JSONL, got {len(animals)}")

    blocks = []
    skipped = []
    for animal in animals:
        if animal["id"] in existing_ids or animal["name"].lower() in existing_names:
            skipped.append(animal["name"])
            continue
        blocks.append(format_animal_block(animal))

    if skipped:
        print("Skipped duplicates:", ", ".join(skipped))

    insert = "\n".join(blocks) + "\n"
    marker = "      ];"
    pos = text.index(marker, start)
    new_text = text[:pos] + insert + text[pos:]
    INDEX.write_text(new_text, encoding="utf-8")
    print(f"Added {len(blocks)} animals ({301 + len(blocks)} total expected).")


if __name__ == "__main__":
    main()
