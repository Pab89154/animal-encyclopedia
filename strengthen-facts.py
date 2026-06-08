#!/usr/bin/env python3
"""Replace weak template facts with curated strong profiles.

Pipeline order:
  1. add-world-facts.py  (uses strong_profiles for population/conservation)
  2. strengthen-facts.py (this script — full profile overlay)
  3. revise-facts.py     (dedupe non-profile animals only)
"""

import importlib.util
import json
import re
from pathlib import Path

_DEDUPE = importlib.util.spec_from_file_location(
    "dedupe_facts", Path(__file__).parent / "dedupe-facts.py"
)
_dedupe_mod = importlib.util.module_from_spec(_DEDUPE)
_DEDUPE.loader.exec_module(_dedupe_mod)

INDEX = Path(__file__).parent / "index.html"
PROFILES = Path(__file__).parent / "strong_profiles.json"

WEAK_RE = re.compile(
    r"amazing adaptations|habitats that match their wild range|suited to life in a \w+ home|"
    r"sized for survival in the wild|still learn new things|Many kids love learning|"
    r"rich web of life|They make their home in \w+ areas|"
    r"What they eat helps them stay strong and healthy|"
    r"Their body size helps them survive in the wild|"
    r"Population estimates vary — some mammals|"
    r"Scientists use tracking, cameras, and surveys to estimate wild numbers|"
    r"Status: Least Concern — populations are still large and widespread",
    re.I,
)

TYPE_EMOJI = {
    "Mammal": "🐾",
    "Bird": "🐦",
    "Reptile": "🦎",
    "Amphibian": "🐸",
    "Fish": "🐟",
    "Insect": "🐛",
    "Crustacean": "🦀",
    "Mollusk": "🐚",
    "Arachnid": "🕷️",
    "Invertebrate": "🪼",
}


def json_escape(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def is_weak(block):
    return bool(WEAK_RE.search(block))


def replace_field(block, field, value):
    pattern = rf'({field}:\s*")((?:\\.|[^"\\])*)(")'
    if re.search(pattern, block):
        return re.sub(pattern, rf"\1{json_escape(value)}\3", block, count=1)
    return block


def replace_array(block, field, values):
    lines = [f"          {field}: ["]
    for v in values:
        lines.append(f'            "{json_escape(v)}",')
    lines.append("          ],")
    snippet = "\n".join(lines)
    pattern = rf"          {field}:\s*\[[\s\S]*?\],"
    if re.search(pattern, block):
        return re.sub(pattern, snippet, block, count=1)
    return block


def apply_profile(block, profile):
    block = replace_field(block, "name", profile["name"])
    block = replace_field(block, "habitat", profile["habitat"])
    for field in ("livesIn", "diet", "size", "funFact", "extraFact", "lifespan", "population", "conservation"):
        block = replace_field(block, field, profile[field])
    for field in (
        "funFacts",
        "didYouKnowFacts",
        "livesInFacts",
        "dietFacts",
        "sizeFacts",
        "lifespanFacts",
        "populationFacts",
        "conservationFacts",
    ):
        block = replace_array(block, field, profile[field])
    return block


def main():
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
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
    end = i

    section = text[start:end]
    markers = list(re.finditer(r"\n        \{\n          id: ", section))
    chunks = []
    strengthened = 0

    for idx, match in enumerate(markers):
        bs = match.start() + 1
        be = markers[idx + 1].start() + 1 if idx + 1 < len(markers) else len(section)
        block = section[bs:be]
        m = re.search(r'id:\s*"([^"]+)"', block)
        aid = m.group(1) if m else None
        if aid in profiles and (is_weak(block) or aid in profiles):
            block = apply_profile(block, _dedupe_mod.dedupe_profile_dict(profiles[aid]))
            strengthened += 1
        chunks.append(block)

    rebuilt = section[: markers[0].start() + 1] + "".join(chunks)
    INDEX.write_text(text[:start] + rebuilt + text[end:], encoding="utf-8")
    print(f"Strengthened {strengthened} animals.")


if __name__ == "__main__":
    main()
