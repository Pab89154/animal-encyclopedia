#!/usr/bin/env python3
"""Add 2-3 facts per category to every animal in index.html."""

import re
from pathlib import Path

INDEX = Path(__file__).parent / "index.html"
MIN_FACTS = 2
MAX_FACTS = 3


def split_sentences(text):
    parts = re.split(r"\s*[—–]\s*|\.\s+(?=[A-Z\"'])", text or "")
    out = []
    for part in parts:
        part = part.strip().rstrip(".")
        if len(part) >= 8:
            out.append(part if part.endswith(("!", "?")) else part + ".")
    return out


def uniq(items):
    seen = set()
    out = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def ensure_facts(primary, fillers):
    facts = uniq([primary] + split_sentences(primary))
    for filler in fillers:
        if len(facts) >= MIN_FACTS:
            break
        facts = uniq(facts + [filler])
    return facts[:MAX_FACTS]


def build_fact_arrays(animal):
    name = animal["name"]
    typ = animal["type"]
    habitat = animal["habitat"]

    # Use revise-facts.py for quality fact arrays; these are only mild backups.
    return {
        "funFacts": ensure_facts(animal["funFact"], []),
        "didYouKnowFacts": ensure_facts(animal["extraFact"], []),
        "livesInFacts": ensure_facts(animal["livesIn"], []),
        "dietFacts": ensure_facts(animal["diet"], []),
        "sizeFacts": ensure_facts(animal["size"], []),
    }


def parse_animal_block(block):
    animal = {}
    for field in [
        "id",
        "name",
        "emoji",
        "type",
        "habitat",
        "livesIn",
        "diet",
        "size",
        "funFact",
        "extraFact",
    ]:
        m = re.search(rf'{field}:\s*"((?:\\.|[^"\\])*)"', block)
        if m:
            animal[field] = m.group(1)
    return animal if animal.get("id") and animal.get("name") else None


def json_escape(value):
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def insert_arrays(block, arrays):
    if "funFacts:" in block:
        return block

    insert_before = block.rfind("        },")
    if insert_before == -1:
        insert_before = block.rfind("        }")

    lines = []
    for key, values in arrays.items():
        lines.append(f"          {key}: [")
        for value in values:
            lines.append(f'            "{json_escape(value)}",')
        lines.append("          ],")

    snippet = "\n".join(lines) + "\n"
    return block[:insert_before] + snippet + block[insert_before:]


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.index("const ANIMALS = [")
    end = text.index("];", start)
    animals_section = text[start:end]

    parts = re.split(r"(\{\s*\n\s*id:)", animals_section)
    rebuilt = parts[0]
    updated = 0

    for i in range(1, len(parts), 2):
        prefix = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        block = prefix + body
        animal = parse_animal_block(block)
        if not animal or animal["id"] == "pending" or animal["name"].startswith("A visitor"):
            rebuilt += block
            continue

        rebuilt += insert_arrays(block, build_fact_arrays(animal))
        updated += 1

    INDEX.write_text(text[:start] + rebuilt + text[end:], encoding="utf-8")
    print(f"Updated {updated} animals with fact arrays.")


if __name__ == "__main__":
    main()
