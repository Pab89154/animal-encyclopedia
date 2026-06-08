#!/usr/bin/env python3
"""Map wildlife checklist names to encyclopedia entries and emit JSONL for gaps."""

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
INDEX = ROOT / "index.html"
CHECKLIST_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "Cursor Projets"
    / "country-encyclopedia"
    / "wildlife-animal-names.txt"
)
OUT = ROOT / "animals_checklist.jsonl"
SKIP = {"Coco de mer palms"}

# Checklist name -> existing animal id (generous synonyms and subspecies coverage).
COVERAGE = {
    "Lions": "lion",
    "Elephants": "elephant",
    "African elephants": "african-elephant",
    "Asian elephants": "asian-elephant",
    "Cheetahs": "cheetah",
    "Tigers": "tiger",
    "Bengal tigers": "tiger",
    "Amur tigers": "siberian-tiger",
    "Leopards": "leopard",
    "African wild dogs": "african-wild-dog",
    "Arctic foxes": "arctic-fox",
    "Bison": "bison",
    "Brown bears": "brown-bear",
    "Grizzly bears": "grizzly-bear",
    "Polar bears": "polar-bear",
    "Grey wolves": "gray-wolf",
    "Hippos": "hippo",
    "Koalas": "koala",
    "Kangaroos": "kangaroo",
    "Meerkats": "meerkat",
    "Orangutans": "orangutan",
    "Gorillas": "gorilla",
    "Jaguars": "jaguar",
    "Orcas": "orca",
    "Whales": "whale",
    "Blue whales": "blue-whale",
    "Humpback whales": "humpback-whale",
    "Sperm whales": "sperm-whale",
    "Dolphins": "dolphin",
    "Bottlenose dolphins": "dolphin",
    "Capybaras": "capybara",
    "Moose": "moose",
    "Wildebeest": "wildebeest",
    "Flamingos": "flamingo",
    "Chameleons": "chameleon",
    "Howler monkeys": "howler-monkey",
    "Red pandas": "red-panda",
    "Giant pandas": "panda",
    "Snow leopards": "snow-leopard",
    "Clouded leopards": "clouded-leopard",
    "Peregrine falcons": "peregrine-falcon",
    "Cotton-top tamarins": "cotton-top-tamarin",
    "Coelacanth fish": "coelacanth",
    "Coconut crabs": "coconut-crab",
    "Fennec foxes": "fennec-fox",
    "Flying fish": "flying-fish",
    "Fossa": "fossa",
    "Giant anteaters": "anteater",
    "Komodo dragons": "komodo-dragon",
    "Manatees": "manatee",
    "Mandrills": "mandrill",
    "Manta rays": "manta-ray",
    "Reef manta rays": "manta-ray",
    "Nurse sharks": "nurse-shark",
    "Okapi": "okapi",
    "Arabian oryx": "oryx",
    "Platypuses": "platypus",
    "Proboscis monkeys": "proboscis-monkey",
    "Puffins": "puffin",
    "Quetzals": "resplendent-quetzal",
    "Ring-tailed lemurs": "ring-tailed-lemur",
    "Saiga antelopes": "saiga",
    "Shoebill storks": "shoebill",
    "Three-toed sloths": "sloth",
    "Spectacled bears": "spectacled-bear",
    "Malayan tapirs": "tapir",
    "Vaquita porpoises": "vaquita",
    "Great white sharks": "great-white-shark",
    "Chinese alligators": "alligator",
    "Hornbills": "hornbill",
    "Harpy eagles": "harpy-eagle",
    "Dugongs": "dugong",
    "Alpine ibex": "alpine-ibex",
    "Markhor goats": "markhor",
    "Musk oxen": "musk-ox",
    "Takin": "takin",
    "Wild boars": "wild-boar",
    "Monarch butterflies": "butterfly",
    "Bee hummingbirds": "hummingbird",
    "Kiwi birds": "kiwi",
    "Bald eagles": "eagle",
    "Golden eagles": "eagle",
    "Whale sharks": "whale-shark",
    "African buffalo": "african-buffalo",
    "Cape buffalo": "african-buffalo",
    "Bonobos": "bonobo",
    "Chimpanzees": "chimpanzee",
    "Addax antelopes": "addax",
    "Agoutis": "agouti",
    "Binturongs": "binturong",
    "Barbary macaques": "barbary-macaque",
    "Forest elephants": "african-elephant",
    "Desert-adapted elephants": "african-elephant",
    "African grey parrots": "african-grey-parrot",
    "Grey parrots": "parrot",
    "Atlantic puffins": "puffin",
    "Atlantic spotted dolphins": "dolphin",
    "Hector's dolphins": "dolphin",
    "Irrawaddy dolphins": "river-dolphin",
    "Ganges river dolphins": "river-dolphin",
    "Indus river dolphins": "river-dolphin",
    "Pink river dolphins": "river-dolphin",
    "West Indian manatees": "manatee",
    "West African manatees": "manatee",
    "American flamingos": "flamingo",
    "Greater flamingos": "flamingo",
    "Andean flamingos": "flamingo",
    "Camargue flamingos": "flamingo",
    "West Indian flamingos": "flamingo",
    "Mountain gorillas": "gorilla",
    "Western lowland gorillas": "gorilla",
    "Olive baboons": "baboon",
    "Gelada baboons": "gelada-baboon",
    "Geoffroy's tamarins": "tamarin",
    "Golden lion tamarins": "golden-lion-tamarin",
    "Pileated gibbons": "gibbon",
    "Hoolock gibbons": "gibbon",
    "Japanese macaques": "snow-monkey",
    "Tree kangaroos": "kangaroo",
    "Nile crocodiles": "crocodile",
    "Saltwater crocodiles": "crocodile",
    "Estuarine crocodiles": "crocodile",
    "West African crocodiles": "crocodile",
    "Morelet's crocodiles": "crocodile",
    "Orinoco crocodiles": "crocodile",
    "American crocodiles": "crocodile",
    "Cuban crocodiles": "crocodile",
    "Green sea turtles": "sea-turtle",
    "Green turtles": "sea-turtle",
    "Leatherback sea turtles": "sea-turtle",
    "Hawksbill sea turtles": "sea-turtle",
    "Loggerhead sea turtles": "sea-turtle",
    "Olive ridley sea turtles": "sea-turtle",
    "Hawksbill turtles": "sea-turtle",
    "Grey seals": "seal",
    "Mediterranean monk seals": "seal",
    "Monk seals": "seal",
    "Cape fur seals": "seal",
    "Baikal seals": "seal",
    "Caspian seals": "seal",
    "Saimaa ringed seals": "seal",
    "Southern right whales": "whale",
    "Minke whales": "whale",
    "Dama gazelles": "gazelle",
    "Dorcas gazelles": "gazelle",
    "Sand gazelles": "gazelle",
    "Goitered gazelles": "gazelle",
    "Mountain gazelles": "gazelle",
    "Soemmerring's gazelles": "gazelle",
    "Grey rhebok antelopes": "gazelle",
    "European bison": "bison",
    "Golden jackals": "jackal",
    "Striped hyenas": "hyena",
    "Eurasian lynx": "lynx",
    "Iberian lynx": "lynx",
    "Balkan lynx": "lynx",
    "Amur leopards": "leopard",
    "Persian leopards": "leopard",
    "Caucasian leopards": "leopard",
    "Arabian leopards": "leopard",
    "Anatolian leopards": "leopard",
    "Asiatic cheetahs": "cheetah",
    "Northwest African cheetahs": "cheetah",
    "Eurasian brown bears": "brown-bear",
    "European brown bears": "brown-bear",
    "Syrian brown bears": "brown-bear",
    "Marsican brown bears": "brown-bear",
    "European beavers": "beaver",
    "Eurasian otters": "river-otter",
    "European otters": "river-otter",
    "Smooth-coated otters": "river-otter",
    "Giant otters": "river-otter",
    "White rhinos": "rhino",
    "One-horned rhinos": "rhino",
    "Pygmy hippos": "hippo",
    "Andean condors": "condor",
    "Andean spectacled bears": "spectacled-bear",
    "Bearded vultures": "vulture",
    "Griffon vultures": "vulture",
    "Egyptian vultures": "vulture",
    "King vultures": "vulture",
    "Steller's sea eagles": "eagle",
    "White-tailed eagles": "eagle",
    "Steppe eagles": "eagle",
    "North African ostriches": "ostrich",
    "Somali ostriches": "ostrich",
    "African penguins": "penguin",
    "Humboldt penguins": "penguin",
    "Magellanic penguins": "penguin",
    "Yellow-eyed penguins": "penguin",
    "Dalmatian pelicans": "pelican",
    "Pink-backed pelicans": "pelican",
    "White storks": "stork",
    "Black storks": "stork",
    "Scarlet macaws": "macaw",
    "Hyacinth macaws": "macaw",
    "Przewalski's horses": "horse",
    "Konik horses": "horse",
    "Guanacos": "llama",
    "Bactrian camels": "camel",
    "Baird's tapirs": "tapir",
    "Bezoar ibex": "ibex",
    "Nubian ibex": "ibex",
    "Waliya ibex": "ibex",
    "Red deer": "deer",
    "Marsh deer": "deer",
    "Bukhara deer": "deer",
    "Flying foxes": "bat",
    "Livingstone's fruit bats": "bat",
    "Reef sharks": "shark",
    "Tree-climbing lions": "lion",
    "Mediterranean chameleons": "chameleon",
    "Panther chameleons": "chameleon",
    "Southern ground hornbills": "hornbill",
    "Oriental pied hornbills": "hornbill",
    "Doctor birds": "hummingbird",
    "Pied kingfishers": "kingfisher",
    "Socotra cormorants": "cormorant",
    "Imperial parrots": "parrot",
    "Galápagos giant tortoises": "galapagos-tortoise",
    "Giant tortoises": "galapagos-tortoise",
    "Bongo antelopes": "bongo",
    "Giant ibis birds": "giant-ibis",
    "Nile lechwe antelopes": "nile-lechwe",
    "Palmchat birds": "palmchat",
    "Sitatunga antelopes": "sitatunga",
    "Armenian mouflon sheep": "armenian-mouflon",
    "Birds-of-paradise": "bird-of-paradise",
    "Mouflon sheep": "mouflon",
    "Noddies": "noddy",
    "Red colobus monkeys": "red-colobus",
    "Giant muntjac deer": "giant-muntjac",
    "Aldabra giant tortoises": "aldabra-tortoise",
    "Frigatebirds": "magnificent-frigatebird",
    "São Tomé grosbeak": "sao-tome-grosbeak",
    "Taiwan blue magpies": "taiwan-blue-magpie",
    "Eurasian elk": "elk",
    "Red squirrels": "squirrel",
    "Grey herons": "great-blue-heron",
    "Marmots": "yellow-bellied-marmot",
}

PLURAL_SUFFIXES = [
    ("antelopes", "antelope"),
    ("monkeys", "monkey"),
    ("macaques", "macaque"),
    ("gorillas", "gorilla"),
    ("tortoises", "tortoise"),
    ("grosbeaks", "grosbeak"),
    ("magpies", "magpie"),
    ("noddies", "noddy"),
    ("squirrels", "squirrel"),
    ("herons", "heron"),
    ("marmots", "marmot"),
    ("frigatebirds", "frigatebird"),
    ("ibises", "ibis"),
    ("cranes", "crane"),
    ("warblers", "warbler"),
    ("cormorants", "cormorant"),
    ("pelicans", "pelican"),
    ("storks", "stork"),
    ("eagles", "eagle"),
    ("falcons", "falcon"),
    ("parrots", "parrot"),
    ("penguins", "penguin"),
    ("dolphins", "dolphin"),
    ("whales", "whale"),
    ("sharks", "shark"),
    ("crocodiles", "crocodile"),
    ("turtles", "turtle"),
    ("seals", "seal"),
    ("flamingos", "flamingo"),
    ("gazelles", "gazelle"),
    ("wolves", "wolf"),
    ("bears", "bear"),
    ("otters", "otter"),
    ("beavers", "beaver"),
    ("camels", "camel"),
    ("tapirs", "tapir"),
    ("iguanas", "iguana"),
    ("horses", "horse"),
    ("rhinos", "rhino"),
    ("hippos", "hippo"),
    ("lions", "lion"),
    ("tigers", "tiger"),
    ("leopards", "leopard"),
    ("cheetahs", "cheetah"),
    ("boars", "boar"),
    ("foxes", "fox"),
    ("goats", "goat"),
    ("chameleons", "chameleon"),
    ("butterflies", "butterfly"),
    ("hummingbirds", "hummingbird"),
    ("vultures", "vulture"),
    ("condors", "condor"),
    ("jackals", "jackal"),
    ("hyenas", "hyena"),
    ("bats", "bat"),
    ("crabs", "crab"),
    ("fish", "fish"),
    ("ducks", "duck"),
    ("geese", "goose"),
    ("asses", "ass"),
    ("lemurs", "lemur"),
    ("porpoises", "porpoise"),
    ("tamarins", "tamarin"),
    ("gibbons", "gibbon"),
    ("ostriches", "ostrich"),
    ("macaws", "macaw"),
    ("elephants", "elephant"),
    ("sheep", "sheep"),
    ("elks", "elk"),
    ("cranes", "crane"),
    ("puffins", "puffin"),
    ("crocodiles", "crocodile"),
    ("porcupines", "porcupine"),
    ("wildebeest", "wildebeest"),
    ("capybaras", "capybara"),
    ("koalas", "koala"),
    ("platypuses", "platypus"),
    ("puffins", "puffin"),
]

# Curated facts for animals that still need new encyclopedia entries.
NEW_ANIMAL_SPECS = {
    "Cross River gorillas": {
        "id": "cross-river-gorilla",
        "name": "Cross River Gorilla",
        "emoji": "🦍",
        "type": "Mammal",
        "habitat": "Jungle",
        "livesIn": "Nigeria and Cameroon — misty mountain forests",
        "diet": "Leaves, fruit, bark, and stems from forest plants",
        "size": "About as tall as a strong adult's chest",
        "funFact": "Cross River gorillas are the world's rarest great apes!",
        "extraFact": "They were once thought extinct until rediscovered in the 1980s.",
        "funFacts": [
            "Cross River gorillas are the world's rarest great apes!",
            "Males beat their chests and roar to warn rival groups.",
            "They build cozy leaf nests in trees each night.",
        ],
        "didYouKnowFacts": [
            "They were once thought extinct until rediscovered in the 1980s.",
            "Only a few hundred remain in scattered forest patches.",
            "Their fur is often darker and longer than other gorillas.",
        ],
        "livesInFacts": [
            "Nigeria and Cameroon — misty mountain forests",
            "Steep slopes and thick trees keep them hidden from people.",
            "Small groups roam between forest fragments linked by ridges.",
        ],
        "dietFacts": [
            "Leaves, fruit, bark, and stems from forest plants",
            "They spend hours each day peacefully munching plants.",
            "Seasonal fruit brings whole families to the same trees.",
        ],
        "sizeFacts": [
            "About as tall as a strong adult's chest",
            "Males are much bigger than females, with wide shoulders.",
            "Arms are longer than legs — perfect for climbing.",
        ],
        "lifespanFacts": [
            "In the wild: Cross River gorillas usually live about 35–40 years.",
            "In captivity: With expert care in sanctuaries, gorillas can live into their 40s or 50s.",
            "Often die from: Habitat loss, hunting, disease, and conflict near human villages.",
        ],
        "populationFacts": [
            "Fewer than 350 Cross River gorillas remain in the wild.",
            "They survive only in scattered forests along the Nigeria–Cameroon border.",
        ],
        "conservationFacts": [
            "Status: Critically Endangered — they are the rarest gorilla subspecies.",
            "Forest protection and anti-poaching patrols are vital to their survival.",
        ],
    },
    "Green monkeys": {
        "id": "green-monkey",
        "name": "Green Monkey",
        "emoji": "🐒",
        "type": "Mammal",
        "habitat": "Grassland",
        "livesIn": "West Africa — savannas, forests, and coastal scrub",
        "diet": "Fruit, leaves, flowers, insects, and seeds",
        "size": "About as long as a house cat with a long tail",
        "funFact": "Green monkeys have golden-green fur and white cheek whiskers!",
        "extraFact": "They were brought to Caribbean islands centuries ago.",
        "funFacts": [
            "Green monkeys have golden-green fur and white cheek whiskers!",
            "Troops chatter loudly when they spot a leopard or eagle.",
            "Babies cling to their mother's belly, then ride on her back.",
        ],
        "didYouKnowFacts": [
            "They were brought to Caribbean islands centuries ago.",
            "Males have bright blue scrotums that stand out in sunlight.",
            "They drink water from puddles and river edges at dawn.",
        ],
        "livesInFacts": [
            "West Africa — savannas, forests, and coastal scrub",
            "They sleep in trees at night to stay safe from predators.",
            "Open grassland lets sentinels watch for danger while others feed.",
        ],
        "dietFacts": [
            "Fruit, leaves, flowers, insects, and seeds",
            "Insects give growing youngsters extra protein.",
            "They raid farm crops when wild food is scarce.",
        ],
        "sizeFacts": [
            "About as long as a house cat with a long tail",
            "Long tails help them balance on thin branches.",
            "Adult males are bigger and bolder than females.",
        ],
        "lifespanFacts": [
            "In the wild: Green monkeys usually live about 11–13 years.",
            "In captivity: In zoos with good care, they may live into their late teens.",
            "Often die from: Leopards, eagles, disease, and car accidents near roads.",
        ],
        "populationFacts": [
            "Green monkeys are common in parts of West Africa.",
            "Introduced groups also live on Caribbean islands such as Barbados.",
        ],
        "conservationFacts": [
            "Status: Least Concern — wild populations are still widespread.",
            "They can become pests on farms, so people sometimes trap or relocate them.",
        ],
    },
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def slugify(name):
    text = (
        name.lower()
        .replace("'", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("ã", "a")
        .replace("ô", "o")
        .replace("í", "i")
    )
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"\s+", "-", text.strip())


def load_checklist():
    if CHECKLIST_PATH.exists():
        lines = CHECKLIST_PATH.read_text(encoding="utf-8").splitlines()
    else:
        raise SystemExit(f"Missing checklist file: {CHECKLIST_PATH}")
    items = []
    seen = set()
    for line in lines:
        name = line.strip()
        if not name or name in SKIP:
            continue
        if name not in seen:
            seen.add(name)
            items.append(name)
    return items


def load_existing_animals():
    text = INDEX.read_text(encoding="utf-8")
    start = text.index("const ANIMALS = [")
    section = text[start:]
    animals = []
    for match in re.finditer(
        r'id: "([^"]+)"[\s\S]*?name: "([^"]+)"', section
    ):
        animals.append({"id": match.group(1), "name": match.group(2)})
    ids = {a["id"] for a in animals}
    return animals, ids


def resolve_coverage(item, existing_ids):
    if item in COVERAGE:
        animal_id = COVERAGE[item]
        if animal_id in existing_ids:
            return animal_id

    slug = slugify(item)
    if slug in existing_ids:
        return slug
    if slug.endswith("s") and slug[:-1] in existing_ids:
        return slug[:-1]
    if slug.endswith("es") and slug[:-2] in existing_ids:
        return slug[:-2]

    for suffix, singular in PLURAL_SUFFIXES:
        if slug.endswith("-" + suffix):
            candidate = slug[: -(len(suffix) + 1)] + "-" + singular
            if candidate in existing_ids:
                return candidate

    if item == "Birds-of-paradise" and "bird-of-paradise" in existing_ids:
        return "bird-of-paradise"

    return None


def title_case_words(text):
    small = {"of", "and", "the", "in", "on", "a", "an"}
    words = text.replace("-", " ").split()
    out = []
    for idx, word in enumerate(words):
        if idx and word.lower() in small:
            out.append(word.lower())
        else:
            out.append(word[:1].upper() + word[1:])
    return " ".join(out)


def infer_type(name):
    lower = name.lower()
    rules = [
        (("shark", "whale", "dolphin", "fish", "ray", "eel", "salmon", "tuna"), "Fish"),
        (("frog", "salamander", "newt", "axolotl"), "Amphibian"),
        (("crocodile", "alligator", "turtle", "tortoise", "iguana", "lizard", "snake"), "Reptile"),
        (("eagle", "owl", "hawk", "falcon", "parrot", "penguin", "crane", "stork", "pelican", "flamingo", "ibis", "heron", "vulture", "condor", "hornbill", "kingfisher", "cormorant", "warbler", "ostrich", "puffin", "quetzal", "grosbeak", "magpie", "pigeon", "duck", "goose", "crane", "bird"), "Bird"),
        (("butterfly", "moth", "bee", "ant", "beetle", "dragonfly", "grasshopper", "cicada", "wasp"), "Insect"),
        (("crab", "lobster", "shrimp", "urchin"), "Crustacean"),
        (("octopus", "squid", "snail", "clam", "nautilus"), "Mollusk"),
    ]
    for keywords, animal_type in rules:
        if any(key in lower for key in keywords):
            return animal_type
    return "Mammal"


def infer_habitat(name):
    lower = name.lower()
    if any(k in lower for k in ("penguin", "seal", "walrus", "polar", "arctic", "musk ox", "reindeer", "ptarmigan")):
        return "Arctic"
    if any(k in lower for k in ("shark", "whale", "dolphin", "fish", "ray", "turtle", "crab", "lobster", "pelican", "cormorant", "gull", "seal")):
        return "Ocean"
    if any(k in lower for k in ("camel", "scorpion", "fennec", "jerboa", "sand", "desert", "oryx", "addax")):
        return "Desert"
    if any(k in lower for k in ("gorilla", "orangutan", "chimpanzee", "bonobo", "jaguar", "toucan", "sloth", "poison", "macaw", "tapir", "okapi", "lemur", "monkey", "paradise")):
        return "Jungle"
    if any(k in lower for k in ("horse", "cow", "pig", "sheep", "goat", "chicken", "duck", "goose", "turkey")):
        return "Farm"
    if any(k in lower for k in ("lion", "cheetah", "zebra", "gazelle", "wildebeest", "ostrich", "hyena", "jackal")):
        return "Grassland"
    if any(k in lower for k in ("bear", "wolf", "deer", "fox", "owl", "squirrel", "lynx", "marten", "woodpecker")):
        return "Forest"
    return "Grassland"


def build_template_animal(checklist_name):
    animal_id = slugify(checklist_name)
    animal_id = re.sub(r"-(antelopes|monkeys|macaques|gorillas|tortoises|grosbeaks|magpies|noddies|squirrels|herons|marmots|frigatebirds|ibises|cranes|warblers|cormorants|pelicans|storks|eagles|falcons|parrots|penguins|dolphins|whales|sharks|crocodiles|turtles|seals|flamingos|gazelles|wolves|bears|otters|beavers|camels|tapirs|iguanas|horses|rhinos|hippos|lions|tigers|leopards|cheetahs|boars|foxes|goats|chameleons|butterflies|hummingbirds|vultures|condors|jackals|hyenas|bats|crabs|fish|ducks|geese|asses|lemurs|porpoises|tamarins|gibbons|ostriches|macaws|elephants)$", lambda m: "-" + m.group(1)[:-1] if m.group(1) != "geese" else "-goose", animal_id)
    display = title_case_words(animal_id)
    animal_type = infer_type(checklist_name)
    habitat = infer_habitat(checklist_name)
    lives_in = f"Regions where {display.lower()} live in the wild"
    diet = "Food found in their habitat — plants, prey, or both"
    size = "About as long as your arm"
    fun = f"{display} are amazing animals kids love to learn about!"
    extra = f"Scientists still discover new facts about {display.lower()} every year."
    return {
        "id": animal_id,
        "name": display,
        "emoji": "🐾",
        "type": animal_type,
        "habitat": habitat,
        "livesIn": lives_in,
        "diet": diet,
        "size": size,
        "funFact": fun,
        "extraFact": extra,
        "funFacts": [
            fun,
            f"{display} have special bodies suited to life in {habitat.lower()} areas.",
            f"Young {display.lower()} learn survival skills from parents or the troop.",
        ],
        "didYouKnowFacts": [
            extra,
            f"{display} help their ecosystem stay healthy where they live.",
            f"Protecting habitat is one of the best ways to help {display.lower()}.",
        ],
        "livesInFacts": [
            lives_in,
            f"{habitat} areas give shelter, food, and space to raise young.",
            "Seasonal changes shift where they travel and what they eat.",
        ],
        "dietFacts": [
            diet,
            "Meals change with seasons and what is ripe or active nearby.",
            "Finding clean water is often part of their daily routine.",
        ],
        "sizeFacts": [
            size,
            "Adults are larger than youngsters and may look very different.",
            "Body shape helps them move, hide, or hunt in their habitat.",
        ],
    }


def enrich_animal(base, build_lifespan, build_world):
    animal = dict(base)
    if "lifespanFacts" not in animal:
        lifespan_facts = build_lifespan(animal)
        animal["lifespanFacts"] = list(lifespan_facts)
        animal["lifespan"] = lifespan_facts[0]
    else:
        animal["lifespan"] = animal["lifespanFacts"][0]

    if "populationFacts" not in animal or "conservationFacts" not in animal:
        population_facts, conservation_facts = build_world(animal)
        animal.setdefault("populationFacts", list(population_facts))
        animal.setdefault("conservationFacts", list(conservation_facts))

    animal["population"] = animal["populationFacts"][0]
    animal["conservation"] = animal["conservationFacts"][0]
    return animal


def build_new_animal(checklist_name, build_lifespan, build_world):
    if checklist_name in NEW_ANIMAL_SPECS:
        base = dict(NEW_ANIMAL_SPECS[checklist_name])
    else:
        base = build_template_animal(checklist_name)
    return enrich_animal(base, build_lifespan, build_world)


def main():
    lifespan_mod = load_module("lifespan_facts", ROOT / "add-lifespan-facts.py")
    world_mod = load_module("world_facts", ROOT / "add-world-facts.py")
    build_lifespan = lifespan_mod.build_lifespan
    build_world = world_mod.build_world

    checklist = load_checklist()
    existing_animals, existing_ids = load_existing_animals()

    covered = []
    needs_new = []
    for item in checklist:
        animal_id = resolve_coverage(item, existing_ids)
        if animal_id:
            covered.append((item, animal_id))
        else:
            needs_new.append(item)

    new_animals = []
    seen_ids = set()
    for item in needs_new:
        animal = build_new_animal(item, build_lifespan, build_world)
        if animal["id"] in existing_ids or animal["id"] in seen_ids:
            raise SystemExit(
                f"Generated duplicate id {animal['id']!r} for checklist item {item!r}"
            )
        seen_ids.add(animal["id"])
        new_animals.append(animal)

    with OUT.open("w", encoding="utf-8") as handle:
        for animal in new_animals:
            handle.write(json.dumps(animal, ensure_ascii=False) + "\n")

    print(f"Checklist items (deduped, minus skip): {len(checklist)}")
    print(f"Existing animals in index.html: {len(existing_animals)}")
    print(f"Covered by existing entries: {len(covered)}")
    print(f"New animals needed: {len(new_animals)}")
    if new_animals:
        print("New animal names:")
        for animal in new_animals:
            print(f"  - {animal['name']}")
    print(f"Wrote {len(new_animals)} animals to {OUT.name}")


if __name__ == "__main__":
    main()
