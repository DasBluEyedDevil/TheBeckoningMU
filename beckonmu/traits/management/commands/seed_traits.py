"""
Django management command to seed VtM 5e trait data.

Populates the database with:
- Trait categories (Attributes, Skills, Disciplines, etc.)
- All V5 attributes (9 total)
- All V5 skills (27 total)
- All V5 disciplines (12 total)
- Sample discipline powers (foundation for expansion)

Usage:
    evennia seed_traits [--clear]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from beckonmu.traits.models import TraitCategory, Trait, DisciplinePower


class Command(BaseCommand):
    """Seed VtM 5e trait definitions from V5_MECHANICS.md reference."""

    help = "Seed comprehensive V5 trait data (Attributes, Skills, Disciplines, Powers)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing trait data before seeding',
        )

    def handle(self, *args, **options):
        """Execute the command."""

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing trait data...'))
            DisciplinePower.objects.all().delete()
            Trait.objects.all().delete()
            TraitCategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all existing trait data'))

        with transaction.atomic():
            # Create trait categories
            categories = self._create_categories()
            self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} trait categories'))

            # Create attributes
            attr_count = self._create_attributes(categories['attributes'])
            self.stdout.write(self.style.SUCCESS(f'Created {attr_count} attributes'))

            # Create skills
            skill_count = self._create_skills(categories['skills'])
            self.stdout.write(self.style.SUCCESS(f'Created {skill_count} skills'))

            # Create disciplines
            disc_count = self._create_disciplines(categories['disciplines'])
            self.stdout.write(self.style.SUCCESS(f'Created {disc_count} disciplines'))

            # Create discipline powers (sample set)
            power_count = self._create_discipline_powers()
            self.stdout.write(self.style.SUCCESS(f'Created {power_count} discipline powers'))

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Trait seeding complete!'))

    def _create_categories(self):
        """Create trait categories."""
        categories_data = [
            {'name': 'Attributes', 'code': 'attributes', 'sort_order': 1,
             'description': 'Innate capabilities - Physical, Social, Mental'},
            {'name': 'Skills', 'code': 'skills', 'sort_order': 2,
             'description': 'Trained abilities and learned knowledge'},
            {'name': 'Disciplines', 'code': 'disciplines', 'sort_order': 3,
             'description': 'Supernatural powers fueled by vampiric blood'},
            {'name': 'Advantages', 'code': 'advantages', 'sort_order': 4,
             'description': 'Merits, backgrounds, and other benefits'},
            {'name': 'Flaws', 'code': 'flaws', 'sort_order': 5,
             'description': 'Disadvantages and complications'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, _ = TraitCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )
            categories[cat_data['code']] = cat

        return categories

    def _create_attributes(self, category):
        """Create all V5 attributes."""
        attributes_data = [
            # Physical Attributes
            {'name': 'Strength', 'sort_order': 1,
             'description': 'Physical power, muscle, brute force'},
            {'name': 'Dexterity', 'sort_order': 2,
             'description': 'Agility, grace, reflexes, fine motor control'},
            {'name': 'Stamina', 'sort_order': 3,
             'description': 'Endurance, resilience, toughness, constitution'},

            # Social Attributes
            {'name': 'Charisma', 'sort_order': 4,
             'description': 'Charm, magnetism, ability to inspire'},
            {'name': 'Manipulation', 'sort_order': 5,
             'description': 'Ability to deceive, influence, control'},
            {'name': 'Composure', 'sort_order': 6,
             'description': 'Self-control, grace under pressure, emotional regulation'},

            # Mental Attributes
            {'name': 'Intelligence', 'sort_order': 7,
             'description': 'Reasoning, memory, analytical capability'},
            {'name': 'Wits', 'sort_order': 8,
             'description': 'Cunning, quick thinking, situational awareness'},
            {'name': 'Resolve', 'sort_order': 9,
             'description': 'Determination, focus, mental fortitude'},
        ]

        count = 0
        for attr_data in attributes_data:
            _, created = Trait.objects.get_or_create(
                name=attr_data['name'],
                category=category,
                defaults={
                    'description': attr_data['description'],
                    'sort_order': attr_data['sort_order'],
                    'min_value': 1,  # All vampires have at least 1 in each attribute
                    'max_value': 5,
                    'has_specialties': False,
                    'is_instanced': False,
                }
            )
            if created:
                count += 1

        return count

    def _create_skills(self, category):
        """Create all V5 skills."""
        skills_data = [
            # Physical Skills (1-9)
            {'name': 'Athletics', 'sort_order': 1,
             'description': 'Running, jumping, climbing, swimming, parkour'},
            {'name': 'Brawl', 'sort_order': 2,
             'description': 'Unarmed combat, grappling, martial arts'},
            {'name': 'Craft', 'sort_order': 3,
             'description': 'Creating and repairing physical objects'},
            {'name': 'Drive', 'sort_order': 4,
             'description': 'Operating vehicles'},
            {'name': 'Firearms', 'sort_order': 5,
             'description': 'Shooting guns of all types'},
            {'name': 'Larceny', 'sort_order': 6,
             'description': 'Lock picking, pickpocketing, security'},
            {'name': 'Melee', 'sort_order': 7,
             'description': 'Armed combat with melee weapons'},
            {'name': 'Stealth', 'sort_order': 8,
             'description': 'Moving unseen and unheard'},
            {'name': 'Survival', 'sort_order': 9,
             'description': 'Wilderness skills, tracking, foraging'},

            # Social Skills (10-18)
            {'name': 'Animal Ken', 'sort_order': 10,
             'description': 'Understanding and influencing animals'},
            {'name': 'Etiquette', 'sort_order': 11,
             'description': 'Social graces, protocol, proper behavior'},
            {'name': 'Insight', 'sort_order': 12,
             'description': 'Reading people, detecting lies, empathy'},
            {'name': 'Intimidation', 'sort_order': 13,
             'description': 'Coercion through fear or threat'},
            {'name': 'Leadership', 'sort_order': 14,
             'description': 'Inspiring and directing others'},
            {'name': 'Performance', 'sort_order': 15,
             'description': 'Artistic expression, entertainment'},
            {'name': 'Persuasion', 'sort_order': 16,
             'description': 'Convincing others through reason or charm'},
            {'name': 'Streetwise', 'sort_order': 17,
             'description': 'Urban survival, criminal knowledge'},
            {'name': 'Subterfuge', 'sort_order': 18,
             'description': 'Lying, disguise, misdirection'},

            # Mental Skills (19-27)
            {'name': 'Academics', 'sort_order': 19,
             'description': 'Scholarly knowledge, research, humanities'},
            {'name': 'Awareness', 'sort_order': 20,
             'description': 'Noticing details, perception, alertness'},
            {'name': 'Finance', 'sort_order': 21,
             'description': 'Money management, economics, business'},
            {'name': 'Investigation', 'sort_order': 22,
             'description': 'Solving mysteries, gathering evidence'},
            {'name': 'Medicine', 'sort_order': 23,
             'description': 'Medical knowledge, first aid, anatomy'},
            {'name': 'Occult', 'sort_order': 24,
             'description': 'Supernatural lore, mysticism, rituals'},
            {'name': 'Politics', 'sort_order': 25,
             'description': 'Government, power structures, diplomacy'},
            {'name': 'Science', 'sort_order': 26,
             'description': 'Natural sciences, chemistry, biology'},
            {'name': 'Technology', 'sort_order': 27,
             'description': 'Computers, electronics, modern tech'},
        ]

        count = 0
        for skill_data in skills_data:
            _, created = Trait.objects.get_or_create(
                name=skill_data['name'],
                category=category,
                defaults={
                    'description': skill_data['description'],
                    'sort_order': skill_data['sort_order'],
                    'min_value': 0,  # Skills can be untrained
                    'max_value': 5,
                    'has_specialties': True,  # All skills can have specialties
                    'is_instanced': False,
                }
            )
            if created:
                count += 1

        return count

    def _create_disciplines(self, category):
        """Create all V5 disciplines."""
        disciplines_data = [
            {'name': 'Animalism', 'sort_order': 1,
             'description': 'Command over beasts and bestial nature'},
            {'name': 'Auspex', 'sort_order': 2,
             'description': 'Supernatural senses and perception'},
            {'name': 'Blood Sorcery', 'sort_order': 3,
             'description': 'Rituals and blood magic'},
            {'name': 'Celerity', 'sort_order': 4,
             'description': 'Supernatural speed'},
            {'name': 'Dominate', 'sort_order': 5,
             'description': 'Mind control and mental manipulation'},
            {'name': 'Fortitude', 'sort_order': 6,
             'description': 'Supernatural resilience and endurance'},
            {'name': 'Obfuscate', 'sort_order': 7,
             'description': 'Supernatural stealth, illusion, and invisibility'},
            {'name': 'Oblivion', 'sort_order': 8,
             'description': 'Death, shadows, necromancy'},
            {'name': 'Potence', 'sort_order': 9,
             'description': 'Supernatural strength'},
            {'name': 'Presence', 'sort_order': 10,
             'description': 'Supernatural charisma and emotional manipulation'},
            {'name': 'Protean', 'sort_order': 11,
             'description': 'Shapeshifting and bestial transformation'},
            {'name': 'Thin-Blood Alchemy', 'sort_order': 12,
             'description': 'Limited supernatural chemistry (Thin-Bloods only)',
             'splat_restriction': 'thin-blood'},
        ]

        count = 0
        for disc_data in disciplines_data:
            defaults = {
                'description': disc_data['description'],
                'sort_order': disc_data['sort_order'],
                'min_value': 0,
                'max_value': 5,
                'has_specialties': False,
                'is_instanced': False,
                'splat_restriction': disc_data.get('splat_restriction'),
            }
            _, created = Trait.objects.get_or_create(
                name=disc_data['name'],
                category=category,
                defaults=defaults
            )
            if created:
                count += 1

        return count

    def _create_discipline_powers(self):
        """Create all V5 discipline powers (complete implementation)."""
        disciplines = {d.name: d for d in Trait.objects.filter(category__code='disciplines')}

        # Complete V5 discipline powers from V5_MECHANICS.md
        powers_data = [
            # ==================== ANIMALISM ====================
            {'name': 'Bond Famulus', 'discipline': 'Animalism', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma + Animal Ken',
             'description': 'Create supernatural bond with one animal, enabling mental communication'},
            {'name': 'Sense the Beast', 'discipline': 'Animalism', 'level': 1,
             'cost': 'Free', 'dice_pool': 'Resolve + Animalism',
             'description': 'Sense presence and emotional state of animals and vampires nearby'},

            {'name': 'Feral Whispers', 'discipline': 'Animalism', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation/Charisma + Animalism',
             'description': 'Communicate with and command animals'},

            {'name': 'Animal Succulence', 'discipline': 'Animalism', 'level': 3,
             'cost': 'Free', 'dice_pool': None,
             'description': 'Slake 1 additional Hunger when feeding from animals'},
            {'name': 'Quell the Beast', 'discipline': 'Animalism', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma/Manipulation + Animalism',
             'description': 'Calm or rouse the Beast in others'},
            {'name': 'Living Hive', 'discipline': 'Animalism', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Composure + Animalism',
             'description': 'Infest body with stinging insects for defense and concealment',
             'amalgam_discipline': 'Obfuscate', 'amalgam_level': 2},

            {'name': 'Subsume the Spirit', 'discipline': 'Animalism', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Animalism',
             'description': 'Project consciousness into animal, control it fully'},

            {'name': 'Animal Dominion', 'discipline': 'Animalism', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma + Animalism',
             'description': 'Command multiple animals or swarms simultaneously'},
            {'name': 'Draw Out the Beast', 'discipline': 'Animalism', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma + Animalism',
             'description': 'Force another\'s Beast into frenzy or calm it entirely'},

            # ==================== AUSPEX ====================
            {'name': 'Heightened Senses', 'discipline': 'Auspex', 'level': 1,
             'cost': 'Free', 'dice_pool': 'Wits/Resolve + Auspex',
             'description': 'Dramatically enhance all five senses'},
            {'name': 'Sense the Unseen', 'discipline': 'Auspex', 'level': 1,
             'cost': 'Free', 'dice_pool': 'Wits/Resolve + Auspex',
             'description': 'Detect supernatural presences (Obfuscate, ghosts, magic)'},

            {'name': 'Premonition', 'discipline': 'Auspex', 'level': 2,
             'cost': 'Free', 'dice_pool': 'Resolve + Auspex',
             'description': 'Get glimpses of danger or future events'},

            {'name': 'Scry the Soul', 'discipline': 'Auspex', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Intelligence + Auspex',
             'description': 'Read aura, discern emotional state, vampiric nature, resonance'},
            {'name': 'Share the Senses', 'discipline': 'Auspex', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Resolve + Auspex',
             'description': 'See/hear through another\'s senses remotely'},

            {'name': 'Spirit\'s Touch', 'discipline': 'Auspex', 'level': 4,
             'cost': 'Free', 'dice_pool': 'Intelligence + Auspex',
             'description': 'Read psychic impressions from objects (psychometry)'},

            {'name': 'Clairvoyance', 'discipline': 'Auspex', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Intelligence + Auspex',
             'description': 'Project senses to a distant familiar location'},
            {'name': 'Possession', 'discipline': 'Auspex', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Resolve + Auspex',
             'description': 'Fully possess another person\'s body',
             'amalgam_discipline': 'Dominate', 'amalgam_level': 3},
            {'name': 'Telepathy', 'discipline': 'Auspex', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Resolve + Auspex',
             'description': 'Read surface thoughts, project thoughts, mental communication'},

            # ==================== BLOOD SORCERY ====================
            {'name': 'Corrosive Vitae', 'discipline': 'Blood Sorcery', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': 'Strength + Blood Sorcery',
             'description': 'Spit vitae as acid weapon'},
            {'name': 'Blood of Potency', 'discipline': 'Blood Sorcery', 'level': 1,
             'cost': 'Ritual', 'dice_pool': 'Intelligence + Blood Sorcery',
             'description': 'Ritual: Temporarily raise Blood Potency'},

            {'name': 'Extinguish Vitae', 'discipline': 'Blood Sorcery', 'level': 2,
             'cost': 'Ritual', 'dice_pool': 'Intelligence + Blood Sorcery',
             'description': 'Ritual: Paralyze a vampire\'s limb'},
            {'name': 'Ward Against Ghouls', 'discipline': 'Blood Sorcery', 'level': 2,
             'cost': 'Ritual', 'dice_pool': 'Intelligence + Blood Sorcery',
             'description': 'Ritual: Create protective ward against ghouls'},

            {'name': 'Scorpion\'s Touch', 'discipline': 'Blood Sorcery', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Strength + Blood Sorcery',
             'description': 'Vitae becomes paralyzing poison in melee'},
            {'name': 'Incorporeal Passage', 'discipline': 'Blood Sorcery', 'level': 3,
             'cost': 'Ritual', 'dice_pool': 'Intelligence + Blood Sorcery',
             'description': 'Ritual: Walk through walls'},

            {'name': 'Theft of Vitae', 'discipline': 'Blood Sorcery', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': 'Wits + Blood Sorcery',
             'description': 'Drain vitae from target at a distance'},

            {'name': 'Cauldron of Blood', 'discipline': 'Blood Sorcery', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Blood Sorcery',
             'description': 'Boil victim\'s blood, causing massive damage'},

            # ==================== CELERITY ====================
            {'name': 'Cat\'s Grace', 'discipline': 'Celerity', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Gain automatic success on Dexterity + Athletics roll. Passive: Add Celerity rating to Defense'},
            {'name': 'Rapid Reflexes', 'discipline': 'Celerity', 'level': 1,
             'cost': 'Free', 'dice_pool': None,
             'description': 'Add Celerity rating to initiative'},

            {'name': 'Fleetness', 'discipline': 'Celerity', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Double movement speed for scene'},

            {'name': 'Blink', 'discipline': 'Celerity', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Move short distance instantly (appears to teleport)'},
            {'name': 'Traversal', 'discipline': 'Celerity', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Scale walls, run across water, perform impossible movements'},

            {'name': 'Draught of Elegance', 'discipline': 'Celerity', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Gain Celerity rating as bonus dice to Dexterity rolls for scene'},
            {'name': 'Unerring Aim', 'discipline': 'Celerity', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Automatically hit target with ranged attack',
             'amalgam_discipline': 'Auspex', 'amalgam_level': 2},

            {'name': 'Lightning Strike', 'discipline': 'Celerity', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Make multiple attacks in single turn'},
            {'name': 'Split Second', 'discipline': 'Celerity', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Wits + Awareness',
             'description': 'Act first in turn order, interrupt actions'},

            # ==================== DOMINATE ====================
            {'name': 'Cloud Memory', 'discipline': 'Dominate', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma + Dominate',
             'description': 'Remove or alter short-term memories'},
            {'name': 'Compel', 'discipline': 'Dominate', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma/Manipulation + Dominate',
             'description': 'Issue one-word command target must obey'},

            {'name': 'Mesmerize', 'discipline': 'Dominate', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma/Manipulation + Dominate',
             'description': 'Issue complex hypnotic commands'},
            {'name': 'Dementation', 'discipline': 'Dominate', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Dominate',
             'description': 'Drive target temporarily insane with hallucinations',
             'amalgam_discipline': 'Obfuscate', 'amalgam_level': 2},
            {'name': 'Submerged Directive', 'discipline': 'Dominate', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Dominate',
             'description': 'Plant delayed trigger command'},

            {'name': 'The Forgetful Mind', 'discipline': 'Dominate', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Dominate',
             'description': 'Rewrite or remove extensive memories'},

            {'name': 'Rationalize', 'discipline': 'Dominate', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Dominate',
             'description': 'Make victim justify/accept anything'},

            {'name': 'Mass Manipulation', 'discipline': 'Dominate', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma + Dominate',
             'description': 'Dominate multiple targets simultaneously'},
            {'name': 'Terminal Decree', 'discipline': 'Dominate', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Dominate',
             'description': 'Implant suicidal or self-destructive command'},

            # ==================== FORTITUDE ====================
            {'name': 'Resilience', 'discipline': 'Fortitude', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Add Fortitude rating to Health for scene'},
            {'name': 'Unswayable Mind', 'discipline': 'Fortitude', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Add Fortitude rating to Resolve or Composure for resisting mental attacks'},

            {'name': 'Toughness', 'discipline': 'Fortitude', 'level': 2,
             'cost': 'Passive', 'dice_pool': None,
             'description': 'Reduce Aggravated damage from fire/sunlight by 1 per Bane Severity'},
            {'name': 'Enduring Beast', 'discipline': 'Fortitude', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': 'Stamina + Survival',
             'description': 'Ignore physical damage penalties for scene'},

            {'name': 'Fortify the Inner Facade', 'discipline': 'Fortitude', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Stamina + Fortitude',
             'description': 'Superficial damage becomes bashing for mortals witnessing violence'},

            {'name': 'Draught of Endurance', 'discipline': 'Fortitude', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Add Fortitude rating as bonus dice to Stamina rolls for scene'},

            {'name': 'Flesh of Marble', 'discipline': 'Fortitude', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Composure + Fortitude',
             'description': 'Become nearly invulnerable to physical harm'},
            {'name': 'Prowess from Pain', 'discipline': 'Fortitude', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Convert Health damage into bonus dice'},

            # ==================== OBFUSCATE ====================
            {'name': 'Cloak of Shadows', 'discipline': 'Obfuscate', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': 'Wits + Obfuscate',
             'description': 'Become invisible while stationary'},
            {'name': 'Silence of Death', 'discipline': 'Obfuscate', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Suppress all sound you make'},

            {'name': 'Unseen Passage', 'discipline': 'Obfuscate', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': 'Wits + Obfuscate',
             'description': 'Remain invisible while moving'},

            {'name': 'Ghost in the Machine', 'discipline': 'Obfuscate', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Obfuscate',
             'description': 'Erase digital presence, disappear from cameras'},
            {'name': 'Mask of a Thousand Faces', 'discipline': 'Obfuscate', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Obfuscate',
             'description': 'Appear as a different person'},

            {'name': 'Conceal', 'discipline': 'Obfuscate', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': 'Wits + Obfuscate',
             'description': 'Hide objects or other people'},

            {'name': 'Vanish', 'discipline': 'Obfuscate', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Disappear instantly, even while observed'},
            {'name': 'Imposter\'s Guise', 'discipline': 'Obfuscate', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Obfuscate',
             'description': 'Perfectly mimic specific person (voice, mannerisms, etc.)'},

            # ==================== OBLIVION ====================
            # Shadow Path
            {'name': 'Shadow Cloak', 'discipline': 'Oblivion', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Obfuscate 1 equivalent using shadows'},
            {'name': 'Oblivion\'s Sight', 'discipline': 'Oblivion', 'level': 1,
             'cost': 'Free', 'dice_pool': 'Resolve + Oblivion',
             'description': 'See into lands of the dead'},

            {'name': 'Tenebrous Avatar', 'discipline': 'Oblivion', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Become shadow-form'},

            {'name': 'Shadow Cast', 'discipline': 'Oblivion', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Oblivion',
             'description': 'Control shadows to attack or manipulate'},

            {'name': 'Shadow Perspective', 'discipline': 'Oblivion', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': 'Intelligence + Oblivion',
             'description': 'Scry through shadows'},

            {'name': 'Shadowstep', 'discipline': 'Oblivion', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Teleport through shadows'},

            # Necromancy Path
            {'name': 'Binding the Fetters', 'discipline': 'Oblivion', 'level': 1,
             'cost': 'Ritual', 'dice_pool': 'Intelligence + Oblivion',
             'description': 'Ritual: Strengthen ghost anchors'},

            {'name': 'Where the Shroud Thins', 'discipline': 'Oblivion', 'level': 2,
             'cost': 'Ritual', 'dice_pool': 'Intelligence + Oblivion',
             'description': 'Ritual: Find weak points in death barrier'},

            {'name': 'Summon Spirit', 'discipline': 'Oblivion', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Intelligence + Oblivion',
             'description': 'Call ghost to appear'},

            {'name': 'Compel Spirit', 'discipline': 'Oblivion', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Oblivion',
             'description': 'Force ghost to obey'},

            {'name': 'Shambling Hordes', 'discipline': 'Oblivion', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Intelligence + Oblivion',
             'description': 'Animate corpses'},

            # ==================== POTENCE ====================
            {'name': 'Lethal Body', 'discipline': 'Potence', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Unarmed attacks deal +1 damage, can be Aggravated'},
            {'name': 'Soaring Leap', 'discipline': 'Potence', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Jump incredible distances'},

            {'name': 'Prowess', 'discipline': 'Potence', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Add Potence rating as bonus dice to Strength rolls for scene'},

            {'name': 'Brutal Feed', 'discipline': 'Potence', 'level': 3,
             'cost': 'Passive', 'dice_pool': None,
             'description': 'Gain additional Resonance benefit when feeding violently'},

            {'name': 'Spark of Rage', 'discipline': 'Potence', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Cause frenzy in nearby vampires',
             'amalgam_discipline': 'Presence', 'amalgam_level': 3},

            {'name': 'Earthshock', 'discipline': 'Potence', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Strength + Potence',
             'description': 'Shockwave knocks down all nearby'},
            {'name': 'Fist of Caine', 'discipline': 'Potence', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'One devastating attack causing massive damage'},

            # ==================== PRESENCE ====================
            {'name': 'Awe', 'discipline': 'Presence', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma/Manipulation + Presence',
             'description': 'Become magnetic center of attention'},
            {'name': 'Daunt', 'discipline': 'Presence', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma/Manipulation + Presence',
             'description': 'Inspire terror in onlookers'},

            {'name': 'Lingering Kiss', 'discipline': 'Presence', 'level': 2,
             'cost': 'Passive', 'dice_pool': None,
             'description': 'Your Kiss causes euphoria, not pain'},

            {'name': 'Dread Gaze', 'discipline': 'Presence', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma/Manipulation + Presence',
             'description': 'Paralyze target with terror'},
            {'name': 'Entrancement', 'discipline': 'Presence', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma/Manipulation + Presence',
             'description': 'Create obsessive fascination/love in target'},

            {'name': 'Irresistible Voice', 'discipline': 'Presence', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Presence',
             'description': 'Commands carry supernatural compulsion'},
            {'name': 'Summon', 'discipline': 'Presence', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': 'Manipulation + Presence',
             'description': 'Call target to your location (they must come)'},

            {'name': 'Majesty', 'discipline': 'Presence', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma + Presence',
             'description': 'Radiate such magnificence others cannot act against you'},
            {'name': 'Star Magnetism', 'discipline': 'Presence', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': 'Charisma + Presence',
             'description': 'Affect large crowds with Presence powers'},

            # ==================== PROTEAN ====================
            {'name': 'Eyes of the Beast', 'discipline': 'Protean', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'See perfectly in darkness, eyes glow red'},
            {'name': 'Weight of the Feather', 'discipline': 'Protean', 'level': 1,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Reduce falling damage, land gracefully'},

            {'name': 'Feral Weapons', 'discipline': 'Protean', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Grow claws dealing Aggravated damage'},
            {'name': 'Metamorphosis', 'discipline': 'Protean', 'level': 2,
             'cost': 'One Rouse Check', 'dice_pool': 'Stamina + Protean',
             'description': 'Transform into animal form (bat, wolf, rat)'},

            {'name': 'Shapechange', 'discipline': 'Protean', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Transform into mist form'},
            {'name': 'Earth Meld', 'discipline': 'Protean', 'level': 3,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Merge with earth/stone for day sleep'},

            {'name': 'One with the Beast', 'discipline': 'Protean', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Remain conscious while in frenzy'},
            {'name': 'Fleshcraft', 'discipline': 'Protean', 'level': 4,
             'cost': 'One Rouse Check', 'dice_pool': 'Dexterity + Protean',
             'description': 'Sculpt flesh (self or others)'},

            {'name': 'Horrid Form', 'discipline': 'Protean', 'level': 5,
             'cost': 'One Rouse Check', 'dice_pool': None,
             'description': 'Transform into massive combat monster'},
            {'name': 'The Unfettered Heart', 'discipline': 'Protean', 'level': 5,
             'cost': 'Ritual', 'dice_pool': 'Intelligence + Protean',
             'description': 'Ritual: Remove heart from body, hide it elsewhere'},

            # ==================== THIN-BLOOD ALCHEMY ====================
            {'name': 'Far Reach', 'discipline': 'Thin-Blood Alchemy', 'level': 1,
             'cost': 'One Rouse', 'dice_pool': None,
             'description': 'Telekinesis on light objects'},
            {'name': 'Haze', 'discipline': 'Thin-Blood Alchemy', 'level': 1,
             'cost': 'One Rouse', 'dice_pool': None,
             'description': 'Obfuscate-like concealment'},

            {'name': 'Envelop', 'discipline': 'Thin-Blood Alchemy', 'level': 2,
             'cost': 'One Rouse', 'dice_pool': None,
             'description': 'Fortitude-like durability'},
            {'name': 'Counterfeit', 'discipline': 'Thin-Blood Alchemy', 'level': 2,
             'cost': 'One Rouse', 'dice_pool': None,
             'description': 'Temporary discipline mimicry'},

            {'name': 'Defraktionierung', 'discipline': 'Thin-Blood Alchemy', 'level': 3,
             'cost': 'Two Rouses', 'dice_pool': None,
             'description': 'Distill disciplines from elder vitae'},
            {'name': 'Awaken the Sleeper', 'discipline': 'Thin-Blood Alchemy', 'level': 3,
             'cost': 'One Rouse', 'dice_pool': None,
             'description': 'Temporarily raise Blood Potency'},
        ]

        count = 0
        for power_data in powers_data:
            discipline = disciplines.get(power_data['discipline'])
            if not discipline:
                continue

            # Handle amalgam disciplines
            amalgam_disc = None
            if power_data.get('amalgam_discipline'):
                amalgam_disc = disciplines.get(power_data['amalgam_discipline'])

            defaults = {
                'level': power_data['level'],
                'description': power_data['description'],
                'cost': power_data.get('cost') or '',
                'dice_pool': power_data.get('dice_pool') or '',
            }

            # Add amalgam fields if present
            if amalgam_disc:
                defaults['amalgam_discipline'] = amalgam_disc
                defaults['amalgam_level'] = power_data.get('amalgam_level')

            _, created = DisciplinePower.objects.get_or_create(
                name=power_data['name'],
                discipline=discipline,
                defaults=defaults
            )
            if created:
                count += 1

        return count
