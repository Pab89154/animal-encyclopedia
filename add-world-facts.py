#!/usr/bin/env python3
"""Add populationFacts and conservationFacts to every animal in index.html.

Curated animals in strong_profiles.json keep their population/conservation facts
instead of generic type templates. Run strengthen-facts.py after this script to
re-apply full profiles if needed.
"""

import hashlib
import json
import re
from pathlib import Path

INDEX = Path(__file__).parent / "index.html"
PROFILES_PATH = Path(__file__).parent / "strong_profiles.json"

# population: (line1, line2), conservation: (line1, line2)
WORLD_DATA = {
    "lion": {
        "population": (
            "About 20,000 African lions remain in the wild today.",
            "Most live in protected parks in eastern and southern Africa.",
        ),
        "conservation": (
            "Status: Vulnerable — numbers have dropped sharply since the 1950s.",
            "Habitat loss, fewer prey, and conflict with people are the biggest threats.",
        ),
    },
    "tiger": {
        "population": (
            "Roughly 4,500 wild tigers remain worldwide.",
            "Most live in India, with smaller groups in Russia and Southeast Asia.",
        ),
        "conservation": (
            "Status: Endangered — very few are left compared to a century ago.",
            "Poaching, habitat loss, and fewer prey animals threaten every tiger population.",
        ),
    },
    "elephant": {
        "population": (
            "About 415,000 African elephants live in the wild.",
            "Asian elephants number roughly 50,000 — far fewer than African elephants.",
        ),
        "conservation": (
            "Status: Endangered (Asian) and Vulnerable (African) — both need protection.",
            "Poaching for ivory and habitat loss are the main dangers.",
        ),
    },
    "giraffe": {
        "population": (
            "Around 117,000 giraffes remain in Africa.",
            "Some types of giraffe have far smaller populations than others.",
        ),
        "conservation": (
            "Status: Vulnerable — numbers fell about 30% in roughly three decades.",
            "Habitat loss, drought, and poaching put pressure on remaining herds.",
        ),
    },
    "zebra": {
        "population": (
            "Hundreds of thousands of zebras still roam African grasslands.",
            "Plains zebras are the most common; mountain zebras are much rarer.",
        ),
        "conservation": (
            "Status: Plains zebra — Least Concern; mountain zebra — Vulnerable.",
            "Some zebra types are safe for now; others need active protection.",
        ),
    },
    "cheetah": {
        "population": (
            "Fewer than 7,000 cheetahs remain in the wild.",
            "Most live in southern and eastern Africa; a tiny group survives in Iran.",
        ),
        "conservation": (
            "Status: Vulnerable — one of the rarest big cats on Earth.",
            "Habitat loss, conflict with farmers, and low genetic diversity hurt cheetahs.",
        ),
    },
    "rhino": {
        "population": (
            "About 27,000 rhinos remain worldwide (white, black, and Asian species).",
            "Northern white rhinos are nearly gone — only a tiny captive group survives.",
        ),
        "conservation": (
            "Status: Critically Endangered to Near Threatened, depending on species.",
            "Poaching for horns is the greatest threat to every rhino species.",
        ),
    },
    "gorilla": {
        "population": (
            "Roughly 316,000 western gorillas and about 1,000 mountain gorillas remain.",
            "Mountain gorillas live only in a few forest patches in central Africa.",
        ),
        "conservation": (
            "Status: Endangered to Critically Endangered, depending on species.",
            "Forest clearing, disease, and hunting have shrunk gorilla numbers badly.",
        ),
    },
    "orangutan": {
        "population": (
            "About 104,000 Bornean and 13,000 Sumatran orangutans remain.",
            "Both species live only on the islands of Borneo and Sumatra.",
        ),
        "conservation": (
            "Status: Critically Endangered — among the closest apes to extinction.",
            "Palm-oil farming and logging destroy the forests they need to survive.",
        ),
    },
    "panda": {
        "population": (
            "About 1,860 giant pandas live in the wild in China.",
            "Another few hundred live in zoos and breeding centers.",
        ),
        "conservation": (
            "Status: Vulnerable — a big recovery from fewer than 1,000 in the 1970s.",
            "Bamboo forest loss and climate change could still threaten pandas.",
        ),
    },
    "polar-bear": {
        "population": (
            "An estimated 22,000–31,000 polar bears live across the Arctic.",
            "They are spread across Canada, Greenland, Norway, Russia, and Alaska.",
        ),
        "conservation": (
            "Status: Vulnerable — warming Arctic threatens their sea-ice hunting grounds.",
            "Melting ice, pollution, and conflict with people put polar bears at risk.",
        ),
    },
    "blue-whale": {
        "population": (
            "About 10,000–25,000 blue whales exist today.",
            "That is a comeback from near extinction — but still far below historic levels.",
        ),
        "conservation": (
            "Status: Endangered — still recovering from centuries of whaling.",
            "Ship strikes, fishing gear, and ocean noise remain serious dangers.",
        ),
    },
    "whale": {
        "population": (
            "Population varies hugely by species — from thousands to hundreds of thousands.",
            "Many large whales are still far below their numbers before commercial whaling.",
        ),
        "conservation": (
            "Status: Many species are Endangered or Vulnerable; some are recovering.",
            "Ship strikes, fishing nets, and pollution threaten whales worldwide.",
        ),
    },
    "orca": {
        "population": (
            "Roughly 50,000 orcas live in oceans worldwide.",
            "Some local groups are very small and may be at risk of disappearing.",
        ),
        "conservation": (
            "Status: Data Deficient globally — some populations are Endangered.",
            "Pollution, prey loss, and captivity have hurt certain orca communities.",
        ),
    },
    "sea-turtle": {
        "population": (
            "All seven sea turtle species together number in the hundreds of thousands.",
            "Leatherbacks and hawksbills are among the rarest sea turtles.",
        ),
        "conservation": (
            "Status: Most species are Endangered or Vulnerable.",
            "Plastic, fishing nets, egg poaching, and beach development threaten turtles.",
        ),
    },
    "koala": {
        "population": (
            "Roughly 100,000–500,000 koalas remain in Australia (estimates vary).",
            "Some local populations have collapsed after wildfires and disease.",
        ),
        "conservation": (
            "Status: Vulnerable — numbers are falling across eastern Australia.",
            "Habitat loss, dog attacks, car hits, and disease hit koalas hard.",
        ),
    },
    "red-panda": {
        "population": (
            "Fewer than 10,000 red pandas remain in the wild.",
            "They live in mountain forests in Nepal, India, Bhutan, China, and Myanmar.",
        ),
        "conservation": (
            "Status: Endangered — populations are small and still shrinking.",
            "Forest clearing and poaching are the main threats to red pandas.",
        ),
    },
    "snow-leopard": {
        "population": (
            "An estimated 4,000–6,500 snow leopards remain in Central Asian mountains.",
            "They are spread across 12 countries in very rugged terrain.",
        ),
        "conservation": (
            "Status: Vulnerable — hard to count, but experts believe numbers are falling.",
            "Poaching, habitat loss, and climate change threaten snow leopards.",
        ),
    },
    "african-wild-dog": {
        "population": (
            "About 6,600 African wild dogs remain in fewer than 40 populations.",
            "They once ranged across much of Africa.",
        ),
        "conservation": (
            "Status: Endangered — one of Africa's rarest carnivores.",
            "Habitat loss, disease, and conflict with people keep numbers low.",
        ),
    },
    "hippo": {
        "population": (
            "Roughly 115,000–130,000 hippos live in Africa.",
            "The largest populations are in Zambia, Tanzania, and Mozambique.",
        ),
        "conservation": (
            "Status: Vulnerable — numbers have declined in many countries.",
            "Hunting, habitat loss, and drought threaten hippo populations.",
        ),
    },
    "wolf": {
        "population": (
            "About 250,000–300,000 wolves live worldwide.",
            "Most are in Canada, Russia, and the northern United States.",
        ),
        "conservation": (
            "Status: Least Concern globally — but some local populations are endangered.",
            "Hunting, habitat loss, and conflict with ranchers hurt wolves in some regions.",
        ),
    },
    "bear": {
        "population": (
            "Hundreds of thousands of brown bears live across North America and Eurasia.",
            "Exact counts are hard because bears roam huge territories.",
        ),
        "conservation": (
            "Status: Least Concern — large populations remain in wilderness areas.",
            "Habitat loss and hunting still threaten bears near human settlements.",
        ),
    },
    "brown-bear": {
        "population": (
            "Hundreds of thousands of brown bears live across North America and Eurasia.",
            "Exact counts are hard because bears roam huge territories.",
        ),
        "conservation": (
            "Status: Least Concern — large populations remain in wilderness areas.",
            "Habitat loss and hunting still threaten bears near human settlements.",
        ),
    },
    "deer": {
        "population": (
            "Millions of white-tailed deer live in North America alone.",
            "Deer are among the most common large mammals in many forests.",
        ),
        "conservation": (
            "Status: Least Concern — populations are large and widespread.",
            "Car hits and hunting are common, but deer numbers stay high in many areas.",
        ),
    },
    "fox": {
        "population": (
            "Millions of red foxes live across Europe, Asia, and North America.",
            "They adapt well to farms, suburbs, and wild country.",
        ),
        "conservation": (
            "Status: Least Concern — one of the world's most widespread carnivores.",
            "Roads, disease, and hunting affect local foxes but not the species overall.",
        ),
    },
    "robin": {
        "population": (
            "Roughly 310 million American robins live in North America.",
            "They are one of the most common backyard birds in the United States.",
        ),
        "conservation": (
            "Status: Least Concern — large, stable populations.",
            "Cats, pesticides, and cold snaps kill many robins, but numbers stay strong.",
        ),
    },
    "penguin": {
        "population": (
            "About 595,000 emperor penguins live in Antarctica (2020 estimate).",
            "Other penguin species range from thousands to several million birds.",
        ),
        "conservation": (
            "Status: Many species are Vulnerable or Endangered; emperors are Near Threatened.",
            "Climate change, fishing, and oil spills threaten different penguin species.",
        ),
    },
    "shark": {
        "population": (
            "Population varies by species — some number in millions, others in thousands.",
            "Many shark species have declined sharply from overfishing.",
        ),
        "conservation": (
            "Status: Many species are Vulnerable or Endangered.",
            "Overfishing and finning have cut shark numbers dramatically worldwide.",
        ),
    },
    "bee": {
        "population": (
            "Trillions of honeybees live in managed hives and wild colonies worldwide.",
            "Exact wild counts are impossible — bees are too small and widespread.",
        ),
        "conservation": (
            "Status: Domestic honeybee — not endangered; some wild bee species are at risk.",
            "Pesticides, mites, and habitat loss threaten many bee species.",
        ),
    },
    "butterfly": {
        "population": (
            "Millions to billions of butterflies exist — counts vary by species and season.",
            "Monarch butterflies have declined badly in North America.",
        ),
        "conservation": (
            "Status: Most butterflies — Least Concern; monarchs are Near Threatened.",
            "Habitat loss, pesticides, and climate change hurt many butterfly populations.",
        ),
    },
    "dog": {
        "population": (
            "About 900 million dogs live worldwide — pets, working dogs, and strays.",
            "They are the most common carnivore on Earth.",
        ),
        "conservation": (
            "Status: Domestic — not a wild extinction concern.",
            "Dogs are cared for by people; wild wolves are the species at risk.",
        ),
    },
    "cat": {
        "population": (
            "Roughly 600 million cats live worldwide as pets or feral animals.",
            "House cats outnumber most wild cat species by millions to one.",
        ),
        "conservation": (
            "Status: Domestic — not a wild extinction concern.",
            "Wild relatives like tigers and leopards face extinction; pet cats do not.",
        ),
    },
    "chicken": {
        "population": (
            "More than 25 billion chickens are raised on farms worldwide.",
            "They are the most numerous bird on the planet.",
        ),
        "conservation": (
            "Status: Domestic — farm birds are not at risk of extinction.",
            "Wild jungle fowl ancestors still exist in small Asian forests.",
        ),
    },
    "horse": {
        "population": (
            "About 60 million horses live worldwide — farm, sport, and wild mustangs.",
            "Truly wild horses like Przewalski's horse number only about 2,000.",
        ),
        "conservation": (
            "Status: Domestic horses — safe; Przewalski's horse — Endangered in the wild.",
            "Most horses live with people; only a few wild horse types need protection.",
        ),
    },
    "cow": {
        "population": (
            "More than 1 billion cattle live on farms worldwide.",
            "They are among the most numerous large mammals on Earth.",
        ),
        "conservation": (
            "Status: Domestic — not a wild extinction concern.",
            "Wild cattle relatives like banteng and anoa are the species at risk.",
        ),
    },
    "rabbit": {
        "population": (
            "Millions of wild rabbits and hundreds of millions of pet and farm rabbits exist.",
            "European rabbits are widespread; some island rabbits are very rare.",
        ),
        "conservation": (
            "Status: Least Concern for common rabbits; some island species are Endangered.",
            "Disease, habitat loss, and predators affect local populations.",
        ),
    },
    "jellyfish": {
        "population": (
            "Uncountable billions of jellyfish pulse through the world's oceans.",
            "Some blooms hold millions of jellyfish in a single bay.",
        ),
        "conservation": (
            "Status: Least Concern for most species — huge numbers in the sea.",
            "Pollution and warming oceans can hurt jellyfish or cause massive blooms.",
        ),
    },
    "clownfish": {
        "population": (
            "Population unknown — clownfish live on reefs across the Indo-Pacific.",
            "They are common on healthy coral reefs but hard to count precisely.",
        ),
        "conservation": (
            "Status: Least Concern — widespread on reefs, but reef loss is a threat.",
            "Coral bleaching and aquarium trade pressure hurt some reef populations.",
        ),
    },
    "alligator": {
        "population": (
            "More than 1 million American alligators live in the southeastern United States.",
            "Chinese alligators are far rarer — only a few hundred in the wild.",
        ),
        "conservation": (
            "Status: American — Least Concern; Chinese — Critically Endangered.",
            "Hunting almost wiped out American alligators; protection brought them back.",
        ),
    },
    "crocodile": {
        "population": (
            "Population varies — saltwater crocodiles number in the hundreds of thousands.",
            "Some crocodile species have fewer than 1,000 adults left.",
        ),
        "conservation": (
            "Status: Least Concern to Critically Endangered, depending on species.",
            "Habitat loss, hunting, and conflict with people threaten many crocodiles.",
        ),
    },
    "tuna": {
        "population": (
            "Bluefin tuna populations dropped to a fraction of historic levels.",
            "Some tuna species still number in the millions; others are severely depleted.",
        ),
        "conservation": (
            "Status: Several species are Vulnerable or Endangered from overfishing.",
            "Heavy fishing pressure is the main threat to tuna worldwide.",
        ),
    },
    "salmon": {
        "population": (
            "Millions of salmon still return to rivers, but many runs have collapsed.",
            "Some populations are huge; others have only dozens of fish left.",
        ),
        "conservation": (
            "Status: Least Concern to Endangered, depending on population and region.",
            "Dams, warming rivers, and overfishing threaten salmon on many coasts.",
        ),
    },
    "sloth": {
        "population": (
            "Exact counts are unknown — sloths live hidden in rainforest treetops.",
            "Pygmy three-toed sloths may number only about 100 animals.",
        ),
        "conservation": (
            "Status: Least Concern to Critically Endangered, depending on species.",
            "Forest clearing is the biggest threat to every sloth species.",
        ),
    },
    "toucan": {
        "population": (
            "Toucans are common in healthy rainforests, but total numbers are unknown.",
            "Toco toucans are widespread; some mountain toucans are much rarer.",
        ),
        "conservation": (
            "Status: Least Concern for common toucans; some species are Near Threatened.",
            "Rainforest loss and capture for the pet trade hurt toucan populations.",
        ),
    },
    "meerkat": {
        "population": (
            "No precise global count — meerkats live in parts of southern Africa.",
            "They are common in the Kalahari and surrounding dry grasslands.",
        ),
        "conservation": (
            "Status: Least Concern — populations are stable in protected areas.",
            "Drought and habitat change could affect meerkats in the future.",
        ),
    },
    "ostrich": {
        "population": (
            "About 2 million common ostriches live in Africa (wild and farmed).",
            "Somali ostriches in the Horn of Africa are much rarer.",
        ),
        "conservation": (
            "Status: Common ostrich — Least Concern; Somali ostrich — Vulnerable.",
            "Hunting and habitat loss threaten the rarer ostrich types.",
        ),
    },
    "bison": {
        "population": (
            "About 20,000 wild American bison live in conservation herds.",
            "Hundreds of thousands more live on ranches in North America.",
        ),
        "conservation": (
            "Status: Near Threatened — wild herds are tiny compared to historic millions.",
            "Most bison live on farms; truly wild herds need continued protection.",
        ),
    },
    "wildebeest": {
        "population": (
            "About 1.5 million blue wildebeest live in the Serengeti–Mara ecosystem alone.",
            "Millions more live across eastern and southern Africa.",
        ),
        "conservation": (
            "Status: Least Concern — large herds remain on African grasslands.",
            "Fences, drought, and habitat loss can block their famous migrations.",
        ),
    },
    "flamingo": {
        "population": (
            "Millions of flamingos live in Africa, South America, and southern Europe.",
            "Some species number in the hundreds of thousands to low millions.",
        ),
        "conservation": (
            "Status: Least Concern to Near Threatened, depending on species.",
            "Lake pollution, mining, and habitat loss threaten nesting flamingos.",
        ),
    },
    "spider": {
        "population": (
            "Likely billions of spiders live on Earth — scientists cannot count them all.",
            "Spiders outnumber humans many times over in most habitats.",
        ),
        "conservation": (
            "Status: Least Concern for nearly all spider species.",
            "Pesticides and habitat loss can hurt local spiders but not the group overall.",
        ),
    },
    "ant": {
        "population": (
            "Scientists estimate 20 quadrillion ants live on Earth (20 with 15 zeros).",
            "Ants may outweigh all wild birds and mammals combined.",
        ),
        "conservation": (
            "Status: Least Concern — ants are among the most successful animals on Earth.",
            "Habitat loss and pesticides can wipe out local colonies but not the whole group.",
        ),
    },
    "goldfish": {
        "population": (
            "Hundreds of millions of goldfish live in ponds, tanks, and lakes worldwide.",
            "Released pets have formed wild populations on every continent except Antarctica.",
        ),
        "conservation": (
            "Status: Domestic — not endangered; invasive in some wild waterways.",
            "Pet goldfish are safe; they can crowd out native fish where released.",
        ),
    },
    "vaquita": {
        "population": (
            "Fewer than 20 vaquitas remain — the rarest marine mammal on Earth.",
            "They live only in the northern Gulf of California in Mexico.",
        ),
        "conservation": (
            "Status: Critically Endangered — on the edge of extinction.",
            "Illegal gillnets set for fish accidentally kill vaquitas faster than they can reproduce.",
        ),
    },
    "kakapo": {
        "population": (
            "About 250 kakapos remain after a major recovery program in New Zealand.",
            "Each bird has a name and is tracked by conservation rangers.",
        ),
        "conservation": (
            "Status: Critically Endangered — once nearly extinct.",
            "Predators, habitat loss, and slow breeding kept numbers dangerously low for decades.",
        ),
    },
    "axolotl": {
        "population": (
            "Few wild axolotls survive — only in canals near Mexico City.",
            "Captive axolotls in labs and homes far outnumber wild ones.",
        ),
        "conservation": (
            "Status: Critically Endangered in the wild.",
            "Pollution, invasive fish, and urban sprawl destroyed most of their wetland home.",
        ),
    },
    "cross-river-gorilla": {
        "population": (
            "Fewer than 350 Cross River gorillas remain in the wild.",
            "They survive only in scattered forests along the Nigeria–Cameroon border.",
        ),
        "conservation": (
            "Status: Critically Endangered — they are the rarest gorilla subspecies.",
            "Forest protection and anti-poaching patrols are vital to their survival.",
        ),
    },
    "green-monkey": {
        "population": (
            "Green monkeys are common in parts of West Africa.",
            "Introduced groups also live on Caribbean islands such as Barbados.",
        ),
        "conservation": (
            "Status: Least Concern — wild populations are still widespread.",
            "They can become pests on farms, so people sometimes trap or relocate them.",
        ),
    },
    "spectacled-bear": {
        "population": (
            "About 18,000–20,000 spectacled bears remain in the Andes.",
            "They are South America's only bear species.",
        ),
        "conservation": (
            "Status: Vulnerable — habitat loss and hunting have reduced their range.",
            "Forest clearing for farms and roads fragments their mountain home.",
        ),
    },
}

DOMESTIC_IDS = {
    "dog", "cat", "chicken", "horse", "cow", "pig", "sheep", "goat", "duck",
    "turkey", "hamster", "goldfish", "guinea-pig", "donkey", "llama", "alpaca",
}

TYPE_POPULATION = {
    "Insect": (
        "Exact counts are unknown — likely millions to billions in nature.",
        "Small size and short lives make insects extremely hard to count.",
    ),
    "Arachnid": (
        "Nobody knows the precise number — likely billions worldwide.",
        "Spiders and scorpions are common but difficult to census.",
    ),
    "Fish": (
        "Population varies widely — from abundant schooling fish to rare deep-sea species.",
        "Overfishing has reduced many fish populations sharply.",
    ),
    "Bird": (
        "Population varies — common birds number in millions; rare birds may have only hundreds left.",
        "Counts change with seasons as birds migrate and breed.",
    ),
    "Mammal": (
        "Population estimates vary — some mammals number in millions, others in hundreds.",
        "Scientists use tracking, cameras, and surveys to estimate wild numbers.",
    ),
    "Reptile": (
        "Counts vary by species — some reptiles are abundant, others are very rare.",
        "Secretive habits make many reptiles hard to count accurately.",
    ),
    "Amphibian": (
        "Many amphibian populations have crashed — some species number in the hundreds.",
        "Frogs and salamanders are sensitive to pollution and habitat change.",
    ),
    "Crustacean": (
        "From countless tiny shrimp to millions of crabs — numbers vary hugely by species.",
        "Ocean crustaceans are often abundant but hard to count precisely.",
    ),
    "Mollusk": (
        "Population ranges from billions of small snails to rare deep-ocean octopuses.",
        "Many mollusks are common; some giant clams and abalone are heavily overfished.",
    ),
    "Invertebrate": (
        "Uncountable numbers — invertebrates dominate animal life on Earth.",
        "Scientists focus on trends rather than exact totals for most invertebrates.",
    ),
}

TYPE_CONSERVATION = {
    "Insect": (
        "Status: Least Concern for most species — insects are extremely numerous.",
        "Pesticides and habitat loss threaten many individual insect species.",
    ),
    "Arachnid": (
        "Status: Least Concern for nearly all spiders and scorpions.",
        "Habitat loss and pesticides can hurt local populations.",
    ),
    "Fish": (
        "Status: Varies — many fish are Least Concern; overfished species are Endangered.",
        "Overfishing, pollution, and dammed rivers are major threats to fish.",
    ),
    "Bird": (
        "Status: Varies — backyard birds are often Least Concern; island birds may be Critically Endangered.",
        "Habitat loss, cats, and climate change threaten many bird species.",
    ),
    "Mammal": (
        "Status: Varies widely — from Least Concern deer to Critically Endangered rhinos.",
        "Habitat loss, hunting, and climate change are common threats to mammals.",
    ),
    "Reptile": (
        "Status: Varies — common lizards are Least Concern; some turtles are Critically Endangered.",
        "Habitat loss, road kills, and collection for trade threaten many reptiles.",
    ),
    "Amphibian": (
        "Status: Many amphibians are Threatened — frogs are declining worldwide.",
        "Pollution, disease, and drained wetlands are major amphibian threats.",
    ),
    "Crustacean": (
        "Status: Most are Least Concern; overfished crabs and lobsters face pressure.",
        "Overfishing and ocean pollution threaten many crustacean populations.",
    ),
    "Mollusk": (
        "Status: Varies — common snails are safe; overfished shellfish are at risk.",
        "Pollution, overharvesting, and ocean warming threaten many mollusks.",
    ),
    "Invertebrate": (
        "Status: Most invertebrates are Least Concern as a group.",
        "Pollution and habitat loss still endanger many individual species.",
    ),
}

FARM_POPULATION = (
    "Large numbers live on farms and ranches worldwide.",
    "Exact farm counts change every year as animals are raised for food or work.",
)
FARM_CONSERVATION = (
    "Status: Domestic — raised by people, not a wild extinction crisis.",
    "Wild relatives of farm animals may be endangered even when farm breeds are plentiful.",
)

RISK_BY_HASH = [
    (
        "Status: Least Concern — populations are still large and widespread.",
        "Scientists watch their numbers, but they are not close to extinction right now.",
    ),
    (
        "Status: Near Threatened — numbers are slipping in parts of their range.",
        "Habitat loss and human activity could push them toward greater risk.",
    ),
    (
        "Status: Vulnerable — fewer individuals remain than in past decades.",
        "Protection efforts help, but habitat loss and hunting still pressure this species.",
    ),
]


def json_escape(value):
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def pick_index(options, seed):
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return h % len(options)


def load_profiles():
    if not PROFILES_PATH.exists():
        return {}
    return json.loads(PROFILES_PATH.read_text(encoding="utf-8"))


def world_from_profile(profile):
    """Return (population_tuple, conservation_tuple) from a strong profile."""
    pop = profile.get("populationFacts")
    if not pop and profile.get("population"):
        pop = [profile["population"]]
    con = profile.get("conservationFacts")
    if not con and profile.get("conservation"):
        con = [profile["conservation"]]
    if pop and con:
        return tuple(pop), tuple(con)
    return None


def build_world(animal, profiles=None):
    aid = animal["id"]
    if profiles and aid in profiles:
        from_profile = world_from_profile(profiles[aid])
        if from_profile:
            return from_profile

    if aid in WORLD_DATA:
        data = WORLD_DATA[aid]
        return data["population"], data["conservation"]

    typ = animal.get("type", "Mammal")
    habitat = animal.get("habitat", "Forest")

    if aid in DOMESTIC_IDS or habitat == "Farm":
        return (FARM_POPULATION, FARM_CONSERVATION)

    if typ in TYPE_POPULATION:
        pop = TYPE_POPULATION[typ]
        con = TYPE_CONSERVATION[typ]
        if typ in ("Mammal", "Bird", "Fish", "Reptile"):
            con = RISK_BY_HASH[pick_index(RISK_BY_HASH, aid + "-risk")]
        return pop, con

    pop = TYPE_POPULATION["Mammal"]
    con = RISK_BY_HASH[pick_index(RISK_BY_HASH, aid + "-risk")]
    return pop, con


def parse_animal_block(block):
    animal = {}
    for field in ("id", "name", "emoji", "type", "habitat", "size"):
        m = re.search(rf'{field}:\s*"((?:\\.|[^"\\])*)"', block)
        if m:
            animal[field] = m.group(1)
    return animal if animal.get("id") and animal.get("name") else None


def strip_world(block):
    block = re.sub(r"\n\s*populationFacts:\s*\[[\s\S]*?\],", "", block)
    block = re.sub(r'\n\s*population:\s*"((?:\\.|[^"\\])*)",', "", block)
    block = re.sub(r"\n\s*conservationFacts:\s*\[[\s\S]*?\],", "", block)
    block = re.sub(r'\n\s*conservation:\s*"((?:\\.|[^"\\])*)",', "", block)
    return block


def format_snippet(population, conservation):
    lines = ["          populationFacts: ["]
    for fact in population:
        lines.append(f'            "{json_escape(fact)}",')
    lines.append("          ],")
    lines.append(f'          population: "{json_escape(population[0])}",')
    lines.append("          conservationFacts: [")
    for fact in conservation:
        lines.append(f'            "{json_escape(fact)}",')
    lines.append("          ],")
    lines.append(f'          conservation: "{json_escape(conservation[0])}",')
    return "\n".join(lines)


def insert_world(block, population, conservation):
    block = strip_world(block)
    m = re.search(r'lifespan:\s*"((?:\\.|[^"\\])*)",', block)
    if not m:
        m = re.search(r"lifespanFacts:\s*\[[\s\S]*?\],", block)
    if not m:
        insert_at = block.rfind("\n        },")
        if insert_at == -1:
            insert_at = block.rfind("\n        }")
        snippet = format_snippet(population, conservation)
        return block[:insert_at] + "\n" + snippet + block[insert_at:]

    insert_at = m.end()
    snippet = "\n" + format_snippet(population, conservation)
    return block[:insert_at] + snippet + block[insert_at:]


def main():
    profiles = load_profiles()
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
    profile_hits = 0

    for idx, match in enumerate(markers):
        block_start = match.start() + 1
        block_end = markers[idx + 1].start() + 1 if idx + 1 < len(markers) else len(section)
        block = section[block_start:block_end]
        animal = parse_animal_block(block)
        if not animal or animal["id"] == "pending":
            chunks.append(block)
            continue

        population, conservation = build_world(animal, profiles)
        if animal["id"] in profiles and world_from_profile(profiles[animal["id"]]):
            profile_hits += 1
        chunks.append(insert_world(block, population, conservation))
        updated += 1

    rebuilt = section[: markers[0].start() + 1] + "".join(chunks)
    INDEX.write_text(text[:start] + rebuilt + text[end:], encoding="utf-8")
    print(
        f"Added population and conservation facts to {updated} animals "
        f"({profile_hits} from strong_profiles.json)."
    )


if __name__ == "__main__":
    main()
