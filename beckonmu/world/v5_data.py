"""
V5 Vampire: The Masquerade Game Data Configuration

This module contains all V5 game mechanics data in a database-ready format.
Unlike the reference repository, this data is NOT hardcoded - it will be loaded
into the database during initialization and can be modified without code changes.

See: V5_REFERENCE_DATABASE.md for complete mechanics reference
See: V5_IMPLEMENTATION_ROADMAP.md Phase 4+ for when this data gets used

ARCHITECTURAL PRINCIPLE:
- This file defines the DATA STRUCTURE only
- Actual data loading happens in beckonmu/server/conf/at_initial_setup.py
- Game logic uses database queries, NOT direct imports from this file
"""

# ============================================================================
# ATTRIBUTES (Physical, Social, Mental)
# ============================================================================

ATTRIBUTES = {
    "Physical": ["Strength", "Dexterity", "Stamina"],
    "Social": ["Charisma", "Manipulation", "Composure"],
    "Mental": ["Intelligence", "Wits", "Resolve"]
}

# ============================================================================
# SKILLS (organized by category)
# ============================================================================

SKILLS = {
    "Physical": [
        "Athletics", "Brawl", "Craft", "Drive", "Firearms",
        "Melee", "Larceny", "Stealth", "Survival"
    ],
    "Social": [
        "Animal Ken", "Etiquette", "Insight", "Intimidation",
        "Leadership", "Performance", "Persuasion", "Streetwise", "Subterfuge"
    ],
    "Mental": [
        "Academics", "Awareness", "Finance", "Investigation",
        "Medicine", "Occult", "Politics", "Science", "Technology"
    ]
}

# ============================================================================
# CLANS (with in-clan disciplines, banes, compulsions)
# ============================================================================

CLANS = {
    "Brujah": {
        "disciplines": ["Celerity", "Potence", "Presence"],
        "bane": "Violent Temper: Difficulty +2 to resist fury frenzy",
        "compulsion": "Rebellion: Must defy authority or lose 1 die from Social pools"
    },
    "Gangrel": {
        "disciplines": ["Animalism", "Fortitude", "Protean"],
        "bane": "Bestial Features: Animal features emerge when Hunger 4+",
        "compulsion": "Feral Impulses: Must avoid civilization or lose 1 die from Mental/Social pools"
    },
    "Malkavian": {
        "disciplines": ["Auspex", "Dominate", "Obfuscate"],
        "bane": "Fractured Perspective: Must have at least one mental derangement",
        "compulsion": "Delusion: Fixate on irrational belief or lose 1 die from pools"
    },
    "Nosferatu": {
        "disciplines": ["Animalism", "Obfuscate", "Potence"],
        "bane": "Repulsive: Appearance 0, automatic fail on all Persuasion/Performance vs mortals",
        "compulsion": "Cryptophilia: Hoard secrets or lose 2 dice from actions"
    },
    "Toreador": {
        "disciplines": ["Auspex", "Celerity", "Presence"],
        "bane": "Aesthetic Fixation: May become entranced by beauty (Composure + Wits vs Diff 3+)",
        "compulsion": "Obsession: Fixate on beauty or lose 2 dice from other actions"
    },
    "Tremere": {
        "disciplines": ["Auspex", "Blood Sorcery", "Dominate"],
        "bane": "Deficient Blood: Blood bonds form one step stronger when drinking from Tremere",
        "compulsion": "Perfectionism: Retry failed action or lose 3 dice from other pools"
    },
    "Ventrue": {
        "disciplines": ["Dominate", "Fortitude", "Presence"],
        "bane": "Rarefied Taste: Can only feed from specific type of mortal (player chosen)",
        "compulsion": "Arrogance: Must dominate situation or lose 2 dice from actions"
    },
    "Caitiff": {
        "disciplines": [],  # Choose any 2 disciplines at character creation
        "bane": "Suspect Blood: Ostracized by Camarilla, -1 die to Social with non-Caitiff",
        "compulsion": "None (varies by individual)"
    },
    "Thin-Blood": {
        "disciplines": ["Thin-Blood Alchemy"],  # Plus 1 discipline with weakness
        "bane": "Thin Blood: No Blood Potency, can't create blood bonds or ghouls",
        "compulsion": "None (varies by individual)"
    },
    # Additional clans (unlockable via admin approval)
    "Lasombra": {
        "disciplines": ["Dominate", "Oblivion", "Potence"],
        "bane": "No Reflection: No reflection in mirrors or recordings",
        "compulsion": "Ruthlessness: Must pursue goal regardless of cost or lose 2 dice"
    },
    "Tzimisce": {
        "disciplines": ["Animalism", "Dominate", "Protean"],
        "bane": "Grounded: Must sleep in homeland soil or lose 1 die cumulatively",
        "compulsion": "Covetousness: Must possess desired object/person or lose 2 dice"
    },
    "Ravnos": {
        "disciplines": ["Animalism", "Obfuscate", "Presence"],
        "bane": "Doomed Blood: Bane severity increases at Hunger 4+",
        "compulsion": "Tempting Fate: Must take unnecessary risk or lose 2 dice"
    },
    "Banu Haqim": {
        "disciplines": ["Blood Sorcery", "Celerity", "Obfuscate"],
        "bane": "Blood Addiction: Must make Hunger Frenzy test when smelling vampire blood",
        "compulsion": "Judgement: Must punish transgressor or lose 2 dice"
    },
    "Ministry": {
        "disciplines": ["Obfuscate", "Presence", "Protean"],
        "bane": "Light Sensitivity: +1 Aggravated damage from sunlight",
        "compulsion": "Transgression: Must corrupt someone or lose 2 dice"
    },
    "Salubri": {
        "disciplines": ["Auspex", "Dominate", "Fortitude"],
        "bane": "Third Eye: Visible third eye reveals vampire nature",
        "compulsion": "Affective Empathy: Must help person in distress or lose 3 dice"
    },
}

# ============================================================================
# DISCIPLINES (power levels 1-5)
# ============================================================================

# SKELETON ONLY - Full discipline powers defined in Phase 5
DISCIPLINES = {
    "Animalism": {
        "type": "standard",
        "description": "Commune with and command animals and the Beast",
        "powers": {}  # Populated in Phase 5
    },
    "Auspex": {
        "type": "standard",
        "description": "Supernatural senses and perception",
        "powers": {}  # Populated in Phase 5
    },
    "Blood Sorcery": {
        "type": "ritual",
        "description": "Blood magic and rituals",
        "powers": {},  # Populated in Phase 5
        "rituals": []  # Populated in Phase 5
    },
    "Celerity": {
        "type": "standard",
        "description": "Supernatural speed and reflexes",
        "powers": {}  # Populated in Phase 5
    },
    "Dominate": {
        "type": "standard",
        "description": "Mind control and mental commands",
        "powers": {}  # Populated in Phase 5
    },
    "Fortitude": {
        "type": "standard",
        "description": "Supernatural resilience and toughness",
        "powers": {}  # Populated in Phase 5
    },
    "Obfuscate": {
        "type": "standard",
        "description": "Supernatural stealth and invisibility",
        "powers": {}  # Populated in Phase 5
    },
    "Oblivion": {
        "type": "standard",
        "description": "Power over death and the Underworld",
        "powers": {}  # Populated in Phase 5
    },
    "Potence": {
        "type": "standard",
        "description": "Supernatural strength",
        "powers": {}  # Populated in Phase 5
    },
    "Presence": {
        "type": "standard",
        "description": "Supernatural charisma and emotion manipulation",
        "powers": {}  # Populated in Phase 5
    },
    "Protean": {
        "type": "standard",
        "description": "Shapeshifting and transformation",
        "powers": {}  # Populated in Phase 5
    },
    "Thin-Blood Alchemy": {
        "type": "thin-blood",
        "description": "Thin-blood formula crafting",
        "powers": {}  # Populated in Phase 9
    }
}

# ============================================================================
# PREDATOR TYPES
# ============================================================================

# SKELETON ONLY - Full predator mechanics defined in Phase 8
PREDATOR_TYPES = {
    "Alleycat": {
        "description": "Hunt the homeless and forgotten",
        "specialty": "Intimidation or Streetwise",
        "disciplines": [],  # Defined in Phase 8
        "merits": [],
        "flaws": []
    },
    "Bagger": {
        "description": "Feed from blood bags and hospitals",
        "specialty": "Medicine or Streetwise",
        "disciplines": [],
        "merits": [],
        "flaws": []
    },
    "Blood Leech": {
        "description": "Feed from other vampires",
        "specialty": "Brawl or Stealth",
        "disciplines": [],
        "merits": [],
        "flaws": []
    },
    "Cleaver": {
        "description": "Feed from a mortal family or group",
        "specialty": "Persuasion or Subterfuge",
        "disciplines": [],
        "merits": [],
        "flaws": []
    },
    "Consensualist": {
        "description": "Feed with permission and consent",
        "specialty": "Medicine or Persuasion",
        "disciplines": [],
        "merits": [],
        "flaws": []
    },
    "Farmer": {
        "description": "Feed from animals",
        "specialty": "Animal Ken or Survival",
        "disciplines": [],
        "merits": [],
        "flaws": []
    },
    "Osiris": {
        "description": "Cult leader who feeds from worshippers",
        "specialty": "Occult or Performance",
        "disciplines": [],
        "merits": [],
        "flaws": []
    },
    "Sandman": {
        "description": "Feed from sleeping victims",
        "specialty": "Medicine or Stealth",
        "disciplines": [],
        "merits": [],
        "flaws": []
    },
    "Scene Queen": {
        "description": "Feed from the party scene",
        "specialty": "Performance or Streetwise",
        "disciplines": [],
        "merits": [],
        "flaws": []
    },
    "Siren": {
        "description": "Seduce and feed",
        "specialty": "Persuasion or Subterfuge",
        "disciplines": [],
        "merits": [],
        "flaws": []
    },
}

# ============================================================================
# BLOOD POTENCY TABLE
# ============================================================================

BLOOD_POTENCY = {
    0: {
        "blood_surge": 0,
        "mend_amount": 1,
        "power_bonus": 0,
        "rouse_reroll": 0,
        "bane_severity": 0,
        "feeding_penalty": "No effect"
    },
    1: {
        "blood_surge": 1,
        "mend_amount": 1,
        "power_bonus": 0,
        "rouse_reroll": 0,
        "bane_severity": 1,
        "feeding_penalty": "No slaking from animals"
    },
    2: {
        "blood_surge": 2,
        "mend_amount": 2,
        "power_bonus": 1,
        "rouse_reroll": 1,
        "bane_severity": 1,
        "feeding_penalty": "No slaking from animals"
    },
    3: {
        "blood_surge": 2,
        "mend_amount": 2,
        "power_bonus": 1,
        "rouse_reroll": 1,
        "bane_severity": 2,
        "feeding_penalty": "No slaking from animals or bagged blood"
    },
    4: {
        "blood_surge": 3,
        "mend_amount": 3,
        "power_bonus": 2,
        "rouse_reroll": 2,
        "bane_severity": 2,
        "feeding_penalty": "No slaking from animals or bagged blood"
    },
    5: {
        "blood_surge": 3,
        "mend_amount": 3,
        "power_bonus": 2,
        "rouse_reroll": 2,
        "bane_severity": 3,
        "feeding_penalty": "Must drain and kill to slake at least 1 Hunger"
    },
    6: {
        "blood_surge": 4,
        "mend_amount": 3,
        "power_bonus": 3,
        "rouse_reroll": 3,
        "bane_severity": 3,
        "feeding_penalty": "Must drain and kill to slake at least 1 Hunger"
    },
    7: {
        "blood_surge": 4,
        "mend_amount": 4,
        "power_bonus": 3,
        "rouse_reroll": 3,
        "bane_severity": 4,
        "feeding_penalty": "Must drain and kill, only 1 Hunger per human"
    },
    8: {
        "blood_surge": 5,
        "mend_amount": 4,
        "power_bonus": 4,
        "rouse_reroll": 4,
        "bane_severity": 4,
        "feeding_penalty": "Must drain and kill, only 1 Hunger per human"
    },
    9: {
        "blood_surge": 5,
        "mend_amount": 5,
        "power_bonus": 4,
        "rouse_reroll": 4,
        "bane_severity": 5,
        "feeding_penalty": "Must drain and kill vampires (1 Hunger per vampire)"
    },
    10: {
        "blood_surge": 6,
        "mend_amount": 5,
        "power_bonus": 5,
        "rouse_reroll": 5,
        "bane_severity": 5,
        "feeding_penalty": "Must drain and kill vampires (1 Hunger per vampire)"
    }
}

# ============================================================================
# CHARACTER CREATION RULES
# ============================================================================

CHARGEN_RULES = {
    "attributes": {
        "starting_value": 1,  # All attributes start at 1
        "priority_pools": {
            "primary": 7,    # 7 dots to primary category
            "secondary": 5,  # 5 dots to secondary category
            "tertiary": 3    # 3 dots to tertiary category
        },
        "max_at_creation": 5  # Can't start higher than 5
    },
    "skills": {
        "starting_value": 0,  # Skills start at 0
        "priority_pools": {
            "primary": 13,   # 13 dots to primary category
            "secondary": 9,  # 9 dots to secondary category
            "tertiary": 5    # 5 dots to tertiary category
        },
        "max_at_creation": 5,  # Can't start higher than 5
        "specialties": 1  # 1 free specialty
    },
    "disciplines": {
        "in_clan_dots": 2,   # 2 dots in in-clan disciplines
        "out_clan_dots": 1,  # 1 dot in any discipline
        "max_at_creation": 3  # Can't start higher than 3
    },
    "backgrounds": {
        "dots": 3,  # 3 dots in backgrounds
        "max_per_background": 5
    },
    "starting_values": {
        "humanity": 7,
        "willpower": 0,  # Calculated: Composure + Resolve
        "health": 0,     # Calculated: Stamina + 3
        "hunger": 1,     # Start at Hunger 1
        "generation": 13,  # Standard fledgling
        "blood_potency": 0,  # Start at BP 0
        "experience": 0
    },
    "advantages": {
        "merits": 7,  # 7 dots in merits
        "flaws": 2    # Up to 2 dots in flaws for bonus points
    }
}

# ============================================================================
# EXPERIENCE COSTS
# ============================================================================

XP_COSTS = {
    "attribute": {
        "formula": "current * 5",
        "description": "Current rating × 5"
    },
    "skill": {
        "formula": "current * 3",
        "description": "Current rating × 3"
    },
    "specialty": {
        "cost": 3,
        "description": "Flat 3 XP"
    },
    "discipline": {
        "in_clan": {
            "formula": "current * 5",
            "description": "Current rating × 5 (in-clan)"
        },
        "out_clan": {
            "formula": "current * 7",
            "description": "Current rating × 7 (out of clan)"
        }
    },
    "ritual": {
        "cost": 3,
        "description": "Flat 3 XP per ritual level"
    },
    "thin_blood_formula": {
        "cost": 3,
        "description": "Flat 3 XP"
    },
    "background": {
        "formula": "current * 3",
        "description": "Current rating × 3"
    },
    "humanity": {
        "formula": "current * 10",
        "description": "Current rating × 10"
    },
    "willpower": {
        "cost": 8,
        "description": "Flat 8 XP per permanent dot"
    }
}

# ============================================================================
# MERITS & FLAWS (SKELETON)
# ============================================================================

# Full merit/flaw lists populated in Phase 8
MERITS = {}
FLAWS = {}

# ============================================================================
# RESONANCES (for Blood Potency/Feeding)
# ============================================================================

RESONANCES = {
    "Choleric": {
        "emotion": "Anger, rage, violence",
        "disciplines": ["Celerity", "Potence"],
        "dyscrasia": "Hot-blooded: +1 die to Physical feats for one scene"
    },
    "Melancholic": {
        "emotion": "Sadness, depression, fear",
        "disciplines": ["Fortitude", "Obfuscate"],
        "dyscrasia": "Icy: +1 die to Composure and Wits for one scene"
    },
    "Phlegmatic": {
        "emotion": "Calm, apathy, laziness",
        "disciplines": ["Auspex", "Dominate"],
        "dyscrasia": "Apathetic: +1 die to resist Dominate/Presence for one scene"
    },
    "Sanguine": {
        "emotion": "Joy, lust, passion",
        "disciplines": ["Blood Sorcery", "Presence"],
        "dyscrasia": "Passionate: +1 die to Persuasion and Performance for one scene"
    },
    "Animal": {
        "emotion": "Bestial (from animals)",
        "disciplines": ["Animalism", "Protean"],
        "dyscrasia": "Feral: +1 die to Survival and Animalism for one scene"
    }
}
