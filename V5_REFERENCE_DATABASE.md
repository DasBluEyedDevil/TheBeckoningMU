# Vampire: The Masquerade 5th Edition - Reference Database

**Purpose**: Comprehensive quick-reference for TheBeckoningMU development
**Last Updated**: 2025-01-19
**Sources**: V5 Core Rulebook, Reference Repository Analysis, V5 Wiki Research

---

## Table of Contents
1. [Core Mechanics](#core-mechanics)
2. [Character Statistics](#character-statistics)
3. [Clans](#clans)
4. [Disciplines](#disciplines)
5. [Predator Types](#predator-types)
6. [Advantages & Flaws](#advantages--flaws)
7. [Character Creation](#character-creation)
8. [Experience & Advancement](#experience--advancement)

---

## Core Mechanics

### Hunger System

Hunger replaces the traditional Blood Pool mechanic in V5. It represents a vampire's need for blood and proximity to the Beast.

| Hunger Level | State | Effects |
|--------------|-------|---------|
| 0 | Sated | Calm, collected, almost human |
| 1 | Peckish | Minor urges, easily controlled |
| 2 | Hungry | Notable cravings, Beast stirs |
| 3 | Ravenous | Dangerous territory, frenzy risk increases |
| 4 | Famished | Critical hunger, Beast very close |
| 5 | Starving | Can't slake Hunger below 1 without killing, constant frenzy danger |

**Rouse Checks**:
- Roll 1d10
- Success on 6+: No Hunger increase
- Failure on 1-5: Hunger increases by 1
- Cannot exceed Hunger 5

**When to Rouse**:
- Using discipline powers (most powers)
- Blood Surge (add dice to physical pools)
- Healing Superficial damage
- Rising for the night (if Hunger 4+)
- Blush of Life (appear human for a scene)

### Blood Potency

Blood Potency represents the inherent power of a vampire's vitae, increasing with age and generation.

| Level | Blood Surge | Feeding Penalty | Bane Severity | Power Bonus | Rouse Re-roll | Mend Amount |
|-------|-------------|-----------------|---------------|-------------|---------------|-------------|
| 0 | +1 | None | 0 | None | None | 1 Superficial |
| 1 | +2 | None | 1 | None | Level 1 | 1 Superficial |
| 2 | +2 | Animals 1/2 | 1 | +1 | Level 1 | 2 Superficial |
| 3 | +3 | Animals none, Bags 1/2 | 2 | +1 | Level 1-2 | 2 Superficial |
| 4 | +3 | Slake 1 less from humans | 2 | +2 | Level 1-2 | 3 Superficial |
| 5 | +4 | Slake 2 less from humans | 3 | +2 | Level 1-3 | 3 Superficial |
| 6 | +4 | Must drain and kill to reduce Hunger below 2 | 3 | +3 | Level 1-3 | 3 Superficial |
| 7 | +5 | Must drain and kill to reduce Hunger below 2 | 4 | +3 | Level 1-4 | 4 Superficial |
| 8 | +5 | Must drain and kill to reduce Hunger below 3 | 4 | +4 | Level 1-4 | 4 Superficial |
| 9 | +6 | Must drain and kill to reduce Hunger below 3 | 5 | +4 | Level 1-5 | 5 Superficial |
| 10 | +6 | Must drain and kill to reduce Hunger below 4 | 5 | +5 | Level 1-5 | 5 Superficial |

**Blood Potency Advancement**:
- +1 dot per 100 years active
- -1 dot per 50 years in torpor
- Can be increased through diablerie
- Maximum determined by Generation

### Resonance

Blood Resonance represents the emotional/psychological state of a vessel, affecting discipline use.

| Resonance | Associated Emotions | Disciplines Enhanced | Dyscrasia (Intense) |
|-----------|--------------------|--------------------|---------------------|
| **Choleric** | Angry, violent, bullying, passionate, envious | Celerity, Potence | Temporary bonus to Physical rolls |
| **Melancholic** | Sad, depressed, intellectual, contemplative | Fortitude, Obfuscate | Temporary bonus to Mental rolls |
| **Phlegmatic** | Calm, lazy, apathetic, controlling | Auspex, Dominate | Temporary bonus to composure |
| **Sanguine** | Horny, happy, enthusiastic, flighty, addicted | Blood Sorcery, Presence | Temporary bonus to Social rolls |
| **Animal Blood** | N/A - from animals | Animalism, Protean | Different effects based on animal type |

**Resonance Benefits**:
- **Intense Resonance**: +1 die to associated disciplines until next feeding
- **Acute Resonance** (Dyscrasia): Special temporary merit-like effects, typically requires draining/killing the vessel or feeding over 3 nights

### Dice Rolling Mechanics

**Basic Roll**:
- Pool = Attribute + Skill + Modifiers
- Roll d10 equal to pool size
- Success = 6, 7, 8, 9 (1 success each)
- Critical = 10 (counts as 2 successes)
- Pair of 10s = Critical Win (4 successes, dramatic success)

**Hunger Dice**:
- Replace regular dice equal to current Hunger
- Different color/marked separately
- Count successes normally BUT:
  - **Bestial Failure**: Only Hunger dice show 1s on a failed roll → Compulsion
  - **Messy Critical**: Hunger dice contribute to a critical → Success but with catastrophic side effect

**Difficulty**:
- Number of successes needed
- Difficulty 2 = routine task
- Difficulty 3-4 = challenging
- Difficulty 5+ = very difficult
- Contested rolls = opposed pools, margin of success matters

**Willpower**:
- Spend 1 Willpower to reroll up to 3 regular dice (not Hunger dice)
- Max Willpower = Composure + Resolve
- Regain through role play, rest, fulfilling character goals

---

## Character Statistics

### Attributes

Attributes represent innate capabilities. All vampires have ratings of 1-5 in each.

#### Physical Attributes
| Attribute | Description |
|-----------|-------------|
| **Strength** | Physical power, muscle, brute force |
| **Dexterity** | Agility, grace, reflexes, fine motor control |
| **Stamina** | Endurance, resilience, toughness, constitution |

#### Social Attributes
| Attribute | Description |
|-----------|-------------|
| **Charisma** | Charm, magnetism, ability to inspire |
| **Manipulation** | Ability to deceive, influence, control |
| **Composure** | Self-control, grace under pressure, emotional regulation |

#### Mental Attributes
| Attribute | Description |
|-----------|-------------|
| **Intelligence** | Reasoning, memory, analytical capability |
| **Wits** | Cunning, quick thinking, situational awareness |
| **Resolve** | Determination, focus, mental fortitude |

**Starting Values**: 1 dot in each attribute (all characters are at least average mortals)

**Attribute Dots**:
- 1 dot = Poor/Below average
- 2 dots = Average
- 3 dots = Good/Above average
- 4 dots = Exceptional
- 5 dots = Peak human/supernatural

### Skills

Skills represent trained abilities and learned knowledge. Rating 0 = untrained (can still attempt rolls).

#### Physical Skills
| Skill | Description | Example Uses |
|-------|-------------|--------------|
| **Athletics** | Running, jumping, climbing, swimming, parkour | Chase scenes, acrobatics, endurance |
| **Brawl** | Unarmed combat, grappling, martial arts | Hand-to-hand combat, wrestling |
| **Craft** | Creating and repairing physical objects | Building, mechanics, art |
| **Drive** | Operating vehicles | Car chases, getaways, stunts |
| **Firearms** | Shooting guns of all types | Ranged combat, gun maintenance |
| **Larceny** | Lock picking, pickpocketing, security | Break-ins, theft, bypassing alarms |
| **Melee** | Armed combat with melee weapons | Sword fights, improvised weapons |
| **Stealth** | Moving unseen and unheard | Sneaking, hiding, shadowing |
| **Survival** | Wilderness skills, tracking, foraging | Navigation, hunting, outdoor survival |

#### Social Skills
| Skill | Description | Example Uses |
|-------|-------------|--------------|
| **Animal Ken** | Understanding and influencing animals | Calming beasts, training, reading animal moods |
| **Etiquette** | Social graces, protocol, proper behavior | Court intrigue, formal events, avoiding faux pas |
| **Insight** | Reading people, detecting lies, empathy | Sensing motives, detecting deception |
| **Intimidation** | Coercion through fear or threat | Interrogation, making threats, dominance |
| **Leadership** | Inspiring and directing others | Rallying groups, giving orders, inspiring loyalty |
| **Performance** | Artistic expression, entertainment | Acting, music, public speaking |
| **Persuasion** | Convincing others through reason or charm | Negotiation, seduction, diplomacy |
| **Streetwise** | Urban survival, criminal knowledge | Finding black markets, gang politics, rumor mill |
| **Subterfuge** | Lying, disguise, misdirection | Creating alibis, fast-talking, maintaining cover |

#### Mental Skills
| Skill | Description | Example Uses |
|-------|-------------|--------------|
| **Academics** | Scholarly knowledge, research, humanities | History, literature, research |
| **Awareness** | Noticing details, perception, alertness | Spotting ambushes, noticing clues |
| **Finance** | Money management, economics, business | Accounting, investments, market analysis |
| **Investigation** | Solving mysteries, gathering evidence | Crime scenes, research, connecting dots |
| **Medicine** | Medical knowledge, first aid, anatomy | Treating wounds, diagnosis, forensics |
| **Occult** | Supernatural lore, mysticism, rituals | Recognizing supernatural, ritual knowledge |
| **Politics** | Government, power structures, diplomacy | Court intrigue, understanding hierarchies |
| **Science** | Natural sciences, chemistry, biology | Lab work, analysis, technical knowledge |
| **Technology** | Computers, electronics, modern tech | Hacking, programming, surveillance |

**Skill Dots**:
- 0 dots = Untrained (roll attribute only)
- 1 dot = Novice/Student
- 2 dots = Professional/Practiced
- 3 dots = Expert/Veteran
- 4 dots = Master
- 5 dots = World-class

**Specialties**: At 4+ dots in a skill, gain a specialty (specific area of expertise). Gain +1 die when specialty applies.

### Pools & Derived Stats

| Pool | Calculation | Description |
|------|-------------|-------------|
| **Health** | Stamina + 3 | Physical well-being, damage capacity |
| **Willpower** | Composure + Resolve | Mental/emotional resilience, spend to reroll |
| **Humanity** | Varies (typically starts 7) | Connection to mortal ethics, distance from Beast |
| **Blood Potency** | Based on Age/Generation | Power of vampiric blood |
| **Hunger** | Tracks current state (0-5) | Need for blood, proximity to Beast |

**Damage Types**:
- **Superficial Damage**: Minor wounds, healed easily with vitae (marked with /)
- **Aggravated Damage**: Serious injuries, harder to heal (marked with X)
- **Impairment**: When Health filled with Superficial, halve all Physical pools
- **Torpor**: When Health filled with Aggravated damage

---

## Clans

The thirteen recognized clans (plus Caitiff and Thin-bloods) each have distinct characteristics, disciplines, and weaknesses.

### Banu Haqim (Assamites)
**Sobriquet**: Assassins
**In-Clan Disciplines**: Blood Sorcery, Celerity, Obfuscate
**Clan Bane**: When slaking at least one Hunger from another vampire, must make Hunger Frenzy test at Difficulty 2 + Bane Severity. On failure, must gorge themselves on vampiric vitae.
**Compulsion**: Judgment - Must punish those who transgress laws or personal code

**Typical Roles**: Judges, assassins, scholars, warriors

### Brujah
**Sobriquet**: Rebels, Rabble
**In-Clan Disciplines**: Celerity, Potence, Presence
**Clan Bane**: Rage simmers beneath the surface. Suffer penalty equal to Bane Severity on rolls to resist Fury Frenzy.
**Compulsion**: Rebellion - Must resist authority or status quo, even when detrimental

**Typical Roles**: Anarchs, rebels, street fighters, idealists, philosophers

### Caitiff
**Sobriquet**: Clanless
**In-Clan Disciplines**: Choose any 3
**Clan Bane**: None (but suffer social stigma)
**Compulsion**: None specific

**Typical Roles**: Outcasts, unknowns, those of uncertain lineage

### Gangrel
**Sobriquet**: Outlanders, Ferals
**In-Clan Disciplines**: Animalism, Fortitude, Protean
**Clan Bane**: When in Frenzy, gain animal features equal to Bane Severity, lasting one additional night. Each feature reduces one Attribute by 1. (Can Ride the Wave to only manifest one feature)
**Compulsion**: Feral Impulses - Must give in to bestial urges, flee civilization

**Typical Roles**: Wanderers, survivalists, shapeshifters, loners

### Hecata
**Sobriquet**: Necromancers (subsumes Giovanni, Cappadocian bloodlines)
**In-Clan Disciplines**: Auspex, Fortitude, Oblivion
**Clan Bane**: Their Kiss causes excruciating pain (no  Blush of Life benefit for feeding). Inflicts Aggravated Willpower damage equal to Bane Severity on vessels.
**Compulsion**: Morbidity - Must involve themselves with death, decay, or the dead

**Typical Roles**: Necromancers, death scholars, cryptkeepers

### Lasombra
**Sobriquet**: Magisters, Night Clan
**In-Clan Disciplines**: Dominate, Oblivion, Potence
**Clan Bane**: Cameras and mirrors don't capture their image properly (shows distortion equal to Bane Severity). Modern surveillance makes Masquerade difficult.
**Compulsion**: Ruthlessness - Must dominate situation, brook no defiance

**Typical Roles**: Leaders, shadows, manipulators, former Sabbat elite

### Malkavian
**Sobriquet**: Lunatics, Madmen
**In-Clan Disciplines**: Auspex, Dominate, Obfuscate
**Clan Bane**: When suffering Bestial Failure or Compulsion, suffer penalty equal to Bane Severity to one category of dice pools (Physical, Social, or Mental) for the entire scene.
**Compulsion**: Delusion - Must pursue irrational insight or fixation

**Typical Roles**: Seers, prophets, madmen, cryptic advisors

### The Ministry (Followers of Set, Setites)
**Sobriquet**: Setites, Snakes
**In-Clan Disciplines**: Obfuscate, Presence, Protean
**Clan Bane**: Take Aggravated damage from sunlight as if Bane Severity higher. Suffer penalties in bright light equal to Bane Severity.
**Compulsion**: Transgression - Must tempt others into breaking their principles

**Typical Roles**: Tempters, dealers, cultists, liberators

### Nosferatu
**Sobriquet**: Sewer Rats, Haunts
**In-Clan Disciplines**: Animalism, Obfuscate, Potence
**Clan Bane**: Hideous appearance causes Social penalty equal to Bane Severity except Intimidation. Cannot increase Looks-related Merits. Automatically break Masquerade if seen by mortals.
**Compulsion**: Cryptophilia - Must uncover secrets, cannot resist information gathering

**Typical Roles**: Information brokers, spies, lurkers in shadows

### Ravnos
**Sobriquet**: Charlatans, Deceivers
**In-Clan Disciplines**: Animalism, Obfuscate, Presence
**Clan Bane**: Must make penalty test equal to Bane Severity when resisting Temptation Compulsion.
**Compulsion**: Temptation - Must indulge in specific vice or criminal act

**Typical Roles**: Travelers, tricksters, daredevils, thieves

### Salubri
**Sobriquet**: Cyclops, Unicorns
**In-Clan Disciplines**: Auspex, Dominate, Fortitude
**Clan Bane**: When slaking Hunger from a mortal, must do so completely (reducing Hunger to 0) or gain Stain equal to Bane Severity. Third eye appears when using disciplines, causing superstitious dread.
**Compulsion**: Affective Empathy - Must help those in pain or need

**Typical Roles**: Healers, warriors, martyrs (very rare)

### Toreador
**Sobriquet**: Degenerates, Artistes
**In-Clan Disciplines**: Auspex, Celerity, Presence
**Clan Bane**: Can become entranced by beauty, art, or their passion. Penalty equal to Bane Severity to resist distraction.
**Compulsion**: Obsession - Must pursue current passion/art to exclusion of all else

**Typical Roles**: Artists, socialites, patrons, hedonists

### Tremere
**Sobriquet**: Warlocks, Usurpers
**In-Clan Disciplines**: Auspex, Blood Sorcery, Dominate
**Clan Bane**: Cannot create Blood Bonds with other Kindred (though they can be Bound by others). To Blood Bond mortals, must feed additional times equal to Bane Severity.
**Compulsion**: Perfectionism - Must succeed completely or consider endeavor worthless

**Typical Roles**: Blood sorcerers, scholars, pyramid members

### Tzimisce
**Sobriquet**: Fiends, Fleshcrafters
**In-Clan Disciplines**: Animalism, Dominate, Protean
**Clan Bane**: Must sleep in their "Haven" (place of significance with at least two handfuls of their native soil). Each night away from Haven applies cumulative penalty equal to Bane Severity to all rolls.
**Compulsion**: Covetousness - Must possess specific person, object, or place

**Typical Roles**: Flesh crafters, lords, possessive masters

### Ventrue
**Sobriquet**: Blue Bloods, Patricians
**In-Clan Disciplines**: Dominate, Fortitude, Presence
**Clan Bane**: Can only feed from a specific type of mortal (specific blood type, social class, profession, etc.). Feeding from others provides no sustenance.
**Compulsion**: Arrogance - Must lead, dominate, or prove superiority

**Typical Roles**: Leaders, CEOs, princes, aristocrats

### Thin-Bloods (Duskborn)
**Sobriquet**: Duskborn, the Thin-Blooded
**In-Clan Disciplines**: None (have Thin-Blood Alchemy)
**Clan Bane**: Reduced vitae capacity (cannot store more than Thin-Blood Alchemy level). Sunlight causes Aggravated damage but not instant death.
**Compulsion**: None (or varies)

**Special Traits**:
- Can walk in daylight (with damage)
- May be mortal-passing (can eat food, have sex, etc.)
- Can learn limited Thin-Blood Alchemy
- Often develop unique "Thin-Blood Merits"

---

## Disciplines

Disciplines are supernatural powers fueled by vampiric blood. Each discipline has powers at levels 1-5, with some requiring amalgams (multiple disciplines).

### Animalism

**Theme**: Command over beasts and bestial nature

| Level | Powers | Rouse | Dice Pool | Amalgam |
|-------|--------|-------|-----------|---------|
| **1** | **Bond Famulus** | Yes | Charisma + Animal Ken | - |
|  | Create supernatural bond with one animal, mental communication | | | |
|  | **Sense the Beast** | No | Resolve + Animalism | - |
|  | Sense presence and emotional state of animals and vampires nearby | | | |
| **2** | **Feral Whispers** | Yes | Manipulation/Charisma + Animalism | - |
|  | Communicate with and command animals | | | |
| **3** | **Animal Succulence** | No | - | - |
|  | Slake 1 additional Hunger when feeding from animals | | | |
|  | **Quell the Beast** | Yes | Charisma/Manipulation + Animalism | - |
|  | Calm or rouse the Beast in others | | | |
|  | **Living Hive** | Yes | Composure + Animalism | Obfuscate 2 |
|  | Infest body with stinging insects for defense and concealment | | | |
| **4** | **Subsume the Spirit** | Yes | Manipulation + Animalism | - |
|  | Project consciousness into animal, control it fully | | | |
| **5** | **Animal Dominion** | Yes | Charisma + Animalism | - |
|  | Command multiple animals or swarms simultaneously | | | |
|  | **Draw Out the Beast** | Yes | Charisma + Animalism | - |
|  | Force another's Beast into frenzy or calm it entirely | | | |

### Auspex

**Theme**: Supernatural senses and perception

| Level | Powers | Rouse | Dice Pool | Amalgam |
|-------|--------|-------|-----------|---------|
| **1** | **Heightened Senses** | No | Wits/Resolve + Auspex | - |
|  | Dramatically enhance all five senses | | | |
|  | **Sense the Unseen** | No | Wits/Resolve + Auspex | - |
|  | Detect supernatural presences (Obfuscate, ghosts, magic) | | | |
| **2** | **Premonition** | No | Resolve + Auspex | - |
|  | Get glimpses of danger or future events | | | |
| **3** | **Scry the Soul** | Yes | Intelligence + Auspex | - |
|  | Read aura, discern emotional state, vampiric nature, resonance | | | |
|  | **Share the Senses** | Yes | Resolve + Auspex | - |
|  | See/hear through another's senses remotely | | | |
| **4** | **Spirit's Touch** | No | Intelligence + Auspex | - |
|  | Read psychic impressions from objects (psychometry) | | | |
| **5** | **Clairvoyance** | Yes | Intelligence + Auspex | - |
|  | Project senses to a distant familiar location | | | |
|  | **Possession** | Yes | Resolve + Auspex | Dominate 3 |
|  | Fully possess another person's body | | | |
|  | **Telepathy** | Yes | Resolve + Auspex | - |
|  | Read surface thoughts, project thoughts, mental communication | | | |

### Blood Sorcery

**Theme**: Rituals and blood magic

*Blood Sorcery is unique: rating determines ritual level learned. Most effects require rituals, not instant powers.*

| Level | Powers/Rituals | Rouse | Dice Pool | Notes |
|-------|----------------|-------|-----------|-------|
| **1** | **Corrosive Vitae** | Yes | Strength + Blood Sorcery | Instant power |
|  | Spit vitae as acid weapon | | | |
|  | **Blood of Potency** (ritual) | - | Intelligence + Blood Sorcery | Level 1 Ritual |
|  | Temporarily raise Blood Potency | | | |
| **2** | **Extinguish Vitae** (ritual) | - | Intelligence + Blood Sorcery | Level 2 Ritual |
|  | Paralyze a vampire's limb | | | |
|  | **Ward Against Ghouls** (ritual) | - | Intelligence + Blood Sorcery | Level 2 Ritual |
| **3** | **Scorpion's Touch** | Yes | Strength + Blood Sorcery | Instant power |
|  | Vitae becomes paralyzing poison in melee | | | |
|  | **Incorporeal Passage** (ritual) | - | Intelligence + Blood Sorcery | Level 3 Ritual |
|  | Walk through walls | | | |
| **4** | **Theft of Vitae** | Yes | Wits + Blood Sorcery | Instant power |
|  | Drain vitae from target at a distance | | | |
| **5** | **Cauldron of Blood** | Yes | Manipulation + Blood Sorcery | Instant power |
|  | Boil victim's blood, causing massive damage | | | |

**Ritual Casting**: Requires time (varies by level), ingredients, and Intelligence + Blood Sorcery roll.

### Celerity

**Theme**: Supernatural speed

| Level | Powers | Rouse | Dice Pool | Amalgam |
|-------|--------|-------|-----------|---------|
| **1** | **Cat's Grace** | Yes | - | - |
|  | Gain automatic success on Dexterity + Athletics roll | | | |
|  | *Passive:* Add Celerity rating to Defense | | | |
| **2** | **Fleetness** | Yes | - | - |
|  | Double movement speed for scene | | | |
| **3** | **Blink** | Yes | - | - |
|  | Move short distance instantly (appears to teleport) | | | |
|  | **Traversal** | Yes | - | - |
|  | Scale walls, run across water, perform impossible movements | | | |
| **4** | **Draught of Elegance** | Yes | - | - |
|  | Gain Celerity rating as bonus dice to Dexterity rolls for scene | | | |
|  | **Unerring Aim** | Yes | - | Auspex 2 |
|  | Automatically hit target with ranged attack | | | |
| **5** | **Lightning Strike** | Yes | - | - |
|  | Make multiple attacks in single turn | | | |
|  | **Split Second** | Yes | Wits + Awareness | - |
|  | Act first in turn order, interrupt actions | | | |

### Dominate

**Theme**: Mind control and mental manipulation

| Level | Powers | Rouse | Dice Pool | Amalgam |
|-------|--------|-------|-----------|---------|
| **1** | **Cloud Memory** | Yes | Charisma + Dominate | - |
|  | Remove or alter short-term memories | | | |
|  | **Compel** | Yes | Charisma/Manipulation + Dominate | - |
|  | Issue one-word command target must obey | | | |
| **2** | **Mesmerize** | Yes | Charisma/Manipulation + Dominate | - |
|  | Issue complex hypnotic commands | | | |
|  | **Dementation** | Yes | Manipulation + Dominate | Obfuscate 2 |
|  | Drive target temporarily insane with hallucinations | | | |
|  | **Submerged Directive** | Yes | Manipulation + Dominate | - |
|  | Plant delayed trigger command | | | |
| **3** | **The Forgetful Mind** | Yes | Manipulation + Dominate | - |
|  | Rewrite or remove extensive memories | | | |
| **4** | **Rationalize** | Yes | Manipulation + Dominate | - |
|  | Make victim justify/accept anything | | | |
| **5** | **Mass Manipulation** | Yes | Charisma + Dominate | - |
|  | Dominate multiple targets simultaneously | | | |
|  | **Terminal Decree** | Yes | Manipulation + Dominate | - |
|  | Implant suicidal or self-destructive command | | | |

**Dominate Restrictions**: Typically requires eye contact and won't work on other vampires with higher Blood Potency (unless Storyteller decides otherwise for drama).

### Fortitude

**Theme**: Supernatural resilience and endurance

| Level | Powers | Rouse | Dice Pool | Amalgam |
|-------|--------|-------|-----------|---------|
| **1** | **Resilience** | Yes | - | - |
|  | Add Fortitude rating to Health for scene | | | |
|  | **Unswayable Mind** | Yes | - | - |
|  | Add Fortitude rating to Resolve or Composure for resisting mental attacks | | | |
| **2** | **Toughness** | No (Passive) | - | - |
|  | Reduce Aggravated damage from fire/sunlight by 1 per Bane Severity | | | |
|  | **Enduring Beast** | Yes | Stamina + Survival | - |
|  | Ignore physical damage penalties for scene | | | |
| **3** | **Fortify the Inner Facade** | Yes | Stamina + Fortitude | - |
|  | Superficial damage becomes bashing for mortals witnessing violence | | | |
| **4** | **Draught of Endurance** | Yes | - | - |
|  | Add Fortitude rating as bonus dice to Stamina rolls for scene | | | |
| **5** | **Flesh of Marble** | Yes | Composure + Fortitude | - |
|  | Become nearly invulnerable to physical harm | | | |
|  | **Prowess from Pain** | Yes | - | - |
|  | Convert Health damage into bonus dice | | | |

### Obfuscate

**Theme**: Supernatural stealth, illusion, and invisibility

| Level | Powers | Rouse | Dice Pool | Amalgam |
|-------|--------|-------|-----------|---------|
| **1** | **Cloak of Shadows** | Yes | Wits + Obfuscate | - |
|  | Become invisible while stationary | | | |
|  | **Silence of Death** (variant) | Yes | - | - |
|  | Suppress all sound you make | | | |
| **2** | **Unseen Passage** | Yes | Wits + Obfuscate | - |
|  | Remain invisible while moving | | | |
| **3** | **Ghost in the Machine** | Yes | Manipulation + Obfuscate | - |
|  | Erase digital presence, disappear from cameras | | | |
|  | **Mask of a Thousand Faces** | Yes | Manipulation + Obfuscate | - |
|  | Appear as a different person | | | |
| **4** | **Conceal** | Yes | Wits + Obfuscate | - |
|  | Hide objects or other people | | | |
| **5** | **Vanish** | Yes | - | - |
|  | Disappear instantly, even while observed | | | |
|  | **Imposter's Guise** | Yes | Manipulation + Obfuscate | - |
|  | Perfectly mimic specific person (voice, mannerisms, etc.) | | | |

**Obfuscate Notes**: Obfuscate affects perception, not physical presence. Breaking Masquerade (attack, loud noise) breaks illusion. Electronics may capture you if not using Ghost in the Machine.

### Oblivion

**Theme**: Death, shadows, necromancy

*Oblivion has two paths: Shadow (Lasombra) and Necromancy (Hecata). Can learn from both but typically specialize.*

#### Shadow Path

| Level | Powers | Rouse | Dice Pool | Notes |
|-------|--------|-------|-----------|-------|
| **1** | **Shadow Cloak** | Yes | - | Obfuscate 1 equivalent using shadows |
|  | **Oblivion's Sight** | No | Resolve + Oblivion | See into lands of the dead |
| **2** | **Tenebrous Avatar** | Yes | - | Become shadow-form |
| **3** | **Shadow Cast** | Yes | Manipulation + Oblivion | Control shadows to attack or manipulate |
| **4** | **Shadow Perspective** | Yes | Intelligence + Oblivion | Scry through shadows |
| **5** | **Shadowstep** | Yes | - | Teleport through shadows |

#### Necromancy Path

| Level | Powers | Rouse | Dice Pool | Notes |
|-------|--------|-------|-----------|-------|
| **1** | **Binding the Fetters** (ritual) | - | Intelligence + Oblivion | Strengthen ghost anchors |
| **2** | **Where the Shroud Thins** (ritual) | - | Intelligence + Oblivion | Find weak points in death barrier |
| **3** | **Summon Spirit** | Yes | Intelligence + Oblivion | Call ghost to appear |
| **4** | **Compel Spirit** | Yes | Manipulation + Oblivion | Force ghost to obey |
| **5** | **Shambling Hordes** | Yes | Intelligence + Oblivion | Animate corpses |

### Potence

**Theme**: Supernatural strength

| Level | Powers | Rouse | Dice Pool | Amalgam |
|-------|--------|-------|-----------|---------|
| **1** | **Lethal Body** | Yes | - | - |
|  | Unarmed attacks deal +1 damage, can be Aggravated | | | |
|  | **Soaring Leap** | Yes | - | - |
|  | Jump incredible distances | | | |
| **2** | **Prowess** | Yes | - | - |
|  | Add Potence rating as bonus dice to Strength rolls for scene | | | |
| **3** | **Brutal Feed** | No (Passive) | - | - |
|  | Gain additional Resonance benefit when feeding violently | | | |
| **4** | **Spark of Rage** | Yes | - | Presence 3 |
|  | Cause frenzy in nearby vampires | | | |
| **5** | **Earthshock** | Yes | Strength + Potence | - |
|  | Shockwave knocks down all nearby | | | |
|  | **Fist of Caine** | Yes | - | - |
|  | One devastating attack causing massive damage | | | |

### Presence

**Theme**: Supernatural charisma and emotional manipulation

| Level | Powers | Rouse | Dice Pool | Amalgam |
|-------|--------|-------|-----------|---------|
| **1** | **Awe** | Yes | Charisma/Manipulation + Presence | - |
|  | Become magnetic center of attention | | | |
|  | **Daunt** | Yes | Charisma/Manipulation + Presence | - |
|  | Inspire terror in onlookers | | | |
| **2** | **Lingering Kiss** | No (Passive) | - | - |
|  | Your Kiss causes euphoria, not pain | | | |
| **3** | **Dread Gaze** | Yes | Charisma/Manipulation + Presence | - |
|  | Paralyze target with terror | | | |
|  | **Entrancement** | Yes | Charisma/Manipulation + Presence | - |
|  | Create obsessive fascination/love in target | | | |
| **4** | **Irresistible Voice** | Yes | Manipulation + Presence | - |
|  | Commands carry supernatural compulsion | | | |
|  | **Summon** | Yes | Manipulation + Presence | - |
|  | Call target to your location (they must come) | | | |
| **5** | **Majesty** | Yes | Charisma + Presence | - |
|  | Radiate such magnificence others cannot act against you | | | |
|  | **Star Magnetism** | Yes | Charisma + Presence | - |
|  | Affect large crowds with Presence powers | | | |

### Protean

**Theme**: Shapeshifting and bestial transformation

| Level | Powers | Rouse | Dice Pool | Amalgam |
|-------|--------|-------|-----------|---------|
| **1** | **Eyes of the Beast** | Yes | - | - |
|  | See perfectly in darkness, eyes glow red | | | |
|  | **Weight of the Feather** | Yes | - | - |
|  | Reduce falling damage, land gracefully | | | |
| **2** | **Feral Weapons** | Yes | - | - |
|  | Grow claws dealing Aggravated damage | | | |
|  | **Metamorphosis** | Yes | Stamina + Protean | - |
|  | Transform into animal form (bat, wolf, rat) | | | |
| **3** | **Shapechange** | Yes | - | - |
|  | Transform into mist form | | | |
|  | **Earth Meld** | Yes | - | - |
|  | Merge with earth/stone for day sleep | | | |
| **4** | **One with the Beast** (variant) | Yes | - | - |
|  | Remain conscious while in frenzy | | | |
|  | **Fleshcraft** | Yes | Dexterity + Protean | - |
|  | Sculpt flesh (self or others) | | | |
| **5** | **Horrid Form** | Yes | - | - |
|  | Transform into massive combat monster | | | |
|  | **The Unfettered Heart** (ritual) | - | Intelligence + Protean | - |
|  | Remove heart from body, hide it elsewhere | | | |

### Thin-Blood Alchemy

*Exclusive to Thin-Bloods, limited supernatural chemistry*

| Level | Formulae | Blood Cost | Notes |
|-------|----------|-----------|-------|
| **1** | **Far Reach** | 1 Rouse | Telekinesis on light objects |
|  | **Haze** | 1 Rouse | Obfuscate-like concealment |
| **2** | **Envelop** | 1 Rouse | Fortitude-like durability |
|  | **Counterfeit** | 1 Rouse | Temporary discipline mimicry |
| **3** | **Defraktionierung** | 2 Rouses | Distill disciplines from elder vitae |
|  | **Awaken the Sleeper** | 1 Rouse | Temporarily raise Blood Potency |

**Notes**: Thin-Blood Alchemy requires preparation, creating "tonics" that can be consumed. Effects typically last one scene.

---

## Predator Types

Predator Types represent how a vampire hunts and feeds, chosen at character creation. Each provides:
- Two dots of Disciplines or Skill Specialties
- One Advantage (Merit or Background)
- One or more Flaws
- Humanity gain/loss

### Core Predator Types

| Predator | Disciplines/Skills | Advantage | Flaw | Humanity |
|----------|-------------------|-----------|------|----------|
| **Alleycat** | +1 Celerity or Potence<br>+1 Stealth | Streetwise Contacts | Dark Secret or Disliked | 7 |
| Feeds through violence on urban prey | | | | |
| | | | | |
| **Bagger** | +1 Blood Sorcery or Obfuscate<br>+1 Streetwise | Iron Gullet (2 pt) | Shunned | 7 |
| Feeds from blood bags, hospital sources | | | | |
| | | | | |
| **Blood Leech** | +1 Celerity or Protean<br>+1 Brawl | Caitiff or Thin-Blood | Enemy (2 pt) | 7 |
| Feeds from other vampires | | | | |
| | | | | |
| **Cleaver** | +1 Dominate or Animalism<br>+1 Persuasion or Subterfuge | Herd (2 pt) or Fame | Dark Secret (Masquerade breacher) | 6 |
| Feeds from family/controlled group | | | | |
| | | | | |
| **Consensualist** | +1 Auspex or Fortitude<br>+1 Medicine or Performance | Contacts (1 pt) | Prey Exclusion (non-consenting) | 8 |
| Only feeds from willing vessels | | | | |
| | | | | |
| **Extortionist** | +1 Dominate or Potence<br>+1 Intimidation or Larceny | Resources or Criminal Contacts | Enemy (crime figures) | 7 |
| Feeds through coercion, protection rackets | | | | |
| | | | | |
| **Farmer** | +1 Animalism or Protean<br>+1 Animal Ken | Herd (animals) | Prey Exclusion (humans)<br>Obvious Predator | 8 |
| Feeds exclusively from animals | | | | |
| | | | | |
| **Graverobber** | +1 Fortitude or Oblivion<br>+1 Occult or Medicine | Allies (morticians) or Haven | Folkloric Bane or Stigmata | 7 |
| Feeds from recently dead or those in graveyards | | | | |
| | | | | |
| **Sandman** | +1 Auspex or Obfuscate<br>+1 Stealth | Resources (2 pt) | Dark Secret or Suspect | 7 |
| Feeds from sleeping victims (breaking and entering) | | | | |
| | | | | |
| **Scene Queen** | +1 Dominate or Potence<br>+1 Intimidation or Streetwise | Fame (1 pt) or Contact | Disliked or Rival | 7 |
| Feeds in subculture scene (clubs, goth scene, etc.) | | | | |
| | | | | |
| **Siren** | +1 Fortitude or Presence<br>+1 Persuasion or Subterfuge | Looks (2 pt) or Resources | Enemy or Rival | 7 |
| Feeds during or while feigning sex | | | | |

### Additional Predator Types (Supplements)

| Predator | Disciplines/Skills | Advantage | Flaw | Humanity |
|----------|-------------------|-----------|------|----------|
| **Grim Reaper** | +1 Oblivion or Potence<br>+1 Medicine | Iron Gullet | Prey Exclusion (healthy) | 6 |
| Feeds from terminally ill or dying | | | | |
| | | | | |
| **Montero** | +1 Celerity or Presence<br>+1 Survival | Herd (travelers) | Folkloric Block | 7 |
| Feeds from travelers on lonely roads | | | | |
| | | | | |
| **Osiris** | +1 Blood Sorcery or Presence<br>+1 Occult | Cult (3 pt Background) | Enemies (rival cults) | 6 |
| Feeds from cult worshipers who revere you as god | | | | |
| | | | | |
| **Pursuer** | +1 Animalism or Presence<br>+1 Survival or Investigation | Bloodhound | Obsession (the hunt) | 7 |
| Feeds after elaborate hunt/chase | | | | |
| | | | | |
| **Roadside Killer** | +1 Celerity or Obfuscate<br>+1 Drive | Mask (mobile haven) | Disliked | 6 |
| Feeds from hitchhikers and travelers | | | | |
| | | | | |
| **Trapdoor** | +1 Protean or Obfuscate<br>+1 Larceny or Stealth | Resources or Haven | Suspect or Stigmata | 7 |
| Lures victims to prepared kill spot | | | | |

**Predator Type Notes**:
- Choose ONE at character creation
- Cannot change without major in-game event
- Humanity can shift based on feeding practices
- Flaws can be bought off with XP if feeding habits change

---

## Advantages & Flaws

### Merits

Merits are purchased with Advantage dots during character creation (7 total dots to spend). Some are specific to vampires.

#### General Merits

| Merit | Cost | Effect |
|-------|------|--------|
| **Beautiful** | 2 | +1 die to Social rolls involving appearance |
| **Stunning** | 4 | +2 dice to Social rolls involving appearance |
| **Linguistics** | Variable | Know additional languages (1 dot = 2 languages, 2 dots = 4, etc.) |
| **Resources** | 1-5 | Wealth and assets. Each dot represents comfortable lifestyle at that level |

#### Vampire-Specific Merits

| Merit | Cost | Effect | Restriction |
|-------|------|--------|-------------|
| **Bond Resistance** | 1 | +2 dice to resist Blood Bonds | Vampire only |
| **Short Bond** | 2 | Blood Bonds on you fade in half normal time | Vampire only |
| **Unbondable** | 4 | Immune to Blood Bonds | Vampire only |
| **Bloodhound** | 1 | +2 dice to track by scent, especially blood | Vampire only |
| **Iron Gullet** | 3 | Can feed from cold blood (corpses, blood bags) | Vampire only |
| **Eat Food** | 1 | Can consume and keep down mortal food | Vampire only |

#### Background Merits

| Background | Cost | Effect |
|------------|------|--------|
| **Allies** | 1-5 | Mortals/Kindred who will help you. Rating = power/number |
| **Contacts** | 1-5 | Information network. Rating = breadth and depth of contacts |
| **Fame** | 1-3 | Public recognition. +1 die per dot in Social with those who recognize |
| **Haven** | 1-5 | Quality and security of haven. Each dot adds features |
| **Herd** | 1-5 | Reliable feeding sources. Rating = number and quality of vessels |
| **Influence** | 1-5 | Sway over mortal institutions. Rating = scope of influence |
| **Mawla** | 1-5 | Powerful patron in Kindred society. Rating = patron's power |
| **Mask** | 1-2 | Fake identity with documentation. 2 dots = multiple masks |
| **Retainers** | 1-5 | Loyal servants (ghouls, mortals). Rating = number/competence |
| **Status** | 1-5 | Standing in Kindred society. Rating = position in hierarchy |

**Haven Features** (examples):
- Security System
- Watchmen/Guards
- Location (central/hidden)
- Size (luxury/cell)
- Laboratory
- Armory

### Flaws

Flaws are taken during character creation. Characters must take 2 points of flaws.

| Flaw | Value | Effect |
|------|-------|--------|
| **Illiterate** | 1 | Cannot read or write |
| **Repulsive** | 2 | -2 dice to Social rolls involving appearance |
| **Hopeless Addiction** | 2 | Severe addiction affecting function |
| **Folklore Block** | 1-2 | Specific folklore bane affects you (garlic, running water, etc.) |
| **Stigmata** | 2 | Blood weeps from hands/eyes when using disciplines |
| **Disliked** | 1 | -1 die to Social rolls with specific group |
| **Shunned** | 2 | Outcast from Kindred society |
| **Dark Secret** | 1-2 | Dangerous secret if revealed (Masquerade breach, diablerie, etc.) |
| **Enemy** | 1-3 | Someone wants you dead/ruined. Rating = enemy's power |
| **Suspect** | 1 | Authorities watch you closely |
| **Adversary** | 2 | Rival vampire or mortal organization opposes you |

#### Vampire-Specific Flaws

| Flaw | Value | Effect | Notes |
|------|-------|--------|-------|
| **Bondslave** | 2 | Bond at first drink (instead of 3) | Vampire only |
| **Bond Junkie** | 2 | Compulsively seek Blood Bonds | Vampire only |
| **Farmer** | 2 | Can only feed from animals | Vampire only (sets Predator Type) |
| **Organovore** | 1 | Only slake Hunger by eating human flesh | Vampire only, rare |
| **Prey Exclusion** | 1 | Cannot feed from specific type (gender, race, profession, etc.) | Vampire only |
| **Stake Bait** | 1 | Stakes through heart paralyze you (even non-wood) | Vampire only |

---

## Character Creation

### Character Creation Steps (V5 Standard)

**Step 1: Concept**
- Choose concept, ambition, desire
- Select Predator Type (determines Humanity start, some disciplines/skills)
- Choose Clan (determines in-clan disciplines, bane, compulsion)
- Select Generation (typically 13th for new characters)

**Step 2: Attributes (7/5/3 spread)**
- Prioritize Physical, Social, or Mental
- Primary category: 4 dots to distribute (all start at 1)
- Secondary: 3 dots to distribute
- Tertiary: 2 dots to distribute

**Example Priority**:
- Physical (Primary): Strength 3, Dexterity 4, Stamina 2
- Social (Secondary): Charisma 3, Manipulation 2, Composure 2
- Mental (Tertiary): Intelligence 2, Wits 2, Resolve 2

**Step 3: Skills (13/9/5 spread)**
- Prioritize Physical, Social, or Mental skills
- Primary: 13 dots
- Secondary: 9 dots
- Tertiary: 5 dots
- At 4+ dots in a skill, choose a specialty

**Step 4: Disciplines (2 dots in clan, 1 anywhere)**
- 2 dots in clan disciplines
- 1 dot in any discipline (including out-of-clan)
- Can split differently (e.g., 1/1/1 or 2/0/1)

**Step 5: Advantages (7 dots)**
- Distribute among Backgrounds, Merits, and Loresheets
- Must take 2 points of Flaws (don't count against Advantage dots)

**Step 6: Humanity & Touchstones**
- Starting Humanity determined by Predator Type (typically 7)
- Choose Convictions (1-3 moral principles)
- Choose Touchstone for each Conviction (mortal who embodies it)

**Step 7: Derived Statistics**
- Health = Stamina + 3
- Willpower = Composure + Resolve
- Blood Potency = 1 (for most new vampires)
- Hunger = 1 (start slightly hungry)

**Step 8: Details**
- Spend 15 freebie XP on anything
- Write backstory, sire, childer if any
- Determine True Age vs Apparent Age
- Select Resonance preference if any

### Typical Starting Character (Example)

**Concept**: Street-smart Brujah punk rocker
**Clan**: Brujah
**Predator**: Scene Queen
**Generation**: 13th
**Humanity**: 7

**Attributes**:
- Physical: Str 3, Dex 3, Sta 2
- Social: Cha 4, Man 2, Com 2
- Mental: Int 2, Wits 3, Res 2

**Skills**:
- Physical: Athletics 2, Brawl 3 (Grappling), Stealth 1
- Social: Etiquette 1, Intimidation 2, Performance 4 (Guitar), Persuasion 2, Streetwise 3
- Mental: Awareness 2, Occult 1, Politics 1

**Disciplines**: Celerity 1, Presence 2

**Advantages**: Fame 1 (local music scene), Contacts 2 (music industry), Resources 1, Haven 1

**Flaws**: Rival 1 (competing band's frontman vampire)

**Convictions**: "Art should speak truth to power", "Protect the scene from corporate sellouts"
**Touchstone**: Best friend from mortal days who still plays music

---

## Experience & Advancement

### XP Costs

| Trait | Cost |
|-------|------|
| **Attribute** | Current Rating × 5 XP |
| **Skill** | Current Rating × 3 XP |
| **Specialty** | 3 XP |
| **Clan Discipline** | Current Rating × 5 XP |
| **Out-of-Clan Discipline** | Current Rating × 7 XP |
| **Discipline Power** (Amalgam) | 5 XP or 7 XP (out-of-clan) |
| **Blood Sorcery Ritual** | Level × 3 XP |
| **Thin-Blood Alchemy Formula** | Level × 3 XP |
| **Merit** | 3 XP per dot |
| **Background** | 3 XP per dot |
| **Loresheet** | 3 XP per dot |
| **Remove Flaw** | 3 XP per dot |
| **Humanity** | Current Rating × 10 XP |
| **Willpower** | 8 XP (permanent increase, not just restoring) |

### XP Awards (Suggested)

| Session Type | XP Award |
|--------------|----------|
| **Standard Session** | 1-2 XP |
| **Exceptional Roleplay** | +1 XP |
| **Achieving Character Goal** | +1 XP |
| **Chronicle Milestone** | 2-5 XP |
| **Danger/Risk** | +1 XP |
| **Coterie Teamwork** | +1 XP |

**Typical XP Rate**: 2-3 XP per session (1 base + 1-2 bonuses)

### Blood Potency Advancement

Blood Potency typically advances through:
- **Age**: +1 per 100 years active
- **Diablerie**: Immediate increase
- **Torpor (Loss)**: -1 per 50 years in torpor
- **Storyteller Award**: Exceptional deeds, generation reduction

**Cannot exceed Generation maximum**:
- 13th Generation: Max Blood Potency 2
- 12th Generation: Max Blood Potency 3
- 11th Generation: Max Blood Potency 4
- 10th Generation: Max Blood Potency 5
- 9th and below: Higher maximums

---

## Quick Reference Tables

### Difficulty Guidelines

| Difficulty | Description | Examples |
|------------|-------------|----------|
| 1 | Trivial | Recalling common knowledge |
| 2 | Simple | Ordinary task under pressure |
| 3 | Standard | Professional-level task |
| 4 | Challenging | Expert-level task |
| 5 | Hard | Master-level task |
| 6+ | Extreme | Nearly impossible |

### Combat Summary

| Action | Dice Pool | Notes |
|--------|-----------|-------|
| **Melee Attack** | Str + Brawl/Melee | vs target's Defense |
| **Ranged Attack** | Dex + Firearms | -1 die per range increment |
| **Dodge** | Dex + Athletics | Active defense, lose action |
| **Defense** | Dex OR Wits (passive) | Always on |
| **Damage (unarmed)** | Str (Superficial) | +1 with Lethal Body |
| **Damage (weapon)** | Weapon rating + margin | Varies by weapon |
| **Soak** | Stamina (mortals) or Fortitude (if active) | Reduce Superficial only |

### Frenzy

**Frenzy Types**:
- **Fury Frenzy**: Triggered by anger, humiliation, hunger. Attack everything.
- **Terror Frenzy**: Triggered by fire, sunlight, True Faith. Flee in panic.

**Resisting Frenzy**:
- Roll Willpower vs Difficulty (usually 2-4)
- Can spend Willpower to reroll
- Humanity provides bonus dice to resist (+1 to +3 based on level)

**Riding the Wave**:
- Accept frenzy but maintain some control
- Make Resolve + Humanity roll
- On success, direct Beast's fury strategically

---

## Developer Notes

### Implementation Priorities

**Phase 1 - Core Systems**:
1. Hunger, Rouse checks, Blood Potency
2. Attributes, Skills, basic dice roller
3. Character creation flow
4. Disciplines (start with most common: Celerity, Potence, Fortitude, Auspex, Presence)

**Phase 2 - Roleplay Systems**:
1. Character sheet display
2. Predator Types
3. Clans with Banes/Compulsions
4. Humanity & Touchstones

**Phase 3 - Advanced**:
1. Remaining Disciplines
2. Blood Sorcery rituals
3. Frenzy system
4. Combat mechanics (manual, roleplay-focused)

**Phase 4 - Social/Political**:
1. Status system
2. Boons/Prestation
3. Coterie system (optional for MUSH)
4. Domain/Influence

### Data Validation

**Clan Restrictions**:
- Verify discipline purchases against clan
- Check generation limits on Blood Potency
- Validate predator type against character history

**Balance Checks**:
- Total starting XP = 0 (after creation)
- Advantages - Flaws = 5 (7 dots - 2 mandatory flaws)
- Attributes: 1 base + (7/5/3) = correct totals
- Skills: (13/9/5) dots distributed correctly

**Amalgam Requirements**:
- Check prerequisite disciplines before allowing amalgam powers
- Display clear error messages for missing requirements

---

## Appendix: Terminology

| Term | Definition |
|------|------------|
| **Amaranth** | Diablerie, the act of draining another vampire's soul |
| **Bane** | Clan-specific weakness or curse |
| **Beast, The** | Primal predatory nature within all vampires |
| **Blood Bond** | Supernatural addiction created by drinking vampire blood 3 times |
| **Blood Potency** | Power of vampiric vitae, related to age and generation |
| **Caine** | Mythical first vampire, progenitor of all Kindred |
| **Cainite** | Alternative term for vampire (archaic) |
| **Camarilla** | Dominant vampire sect focused on Masquerade |
| **Diablerie** | Consuming another vampire's soul for power (Amaranth) |
| **Elysium** | Neutral ground where violence is forbidden |
| **Embrace, The** | Act of turning a mortal into a vampire |
| **Final Death** | True death of a vampire (permanent destruction) |
| **Gehenna** | Prophesied apocalypse when Antediluvians rise |
| **Generation** | Distance from Caine (lower = more powerful) |
| **Ghoul** | Mortal who drinks vampire blood regularly, gains powers |
| **Haven** | Vampire's home/lair |
| **Hunger** | V5 mechanic replacing Blood Pool |
| **Kindred** | Vampire (formal term) |
| **Kine** | Mortals (cattle, archaic term) |
| **Lick** | Vampire (slang) |
| **Masquerade** | Hiding vampire existence from mortals |
| **Methuselah** | Ancient vampire (1000+ years old) |
| **Neonate** | Young vampire (0-50 years undead) |
| **Prince** | Camarilla leader of a city/domain |
| **Resonance** | Emotional quality of blood affecting disciplines |
| **Rouse Check** | V5 roll to avoid increasing Hunger |
| **Sect** | Vampire political faction (Camarilla, Anarchs, etc.) |
| **Sire** | Vampire who Embraced you |
| **Thin-Blood** | Weak vampire (14th-16th generation) |
| **Torpor** | Deathlike sleep vampires enter when severely injured |
| **Touchstone** | Mortal connection that helps maintain Humanity |
| **Vitae** | Vampire blood |
| **Wight** | Vampire at Humanity 0, mindless beast |

---

## References & Sources

- **Vampire: The Masquerade 5th Edition Core Rulebook** (Renegade Game Studios, 2018)
- **V5 Companion** (2020)
- **Players Guide** (2024)
- **VTM Wiki**: https://vtm.paradoxwikis.com/
- **White Wolf Wiki**: https://whitewolf.fandom.com/
- **Reference Repository**: BeckoningMU-master/world/data.py

---

**Document Version**: 1.0
**Created**: 2025-01-19
**For**: TheBeckoningMU Development Team
