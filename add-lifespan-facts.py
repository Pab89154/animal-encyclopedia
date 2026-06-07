#!/usr/bin/env python3
"""Add lifespanFacts (wild, captivity, common deaths) to every animal in index.html."""

import hashlib
import re
from pathlib import Path

INDEX = Path(__file__).parent / "index.html"

# Curated facts for well-known species (wild, captivity, common deaths).
OVERRIDES = {
    "lion": (
        "In the wild: Lions usually live about 10–14 years.",
        "In captivity: In zoos with good care, lions can live into their late teens or early 20s.",
        "Often die from: Fights with other lions, hunting injuries, drought, or disease.",
    ),
    "tiger": (
        "In the wild: Tigers often live about 10–15 years.",
        "In captivity: Tigers in zoos can reach their late teens or about 20 with expert care.",
        "Often die from: Loss of prey, fights with other tigers, poaching, or injury while hunting.",
    ),
    "elephant": (
        "In the wild: African elephants can live about 60–70 years.",
        "In captivity: Elephants in sanctuaries and zoos sometimes live into their 70s or a bit longer.",
        "Often die from: Drought, habitat loss, conflict with people, or sickness in old age.",
    ),
    "giraffe": (
        "In the wild: Giraffes usually live about 20–25 years.",
        "In captivity: With steady food and vet care, giraffes can live into their late 20s.",
        "Often die from: Predators when young, accidents, drought, or disease.",
    ),
    "zebra": (
        "In the wild: Zebras often live about 20–25 years.",
        "In captivity: In wildlife parks, zebras can live into their late 20s or early 30s.",
        "Often die from: Lions and other predators, drought, or sickness.",
    ),
    "cheetah": (
        "In the wild: Cheetahs usually live about 10–12 years.",
        "In captivity: Cheetahs in breeding programs can live about 15–17 years.",
        "Often die from: Other predators, injuries from fast chases, or lack of prey.",
    ),
    "rhino": (
        "In the wild: Rhinos can live about 35–45 years depending on the species.",
        "In captivity: Protected rhinos may live into their 40s or 50s with vet care.",
        "Often die from: Poaching, habitat loss, fights, or disease.",
    ),
    "bear": (
        "In the wild: Brown bears often live about 20–25 years.",
        "In captivity: Bears in zoos can live into their 30s with good care.",
        "Often die from: Fights with other bears, starvation, hunting, or disease.",
    ),
    "brown-bear": (
        "In the wild: Brown bears often live about 20–25 years.",
        "In captivity: Bears in zoos can live into their 30s with good care.",
        "Often die from: Fights with other bears, starvation, hunting, or disease.",
    ),
    "polar-bear": (
        "In the wild: Polar bears usually live about 15–18 years.",
        "In captivity: Polar bears in zoos can live into their mid-20s or a bit longer.",
        "Often die from: Thin sea ice, lack of seals to eat, pollution, or drowning.",
    ),
    "wolf": (
        "In the wild: Wolves often live about 6–8 years in the wild.",
        "In captivity: Wolves in sanctuaries can live about 12–15 years.",
        "Often die from: Fights with rival packs, lack of prey, disease, or people.",
    ),
    "fox": (
        "In the wild: Red foxes usually live about 3–5 years in the wild.",
        "In captivity: Foxes can live about 10–14 years with care.",
        "Often die from: Cars, coyotes, disease, or starvation in hard winters.",
    ),
    "arctic-fox": (
        "In the wild: Arctic foxes often live about 3–6 years.",
        "In captivity: They can live about 10–14 years in wildlife centers.",
        "Often die from: Cold winters with little food, predators, or disease.",
    ),
    "deer": (
        "In the wild: White-tailed deer often live about 6–10 years.",
        "In captivity: Deer in refuges can live about 15–20 years.",
        "Often die from: Hunters, cars, wolves or coyotes, and harsh winters.",
    ),
    "moose": (
        "In the wild: Moose often live about 15–20 years.",
        "In captivity: Moose in wildlife parks can live into their 20s.",
        "Often die from: Wolves, ticks and disease, winter starvation, or car crashes.",
    ),
    "gorilla": (
        "In the wild: Gorillas often live about 35–40 years.",
        "In captivity: Gorillas in zoos can live into their 40s or 50s.",
        "Often die from: Disease, habitat loss, and sometimes fights in the group.",
    ),
    "orangutan": (
        "In the wild: Orangutans can live about 35–45 years.",
        "In captivity: With care, orangutans can live into their 50s.",
        "Often die from: Habitat loss, falling from trees, or disease.",
    ),
    "chimpanzee": (
        "In the wild: Chimpanzees often live about 33–40 years.",
        "In captivity: Chimps in zoos can live into their 50s.",
        "Often die from: Disease, predators when young, and fights in the troop.",
    ),
    "panda": (
        "In the wild: Giant pandas often live about 15–20 years.",
        "In captivity: Pandas in breeding centers can live into their 30s.",
        "Often die from: Bamboo shortages, sickness, or accidents in rough terrain.",
    ),
    "koala": (
        "In the wild: Koalas often live about 10–15 years.",
        "In captivity: Koalas in wildlife hospitals can live a few years longer.",
        "Often die from: Chlamydia disease, dog attacks, car hits, and habitat loss.",
    ),
    "kangaroo": (
        "In the wild: Kangaroos often live about 6–8 years in the wild.",
        "In captivity: They can live about 15–20 years in sanctuaries.",
        "Often die from: Drought, dingoes, cars, and disease.",
    ),
    "sloth": (
        "In the wild: Sloths often live about 20–30 years.",
        "In captivity: Sloths in zoos can live into their 30s or 40s.",
        "Often die from: Falling, eagles when young, habitat loss, or infection.",
    ),
    "hippo": (
        "In the wild: Hippos can live about 40–50 years.",
        "In captivity: Hippos in zoos often live into their 50s.",
        "Often die from: Fights with other hippos, drought, or disease.",
    ),
    "bison": (
        "In the wild: Bison often live about 15–20 years.",
        "In captivity: Bison on protected ranges can live into their 20s.",
        "Often die from: Wolves when calves, harsh winters, disease, or hunting.",
    ),
    "whale": (
        "In the wild: Many large whales live 50–90 years or more.",
        "In captivity: Few whales live in tanks today; wild lifespans are much longer than short captive ones.",
        "Often die from: Ship strikes, fishing gear, pollution, and lack of food.",
    ),
    "orca": (
        "In the wild: Orcas can live about 50–90 years (females often live longest).",
        "In captivity: Orcas in marine parks have often died much younger than in the wild.",
        "Often die from: Pollution, prey loss, boat noise stress, and entanglement in nets.",
    ),
    "dolphin": (
        "In the wild: Bottlenose dolphins often live about 40–50 years.",
        "In captivity: Dolphins in marine parks may live decades but face stress and illness.",
        "Often die from: Fishing nets, pollution, boat strikes, and disease.",
    ),
    "shark": (
        "In the wild: Many sharks live 20–70 years depending on species.",
        "In captivity: Large sharks rarely thrive in tanks; lifespans are usually shorter.",
        "Often die from: Overfishing, finning, habitat damage, and slow reproduction.",
    ),
    "sea-turtle": (
        "In the wild: Sea turtles can live 50–80 years or more.",
        "In captivity: Rehab turtles may be released; long lives are normal in the ocean.",
        "Often die from: Plastic pollution, fishing nets, boat hits, and egg poaching.",
    ),
    "penguin": (
        "In the wild: Emperor penguins can live about 15–20 years.",
        "In captivity: Penguins in zoos can live into their 20s with steady food.",
        "Often die from: Leopard seals, starvation, extreme cold, and oil spills.",
    ),
    "seal": (
        "In the wild: Harbor seals often live about 25–30 years.",
        "In captivity: Seals in rehab centers can live into their 30s.",
        "Often die from: Orcas, sharks, fishing nets, and disease.",
    ),
    "walrus": (
        "In the wild: Walruses can live about 30–40 years.",
        "In captivity: Walruses in zoos may live into their 30s.",
        "Often die from: Loss of sea ice, lack of clams to eat, polar bears, and disease.",
    ),
    "reindeer": (
        "In the wild: Reindeer (caribou) often live about 12–15 years.",
        "In captivity: Herded reindeer can live a few years longer with vet care.",
        "Often die from: Wolves, harsh winters, disease, and lack of lichen to eat.",
    ),
    "owl": (
        "In the wild: Great horned owls can live about 13–15 years in the wild.",
        "In captivity: Owls in wildlife centers can live 20–30 years.",
        "Often die from: Cars, rodent poison, starvation, and territorial fights.",
    ),
    "snowy-owl": (
        "In the wild: Snowy owls often live about 10 years in the wild.",
        "In captivity: They can live about 25–30 years with care.",
        "Often die from: Starvation when lemmings are scarce, cars, and disease.",
    ),
    "eagle": (
        "In the wild: Bald eagles can live about 20–30 years in the wild.",
        "In captivity: Eagles in rehab can live into their 30s.",
        "Often die from: Lead poisoning from shot animals, car hits, and starvation.",
    ),
    "robin": (
        "In the wild: American robins often live about 2 years in the wild (many are young).",
        "In captivity: Pet birds are uncommon; robins in rehab are usually released quickly.",
        "Often die from: Cats, hawks, cars, cold snaps, and worms sprayed with pesticides.",
    ),
    "parrot": (
        "In the wild: Large parrots can live 30–80 years depending on species.",
        "In captivity: Well-cared-for parrots are among the longest-lived pet birds.",
        "Often die from: Habitat loss, capture for trade, predators, and poor diet in captivity.",
    ),
    "toucan": (
        "In the wild: Toucans often live about 15–20 years.",
        "In captivity: Toucans in zoos can live into their 20s.",
        "Often die from: Habitat loss, predators at nests, and disease.",
    ),
    "crocodile": (
        "In the wild: Saltwater crocodiles can live 70+ years.",
        "In captivity: Crocodiles in zoos can live many decades with care.",
        "Often die from: Fights with other crocs, habitat loss, and hunting.",
    ),
    "alligator": (
        "In the wild: American alligators can live 35–50 years.",
        "In captivity: Alligators in zoos can live 50–70 years.",
        "Often die from: Cold snaps, fights, pollution, and hunting (where allowed).",
    ),
    "snake": (
        "In the wild: Many snakes live 10–25 years depending on species.",
        "In captivity: Snakes in zoos or as pets can live longer with steady food.",
        "Often die from: Hawks, people, cars, cold weather, and disease.",
    ),
    "turtle": (
        "In the wild: Box turtles can live 30–40 years or more.",
        "In captivity: Turtles with proper care can outlive their wild peers.",
        "Often die from: Cars, habitat loss, raccoons eating eggs, and disease.",
    ),
    "frog": (
        "In the wild: Many frogs live about 3–6 years in the wild.",
        "In captivity: Frogs in terrariums can live about 10–15 years.",
        "Often die from: Pollution, drying ponds, predators, and fungus disease.",
    ),
    "poison-dart-frog": (
        "In the wild: Poison dart frogs often live about 3–6 years.",
        "In captivity: In humid terrariums they can live about 10–15 years.",
        "Often die from: Habitat loss, pollution, and fungal skin disease.",
    ),
    "butterfly": (
        "In the wild: Adult butterflies often live a few days to a few weeks.",
        "In captivity: In butterfly houses, adults still live only a short time.",
        "Often die from: Birds, weather, pesticides, and worn-out wings.",
    ),
    "bee": (
        "In the wild: Worker honeybees live about 5–6 weeks in summer.",
        "In captivity: Queen bees in a hive can live about 2–5 years.",
        "Often die from: Pesticides, mites, cold, and predators at the hive.",
    ),
    "ant": (
        "In the wild: Worker ants often live weeks to a few months; queens can live years.",
        "In captivity: Ant colonies in formicaria mirror wild lifespans by caste.",
        "Often die from: Other ants, spiders, flooding, and poison baits.",
    ),
    "jellyfish": (
        "In the wild: Many jellyfish live a few months; some species can live years.",
        "In captivity: Aquarium jellies live about as long as in the sea with clean water.",
        "Often die from: Predators, rough waves, temperature changes, and pollution.",
    ),
    "octopus": (
        "In the wild: Most octopuses live about 1–3 years (giants live longer).",
        "In captivity: Octopuses in aquariums rarely live more than a few years.",
        "Often die from: Predators, fishing, and they often die soon after laying eggs.",
    ),
    "crab": (
        "In the wild: Many crabs live 3–10 years depending on species.",
        "In captivity: Crabs in aquariums can live toward the upper end with good water.",
        "Often die from: Birds, fish, fishing, pollution, and molting problems.",
    ),
    "lobster": (
        "In the wild: American lobsters can live 50+ years.",
        "In captivity: Lobsters in tanks may live decades if not harvested.",
        "Often die from: Fishing, predators when small, and ocean warming.",
    ),
    "shrimp": (
        "In the wild: Many shrimp live 1–2 years.",
        "In captivity: Aquarium shrimp often live about the same span with clean water.",
        "Often die from: Fish predators, pollution, and sudden water changes.",
    ),
    "starfish": (
        "In the wild: Sea stars often live about 10–35 years depending on species.",
        "In captivity: In touch tanks and aquariums they need cool, clean salt water.",
        "Often die from: Wasting disease, pollution, drying out at low tide, and predators.",
    ),
    "spider": (
        "In the wild: Many spiders live 1–2 years; tarantulas can live much longer.",
        "In captivity: Pet tarantulas can live 15–25 years (females often longest).",
        "Often die from: Birds, wasps, people, and molting accidents.",
    ),
    "scorpion": (
        "In the wild: Emperor scorpions can live about 6–8 years.",
        "In captivity: Pet scorpions can live about 8–10 years.",
        "Often die from: Other scorpions, birds, habitat loss, and drying out.",
    ),
    "horse": (
        "In the wild: Mustangs and wild horses often live about 15–20 years.",
        "In captivity: Well-cared-for horses can live into their 25s or 30s.",
        "Often die from: Predators when foals, drought, injury, and colic.",
    ),
    "cow": (
        "In the wild: Wild cattle relatives can live about 18–25 years.",
        "In captivity: Farm cows often live about 15–20 years depending on the farm.",
        "Often die from: Disease, birthing problems, and slaughter on meat farms.",
    ),
    "pig": (
        "In the wild: Wild boar often live about 10–15 years.",
        "In captivity: Pet pigs can live 15–20 years; farm pigs are usually younger at end of life.",
        "Often die from: Hunters, wolves in Europe, disease, and farming.",
    ),
    "chicken": (
        "In the wild: Jungle fowl relatives live about 5–10 years.",
        "In captivity: Backyard hens can live 8–12 years; many farm birds live fewer years.",
        "Often die from: Foxes, hawks, disease, and farming.",
    ),
    "dog": (
        "In the wild: Wild dogs and dingoes often live about 5–7 years.",
        "In captivity: Pet dogs often live 10–13 years (small breeds often longer).",
        "Often die from: Disease, cars, fights, and old-age problems.",
    ),
    "cat": (
        "In the wild: Feral cats often live about 2–5 years.",
        "In captivity: Indoor pet cats often live 13–17 years or more.",
        "Often die from: Cars, coyotes, disease, and old-age illness.",
    ),
    "rabbit": (
        "In the wild: Cottontails often live about 1–2 years.",
        "In captivity: Pet rabbits can live 8–12 years.",
        "Often die from: Hawks, foxes, cars, and disease.",
    ),
    "hamster": (
        "In the wild: Syrian hamsters live about 2–3 years in the wild.",
        "In captivity: Pet hamsters usually live about 2–3 years.",
        "Often die from: Owls, snakes, cold, and old age.",
    ),
    "goldfish": (
        "In the wild: Goldfish in ponds can live about 10–15 years.",
        "In captivity: Well-kept aquarium goldfish can live 10–20 years or more.",
        "Often die from: Poor water, predators in ponds, and overfeeding problems.",
    ),
    "clownfish": (
        "In the wild: Clownfish often live about 6–10 years on the reef.",
        "In captivity: Aquarium clownfish can live about 10–15 years with good salt water.",
        "Often die from: Predators, reef bleaching, and captivity stress.",
    ),
    "salmon": (
        "In the wild: Many salmon live 2–7 years before returning to spawn once.",
        "In captivity: Hatchery fish are released; adults die soon after spawning in the wild.",
        "Often die from: Bears and birds, dams, warming rivers, and fishing.",
    ),
    "tuna": (
        "In the wild: Bluefin tuna can live 15–40 years.",
        "In captivity: Tuna are not kept as pets; wild fish face heavy fishing pressure.",
        "Often die from: Overfishing, bycatch in nets, and pollution.",
    ),
    "piranha": (
        "In the wild: Piranhas often live about 10–15 years.",
        "In captivity: Aquarium piranhas can live toward 15 years with clean water.",
        "Often die from: Larger fish, fishing, and poor aquarium care.",
    ),
    "eel": (
        "In the wild: American eels can live 15–30 years before spawning once.",
        "In captivity: Eels in aquariums may live many years with cool, clean water.",
        "Often die from: Dams blocking rivers, fishing, pollution, and spawning death.",
    ),
    "ray": (
        "In the wild: Stingrays can live 15–25 years.",
        "In captivity: Aquarium rays need huge tanks and can live many years with expert care.",
        "Often die from: Fishing, habitat damage, and sharks.",
    ),
    "stingray": (
        "In the wild: Stingrays can live 15–25 years.",
        "In captivity: Aquarium rays need huge tanks and can live many years with expert care.",
        "Often die from: Fishing, habitat damage, and sharks.",
    ),
    "camel": (
        "In the wild: Camels often live about 40 years.",
        "In captivity: Working camels with care can live into their 40s.",
        "Often die from: Drought, disease, accidents, and old age.",
    ),
    "hyena": (
        "In the wild: Spotted hyenas often live about 12–15 years.",
        "In captivity: Hyenas in zoos can live into their 20s.",
        "Often die from: Lions, food shortages, disease, and clan fights.",
    ),
    "warthog": (
        "In the wild: Warthogs often live about 15 years.",
        "In captivity: Warthogs in zoos can live a few years longer.",
        "Often die from: Lions, leopards, drought, and disease.",
    ),
    "meerkat": (
        "In the wild: Meerkats often live about 7–10 years.",
        "In captivity: Meerkats in zoos can live about 12–15 years.",
        "Often die from: Eagles, snakes, starvation, and fights with other groups.",
    ),
    "ostrich": (
        "In the wild: Ostriches can live 30–40 years.",
        "In captivity: Farm and zoo ostriches can live into their 40s.",
        "Often die from: Predators on eggs, disease, and accidents.",
    ),
    "emu": (
        "In the wild: Emus often live about 10–20 years.",
        "In captivity: Emus on farms and in zoos can live into their 20s.",
        "Often die from: Dingoes on chicks, disease, and car strikes.",
    ),
    "red-panda": (
        "In the wild: Red pandas often live about 8–10 years.",
        "In captivity: Red pandas in zoos can live about 15 years.",
        "Often die from: Habitat loss, snow leopards, and disease.",
    ),
    "raccoon": (
        "In the wild: Raccoons often live about 2–3 years in the wild.",
        "In captivity: Raccoons in rehab can live about 10–15 years.",
        "Often die from: Cars, disease, hunters, and dogs.",
    ),
    "squirrel": (
        "In the wild: Gray squirrels often live about 6 years in the wild.",
        "In captivity: Pet squirrels are rare; wild ones face many dangers early.",
        "Often die from: Hawks, cars, cats, and winter food shortages.",
    ),
    "porcupine": (
        "In the wild: Porcupines often live about 15–18 years.",
        "In captivity: Porcupines in zoos can live into their 20s.",
        "Often die from: Fishers and other predators, cars, and disease.",
    ),
    "jaguar": (
        "In the wild: Jaguars often live about 12–15 years.",
        "In captivity: Jaguars in zoos can live into their 20s.",
        "Often die from: Habitat loss, poaching, and fights over territory.",
    ),
    "leopard": (
        "In the wild: Leopards often live about 12–15 years.",
        "In captivity: Leopards in zoos can live into their 20s.",
        "Often die from: Loss of prey, poaching, and fights with other leopards.",
    ),
    "howler-monkey": (
        "In the wild: Howler monkeys often live about 15–20 years.",
        "In captivity: Monkeys in zoos can live into their 20s.",
        "Often die from: Habitat loss, eagles on young, and disease.",
    ),
    "african-wild-dog": (
        "In the wild: African wild dogs often live about 10 years.",
        "In captivity: In breeding programs they can live a few years longer.",
        "Often die from: Lions, disease, snares, and habitat loss.",
    ),
    "platypus": (
        "In the wild: Platypuses can live about 11–13 years in the wild.",
        "In captivity: Platypuses in zoos are rare but can live a bit longer.",
        "Often die from: Foxes, nets, drought, and water pollution.",
    ),
    "anaconda": (
        "In the wild: Green anacondas can live about 10 years in the wild.",
        "In captivity: Large snakes in zoos can live 15–20 years.",
        "Often die from: People, disease, injury, and old age after breeding.",
    ),
}

DEATH_BY_HABITAT = {
    "Grassland": [
        "Predators, drought, and disease",
        "Lack of grass or water, predators, and sickness",
        "Fights over territory, starvation, and hunting",
    ],
    "Forest": [
        "Predators, habitat loss, and disease",
        "Cars near roads, predators, and winter starvation",
        "Loss of trees, hunters, and sickness",
    ],
    "Jungle": [
        "Habitat loss, predators, and disease",
        "Snakes and big cats, pollution, and food shortages",
        "Logging, hunting, and infection",
    ],
    "Ocean": [
        "Predators, fishing nets, and pollution",
        "Larger hunters, plastic, and warming seas",
        "Lack of food, boats, and habitat damage",
    ],
    "Arctic": [
        "Cold winters, starvation, and predators",
        "Thin ice, lack of prey, and disease",
        "Climate change stress, pollution, and hunting",
    ],
    "Desert": [
        "Heat, thirst, and predators",
        "Drought, snakes, and lack of shade",
        "Cars, birds, and scarce food",
    ],
    "Farm": [
        "Predators, disease, and farming",
        "Foxes and hawks, illness, and slaughter on meat farms",
        "Cars, dogs, and poor shelter in bad weather",
    ],
}

PROFILES = {
    ("Mammal", "tiny"): (1, 2, 3, 6),
    ("Mammal", "small"): (2, 5, 6, 12),
    ("Mammal", "medium"): (5, 10, 12, 20),
    ("Mammal", "large"): (8, 15, 15, 30),
    ("Mammal", "giant"): (25, 45, 40, 65),
    ("Bird", "tiny"): (1, 3, 5, 12),
    ("Bird", "small"): (2, 6, 8, 18),
    ("Bird", "medium"): (5, 12, 12, 25),
    ("Bird", "large"): (15, 30, 25, 50),
    ("Reptile", "small"): (5, 10, 10, 20),
    ("Reptile", "medium"): (10, 20, 20, 40),
    ("Reptile", "large"): (25, 50, 40, 70),
    ("Amphibian", "small"): (2, 5, 6, 12),
    ("Amphibian", "medium"): (5, 10, 10, 18),
    ("Fish", "tiny"): (1, 3, 3, 8),
    ("Fish", "small"): (2, 5, 5, 12),
    ("Fish", "medium"): (5, 12, 10, 20),
    ("Fish", "large"): (15, 40, 20, 50),
    ("Insect", "tiny"): None,
    ("Crustacean", "small"): (2, 5, 5, 12),
    ("Crustacean", "medium"): (5, 15, 10, 30),
    ("Mollusk", "small"): (1, 3, 3, 8),
    ("Mollusk", "medium"): (3, 10, 8, 20),
    ("Arachnid", "small"): (1, 3, 3, 10),
    ("Invertebrate", "small"): (1, 3, 3, 10),
    ("Invertebrate", "medium"): (3, 8, 6, 15),
}

SHORT_LIVED = {
    "Insect": (
        "In the wild: Most adults live a few weeks to a few months.",
        "In captivity: In safe habitats, some can live about a year with steady food.",
        "Often die from: Birds, spiders, cold weather, and pesticides.",
    ),
    "Invertebrate": (
        "In the wild: Many small invertebrates live weeks to a couple of years.",
        "In captivity: In aquariums or terrariums, some species live longer with care.",
        "Often die from: Predators, drying out, pollution, and disease.",
    ),
}


def json_escape(value):
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def size_class(size_text, typ):
    s = (size_text or "").lower()
    if typ in ("Insect", "Arachnid") or any(
        w in s
        for w in [
            "grain",
            "rice",
            "thumb",
            "finger",
            "pencil",
            "coin",
            "pea",
            "ant-sized",
            "microscopic",
            "tiny",
            "small as a",
        ]
    ):
        return "tiny"
    if any(
        w in s
        for w in [
            "school bus",
            "bus",
            "building",
            "blue whale",
            "largest",
            "twice as long",
        ]
    ):
        return "giant"
    if any(
        w in s
        for w in [
            "car",
            "truck",
            "giraffe",
            "elephant",
            "hippo",
            "rhino",
            "bear",
            "horse",
            "adult human",
            "grown-up",
            "taller than",
        ]
    ):
        return "large"
    if any(w in s for w in ["cat", "dog", "rabbit", "football", "soccer"]):
        return "small"
    return "medium"


def pick_index(options, seed):
    if not options:
        return 0
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return h % len(options)


def format_years(lo, hi):
    if lo == hi:
        return f"about {lo} years"
    return f"about {lo}–{hi} years"


def pick_death(typ, habitat, animal_id):
    pool = DEATH_BY_HABITAT.get(habitat, DEATH_BY_HABITAT["Forest"])
    base = pool[pick_index(pool, animal_id + "-death")]
    if typ == "Fish":
        extras = ["fishing", "pollution", "and bigger fish"]
    elif typ == "Bird":
        extras = ["cats", "hawks", "and cars"]
    elif typ == "Reptile":
        extras = ["cars", "people", "and cold weather"]
    elif typ == "Amphibian":
        extras = ["pollution", "drying ponds", "and predators"]
    else:
        extras = []
    if extras and pick_index([0, 1], animal_id) == 1:
        return f"{base}, plus {', '.join(extras)}"
    return base


def build_lifespan(animal):
    aid = animal["id"]
    if aid in OVERRIDES:
        return OVERRIDES[aid]

    typ = animal.get("type", "Mammal")
    if typ in SHORT_LIVED and typ == "Insect":
        return SHORT_LIVED["Insect"]
    if typ == "Invertebrate" and size_class(animal.get("size", ""), typ) == "tiny":
        return SHORT_LIVED["Invertebrate"]

    sc = size_class(animal.get("size", ""), typ)
    if sc == "giant" and typ != "Mammal":
        sc = "large"
    key = (typ, sc)
    if key not in PROFILES:
        key = (typ, "medium")
    if key not in PROFILES:
        key = ("Mammal", "medium")
    profile = PROFILES.get(key)
    if profile is None:
        return SHORT_LIVED.get(typ, SHORT_LIVED["Invertebrate"])

    wild_lo, wild_hi, cap_lo, cap_hi = profile
    name = animal["name"]
    plural = name.lower() + "s"
    if name.lower().endswith("s"):
        plural = name.lower()

    wild = f"In the wild: Most {plural} live {format_years(wild_lo, wild_hi)}."
    cap = (
        f"In captivity: In zoos, farms, or wildlife centers, they may live "
        f"{format_years(cap_lo, cap_hi)} with expert care."
    )
    death = f"Often die from: {pick_death(typ, animal.get('habitat', 'Forest'), aid)}."
    return (wild, cap, death)


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


def strip_lifespan(block):
    block = re.sub(r"\n\s*lifespanFacts:\s*\[[\s\S]*?\],", "", block)
    block = re.sub(r'\n\s*lifespan:\s*"((?:\\.|[^"\\])*)",', "", block)
    return block


def insert_lifespan(block, facts):
    block = strip_lifespan(block)
    m = re.search(r"sizeFacts:\s*\[[\s\S]*?\],", block)
    if not m:
        insert_at = block.rfind("\n        },")
        if insert_at == -1:
            insert_at = block.rfind("\n        }")
        snippet = format_lifespan_snippet(facts)
        return block[:insert_at] + "\n" + snippet + block[insert_at:]

    insert_at = m.end()
    snippet = "\n" + format_lifespan_snippet(facts)
    return block[:insert_at] + snippet + block[insert_at:]


def format_lifespan_snippet(facts):
    lines = ["          lifespanFacts: ["]
    for fact in facts:
        lines.append(f'            "{json_escape(fact)}",')
    lines.append("          ],")
    lines.append(f'          lifespan: "{json_escape(facts[0])}",')
    return "\n".join(lines)


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
        if not animal or animal["id"] == "pending":
            chunks.append(block)
            continue

        facts = build_lifespan(animal)
        chunks.append(insert_lifespan(block, facts))
        updated += 1

    rebuilt = section[: markers[0].start() + 1] + "".join(chunks)
    INDEX.write_text(text[:start] + rebuilt + text[end:], encoding="utf-8")
    print(f"Added lifespan facts to {updated} animals.")


if __name__ == "__main__":
    main()
