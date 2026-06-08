#!/usr/bin/env python3
"""Remove duplicate facts within and across animal fact sections in index.html."""

import json
import re
from pathlib import Path

INDEX = Path(__file__).parent / "index.html"
PROFILES = Path(__file__).parent / "strong_profiles.json"

MIN_PER_SECTION = {
    "funFacts": 1,
    "didYouKnowFacts": 1,
    "livesInFacts": 2,
    "dietFacts": 2,
    "sizeFacts": 2,
    "lifespanFacts": 3,
    "populationFacts": 2,
    "conservationFacts": 2,
}
MAX_PER_SECTION = 3

SECTIONS = [
    ("funFacts", "funFact"),
    ("didYouKnowFacts", "extraFact"),
    ("livesInFacts", "livesIn"),
    ("dietFacts", "diet"),
    ("sizeFacts", "size"),
    ("lifespanFacts", "lifespan"),
    ("populationFacts", "population"),
    ("conservationFacts", "conservation"),
]


def norm(text):
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text)


def is_near_duplicate(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return True
    if na == nb:
        return True
    if na in nb or nb in na:
        shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
        if len(shorter) >= 12:
            return True
        if len(shorter) >= 0.75 * len(longer):
            return True
    return False


def is_dup_of_any(fact, kept):
    return any(is_near_duplicate(fact, item) for item in kept)


OTHER_PRIMARY = {
    "funFacts": "extraFact",
    "didYouKnowFacts": "funFact",
}


def dedupe_sections(animal):
    global_kept = []
    result = {}

    for array_key, legacy_key in SECTIONS:
        primary = (animal.get(legacy_key) or "").strip()
        blocked_primary = (animal.get(OTHER_PRIMARY.get(array_key, "")) or "").strip()
        pool = []
        if primary:
            pool.append(primary)
        for item in animal.get(array_key) or []:
            item = (item or "").strip()
            if not item or is_dup_of_any(item, pool):
                continue
            if blocked_primary and is_near_duplicate(item, blocked_primary):
                continue
            pool.append(item)

        section_only = array_key in ("funFacts", "didYouKnowFacts")
        cleaned = []
        for item in pool:
            if len(item) < 8:
                continue
            scope = cleaned if section_only else cleaned + global_kept
            if is_dup_of_any(item, scope):
                continue
            cleaned.append(item)
            if not section_only:
                global_kept.append(item)

        min_count = MIN_PER_SECTION[array_key]
        max_count = MAX_PER_SECTION
        if len(cleaned) < min_count:
            for item in animal.get(array_key) or []:
                item = (item or "").strip()
                scope = cleaned if section_only else cleaned + global_kept
                if (
                    len(item) < 8
                    or is_dup_of_any(item, scope)
                    or (blocked_primary and is_near_duplicate(item, blocked_primary))
                ):
                    continue
                cleaned.append(item)
                if not section_only:
                    global_kept.append(item)
                if len(cleaned) >= min_count:
                    break
        if (
            len(cleaned) < min_count
            and primary
            and not is_dup_of_any(primary, cleaned)
            and not (
                not section_only and is_dup_of_any(primary, global_kept)
            )
        ):
            cleaned.insert(0, primary)
            if not section_only:
                global_kept.append(primary)
        elif section_only and primary and not cleaned:
            cleaned = [primary]

        if section_only:
            global_kept.extend(cleaned)

        result[array_key] = cleaned[:max_count]
        result[legacy_key] = result[array_key][0] if result[array_key] else primary

    return result


def json_escape(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def replace_scalar(block, field, value):
    pattern = rf'({field}:\s*")((?:\\.|[^"\\])*)(")'
    if re.search(pattern, block):
        return re.sub(pattern, rf"\1{json_escape(value)}\3", block, count=1)
    return block


def replace_array(block, field, values):
    lines = [f"          {field}: ["]
    for value in values:
        lines.append(f'            "{json_escape(value)}",')
    lines.append("          ],")
    snippet = "\n".join(lines)
    pattern = rf"          {field}:\s*\[[\s\S]*?\],"
    if re.search(pattern, block):
        return re.sub(pattern, snippet, block, count=1)
    return block


def parse_animal_block(block):
    animal = {}
    for array_key, legacy_key in SECTIONS:
        match = re.search(rf'{legacy_key}:\s*"((?:\\.|[^"\\])*)"', block)
        if match:
            animal[legacy_key] = match.group(1)
        array_match = re.search(rf"{array_key}:\s*\[(.*?)\]", block, re.S)
        if array_match:
            animal[array_key] = re.findall(r'"((?:\\.|[^"\\])*)"', array_match.group(1))
    match = re.search(r'id:\s*"([^"]+)"', block)
    if match:
        animal["id"] = match.group(1)
    return animal if animal.get("id") else None


def apply_deduped(block, deduped):
    for array_key, legacy_key in SECTIONS:
        block = replace_scalar(block, legacy_key, deduped[legacy_key])
        block = replace_array(block, array_key, deduped[array_key])
    return block


META_KEYS = ("id", "name", "emoji", "type", "habitat")


def dedupe_profile_dict(profile):
    deduped = dedupe_sections(profile)
    out = dict(profile)
    out.update(deduped)
    return out


def count_cross_dupes(text):
    start = text.index("const ANIMALS = [")
    section = text[start:]
    markers = list(re.finditer(r"\n        \{\n          id: ", section))
    animals_with_dupes = 0

    for idx, match in enumerate(markers):
        bs = match.start() + 1
        be = markers[idx + 1].start() + 1 if idx + 1 < len(markers) else len(section)
        block = section[bs:be]
        animal = parse_animal_block(block)
        if not animal:
            continue
        global_kept = []
        has_dupe = False
        for array_key, legacy_key in SECTIONS:
            for item in animal.get(array_key) or []:
                item = (item or "").strip()
                if not item:
                    continue
                if is_dup_of_any(item, global_kept):
                    has_dupe = True
                    break
                global_kept.append(item)
            if has_dupe:
                break
        if has_dupe:
            animals_with_dupes += 1

    return animals_with_dupes


def main():
    if PROFILES.exists():
        profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
        for aid, profile in profiles.items():
            profiles[aid] = dedupe_profile_dict(profile)
        PROFILES.write_text(
            json.dumps(profiles, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Deduped {len(profiles)} profiles in strong_profiles.json.")

    text = INDEX.read_text(encoding="utf-8")
    before = count_cross_dupes(text)

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
    updated = 0

    for idx, match in enumerate(markers):
        bs = match.start() + 1
        be = markers[idx + 1].start() + 1 if idx + 1 < len(markers) else len(section)
        block = section[bs:be]
        animal = parse_animal_block(block)
        if not animal:
            chunks.append(block)
            continue
        deduped = dedupe_sections(animal)
        chunks.append(apply_deduped(block, deduped))
        updated += 1

    rebuilt = section[: markers[0].start() + 1] + "".join(chunks)
    INDEX.write_text(text[:start] + rebuilt + text[end:], encoding="utf-8")
    after = count_cross_dupes(INDEX.read_text(encoding="utf-8"))
    print(f"Deduped facts for {updated} animals.")
    print(f"Animals with cross-section duplicates: {before} -> {after}")


if __name__ == "__main__":
    main()
