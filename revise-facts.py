#!/usr/bin/env python3
"""Deduplicate and rewrite animal fact arrays in index.html."""

import re
import hashlib
from pathlib import Path

INDEX = Path(__file__).parent / "index.html"
MIN_FACTS = 2
MAX_FACTS = 3

GENERIC_RE = re.compile(
    r"("
    r"is a fascinating \w+!|"
    r"Many kids love learning about|"
    r"have amazing abilities for life in the wild|"
    r"Scientists still discover new things about|"
    r"Their diet helps them stay strong and healthy|"
    r"What they eat fits life in a \w+ home|"
    r"Their body size helps them survive in the wild|"
    r"Compared to other animals, .+ are built for their habitat|"
    r"They make their home in \w+ areas\.?|"
    r"Their \w+ habitat gives them food and shelter"
    r")",
    re.I,
)

FRAGMENT_RE = re.compile(
    r"^(open |they |their |the |and |or |most |many |some )", re.I
)


def norm(text):
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text)


def is_generic(text):
    return bool(GENERIC_RE.search(text or ""))


def is_near_duplicate(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return True
    if na == nb:
        return True
    if na in nb or nb in na:
        shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
        # Drop sentence fragments that repeat part of another fact.
        if len(shorter) >= 12:
            return True
        if len(shorter) >= 0.75 * len(longer):
            return True
    return False


def uniq_facts(facts):
    out = []
    for fact in facts:
        fact = fact.strip()
        if len(fact) < 12:
            continue
        if is_generic(fact):
            continue
        if any(is_near_duplicate(fact, kept) for kept in out):
            continue
        out.append(fact)
    return out


def split_sentences(text):
    if not text:
        return []
    text = text.strip()
    parts = []
    for piece in re.split(r"\s*[—–]\s*", text):
        piece = piece.strip().rstrip(".")
        if len(piece) >= 18 and not FRAGMENT_RE.match(piece):
            if not piece.endswith(("!", "?")):
                piece += "."
            parts.append(piece)
    if len(parts) < 2:
        for piece in re.split(r"\.\s+", text):
            piece = piece.strip().rstrip(".")
            if len(piece) >= 22 and not FRAGMENT_RE.match(piece):
                if not piece.endswith(("!", "?")):
                    piece += "."
                parts.append(piece)
    return parts


def pick_rotating(options, seed, count):
    if not options:
        return []
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    ordered = []
    for i in range(len(options)):
        ordered.append(options[(h + i) % len(options)])
    return ordered[:count]


HABITAT_LIVES = {
    "Grassland": [
        "Open grassy land lets them see danger and prey from far away.",
        "Dry and rainy seasons change what food is easy to find.",
    ],
    "Forest": [
        "Trees and leaf litter give hiding spots and places to raise young.",
        "Forests offer shade, water, and many kinds of food through the year.",
    ],
    "Jungle": [
        "Warm, wet rainforests have thick plants and lots of food.",
        "Layers from forest floor to treetops hold different animals and plants.",
    ],
    "Ocean": [
        "Salt water covers most of our planet, and many animals live there full-time.",
        "Tides, currents, and reefs change where food and shelter are found.",
    ],
    "Arctic": [
        "Long cold winters and short summers shape how animals find food.",
        "Sea ice, tundra, and cold seas are home to tough survivors.",
    ],
    "Desert": [
        "Hot days, cool nights, and little rain make life a daily challenge.",
        "Animals often rest in shade by day and move more when it is cooler.",
    ],
    "Farm": [
        "Fields, barns, and ponds near people give food and shelter.",
        "Farm habitats mix grass, crops, and water in one place.",
    ],
}

HABITAT_DIET = {
    "Grassland": [
        "Meals depend on what plants or prey are common that season.",
        "Grassland hunters and plant-eaters both follow food across open land.",
    ],
    "Forest": [
        "Forest meals change with seasons — nuts, berries, leaves, or prey.",
        "Many forest animals eat what falls to the ground or lives in trees.",
    ],
    "Jungle": [
        "Jungle animals eat fruit, leaves, insects, or other jungle animals.",
        "So much grows year-round that many jungle species rarely go hungry.",
    ],
    "Ocean": [
        "Ocean meals range from tiny plankton to large fish and mammals.",
        "Filter feeders, hunters, and plant-eaters all share the same water.",
    ],
    "Arctic": [
        "Arctic meals are often meat or seafood found on ice or cold shores.",
        "Food can be scarce, so many arctic animals store fat for hard times.",
    ],
    "Desert": [
        "Desert animals eat plants, seeds, insects, or small prey when they find them.",
        "They get much of their water from food, not from drinking often.",
    ],
    "Farm": [
        "Farm animals may eat grain, grass, or food people provide.",
        "Chickens, cows, and other farm animals are fed to match what they need.",
    ],
}

HABITAT_SIZE = {
    "Grassland": [
        "Their size helps them run, hide in grass, or tower over the plains.",
    ],
    "Forest": [
        "Size helps them climb, slip between trees, or stay hidden on the forest floor.",
    ],
    "Jungle": [
        "Some jungle animals are tiny; others are among the largest on Earth.",
    ],
    "Ocean": [
        "Ocean animals range from microscopic to longer than a school bus.",
    ],
    "Arctic": [
        "Thick fur or blubber makes arctic animals look bigger than their bones alone.",
    ],
    "Desert": [
        "Many desert animals are small to lose less water in the heat.",
    ],
    "Farm": [
        "Farm breeds are often chosen for size that fits their job — eggs, milk, or meat.",
    ],
}

TYPE_DIDYOU = {
    "Mammal": [
        "Young mammals often drink mother's milk when they are first born.",
        "Mammals are warm-blooded, so they stay active in cool weather.",
    ],
    "Bird": [
        "Birds lay eggs, and most species care for chicks in a nest.",
        "Feathers keep birds warm and help many species fly.",
    ],
    "Reptile": [
        "Reptiles are cold-blooded and warm up by resting in sun or on warm rocks.",
        "Most reptiles lay eggs, though some give birth to live young.",
    ],
    "Amphibian": [
        "Many amphibians begin life in water and change form as they grow up.",
        "Their thin skin can absorb water, so they need damp places.",
    ],
    "Fish": [
        "Fish breathe with gills that take oxygen from the water.",
        "Most fish lay many eggs because few survive to adulthood.",
    ],
    "Insect": [
        "Insects have six legs and three main body parts — head, thorax, and abdomen.",
        "Many insects change shape completely as they grow, like caterpillars to butterflies.",
    ],
    "Crustacean": [
        "Crustaceans often wear a hard shell and molt to grow larger.",
        "Many have jointed legs and two pairs of antennae.",
    ],
    "Mollusk": [
        "Many mollusks make shells to protect their soft bodies.",
        "Octopuses and slugs are mollusks too — shells are not always visible.",
    ],
    "Arachnid": [
        "Arachnids have eight legs and two body sections, not three like insects.",
        "Spiders, scorpions, and ticks are all arachnids.",
    ],
}

TYPE_FUN = {
    "Mammal": ["Most mammals have hair or fur, even if it is very short."],
    "Bird": ["Bird bones are often hollow, which keeps their bodies lighter for flight."],
    "Reptile": ["Reptiles usually have dry, scaly skin unlike smooth amphibian skin."],
    "Amphibian": ["Amphibians often have moist skin and live near water."],
    "Fish": ["Fish use fins and tails to steer and push through the water."],
    "Insect": ["Insects are the most common animals on land — there are millions of kinds."],
}


def build_category(primary, existing, extras, animal_id, min_count=MIN_FACTS):
    facts = []
    if primary and primary.strip():
        facts.append(primary.strip())
    for part in split_sentences(primary or ""):
        if len(facts) >= MAX_FACTS:
            break
        if not any(is_near_duplicate(part, f) for f in facts):
            facts.append(part)
    for item in existing or []:
        if len(facts) >= MAX_FACTS:
            break
        item = item.strip()
        if is_generic(item) or len(item) < 12:
            continue
        if not any(is_near_duplicate(item, f) for f in facts):
            facts.append(item)
    for item in pick_rotating(extras, animal_id, len(extras)):
        if len(facts) >= MAX_FACTS:
            break
        if not any(is_near_duplicate(item, f) for f in facts):
            facts.append(item)
    facts = uniq_facts(facts)
    while len(facts) < min_count and extras:
        for item in extras:
            if len(facts) >= min_count:
                break
            if not any(is_near_duplicate(item, f) for f in facts):
                facts.append(item)
        break
    return facts[:MAX_FACTS]


def build_all_facts(animal, existing_arrays):
    habitat = animal.get("habitat", "Forest")
    typ = animal.get("type", "Mammal")
    aid = animal["id"]

    return {
        "funFacts": build_category(
            animal.get("funFact", ""),
            existing_arrays.get("funFacts"),
            TYPE_FUN.get(typ, TYPE_FUN["Mammal"]),
            aid + "-fun",
        ),
        "didYouKnowFacts": build_category(
            animal.get("extraFact", ""),
            existing_arrays.get("didYouKnowFacts"),
            TYPE_DIDYOU.get(typ, TYPE_DIDYOU["Mammal"]),
            aid + "-dyk",
        ),
        "livesInFacts": build_category(
            animal.get("livesIn", ""),
            existing_arrays.get("livesInFacts"),
            HABITAT_LIVES.get(habitat, HABITAT_LIVES["Forest"]),
            aid + "-live",
        ),
        "dietFacts": build_category(
            animal.get("diet", ""),
            existing_arrays.get("dietFacts"),
            HABITAT_DIET.get(habitat, HABITAT_DIET["Forest"]),
            aid + "-diet",
        ),
        "sizeFacts": build_category(
            animal.get("size", ""),
            existing_arrays.get("sizeFacts"),
            HABITAT_SIZE.get(habitat, HABITAT_SIZE["Forest"]),
            aid + "-size",
        ),
    }


def json_escape(value):
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def parse_existing_arrays(block):
    arrays = {}
    for key in ("funFacts", "didYouKnowFacts", "livesInFacts", "dietFacts", "sizeFacts"):
        m = re.search(rf"{key}:\s*\[(.*?)\]", block, re.S)
        if m:
            arrays[key] = re.findall(r'"((?:\\.|[^"\\])*)"', m.group(1))
    return arrays


def parse_animal_block(block):
    animal = {}
    for field in (
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
    ):
        m = re.search(rf'{field}:\s*"((?:\\.|[^"\\])*)"', block)
        if m:
            animal[field] = m.group(1)
    return animal if animal.get("id") and animal.get("name") else None


def format_arrays(arrays):
    lines = []
    for key in ("funFacts", "didYouKnowFacts", "livesInFacts", "dietFacts", "sizeFacts"):
        lines.append(f"          {key}: [")
        for value in arrays[key]:
            lines.append(f'            "{json_escape(value)}",')
        lines.append("          ],")
    return "\n".join(lines)


def fact_arrays_span(block):
    start = block.find("          funFacts: [")
    if start == -1:
        return None
    end = block.find("          sizeFacts: [", start)
    if end == -1:
        return None
    end = block.find("],", end)
    if end == -1:
        return None
    return start, end + 2


def replace_arrays(block, arrays):
    span = fact_arrays_span(block)
    snippet = format_arrays(arrays) + "\n"
    if span:
        return block[: span[0]] + snippet + block[span[1] :]
    insert_at = block.rfind("\n        },")
    if insert_at == -1:
        insert_at = block.rfind("\n        }")
    return block[:insert_at] + "\n" + snippet + block[insert_at:]


def main():
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
    updated = 0

    for idx, match in enumerate(markers):
        block_start = match.start() + 1
        block_end = markers[idx + 1].start() + 1 if idx + 1 < len(markers) else len(section)
        block = section[block_start:block_end]
        animal = parse_animal_block(block)
        if not animal:
            chunks.append(block)
            continue

        existing = parse_existing_arrays(block)
        arrays = build_all_facts(animal, existing)
        chunks.append(replace_arrays(block, arrays))
        updated += 1

    rebuilt = section[: markers[0].start() + 1] + "".join(chunks)
    INDEX.write_text(text[:start] + rebuilt + text[end:], encoding="utf-8")
    print(f"Revised facts for {updated} animals.")


if __name__ == "__main__":
    main()
