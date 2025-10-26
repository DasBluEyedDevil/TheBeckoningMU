"""V5 Character Sheet Commands"""
from evennia.commands.command import Command
from traits.utils import get_character_trait_value

class CmdSheet(Command):
    """
    Display your character sheet.
    
    Usage:
        +sheet
        sheet
    
    Shows your character's attributes, skills, disciplines, and other stats.
    """
    
    key = "+sheet"
    aliases = ["sheet"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        char = self.caller
        
        # Header
        output = "\n"
        output += "|w" + "=" * 78 + "|n\n"
        output += f"|w{char.key}'s Character Sheet|n\n"
        output += "|w" + "=" * 78 + "|n\n\n"
        
        # Vampire vitals (if vampire)
        if hasattr(char.db, 'vampire') and isinstance(char.db.vampire, dict):
            vamp = char.db.vampire
            output += "|rVampire Status:|n\n"
            output += f"  Clan: {vamp.get('clan', 'Unknown')}\n"
            output += f"  Generation: {vamp.get('generation', 13)}\n"
            output += f"  Blood Potency: {vamp.get('blood_potency', 0)}\n"
            output += f"  Hunger: |r{'●' * vamp.get('hunger', 0)}|n{'○' * (5 - vamp.get('hunger', 0))}\n"
            output += f"  Humanity: {vamp.get('humanity', 7)}\n\n"
        
        # Attributes
        output += "|wAttributes:|n\n"
        attrs = {
            'Physical': ['strength', 'dexterity', 'stamina'],
            'Social': ['charisma', 'manipulation', 'composure'],
            'Mental': ['intelligence', 'wits', 'resolve']
        }
        
        for cat, trait_list in attrs.items():
            output += f"  |c{cat}:|n\n"
            for trait in trait_list:
                val = get_character_trait_value(char, trait) or 0
                dots = '●' * val + '○' * (5 - val)
                output += f"    {trait.capitalize():<15} {dots} ({val})\n"
        
        output += "\n"
        
        # Skills
        output += "|wSkills:|n\n"
        skills = {
            'Physical': ['athletics', 'brawl', 'craft', 'drive', 'firearms', 
                        'melee', 'larceny', 'stealth', 'survival'],
            'Social': ['animal_ken', 'etiquette', 'insight', 'intimidation',
                      'leadership', 'performance', 'persuasion', 'streetwise', 'subterfuge'],
            'Mental': ['academics', 'awareness', 'finance', 'investigation',
                      'medicine', 'occult', 'politics', 'science', 'technology']
        }
        
        for cat, skill_list in skills.items():
            output += f"  |c{cat}:|n\n"
            for skill in skill_list:
                val = get_character_trait_value(char, skill) or 0
                if val > 0:  # Only show skills with dots
                    dots = '●' * val + '○' * (5 - val)
                    display_name = skill.replace('_', ' ').title()
                    output += f"    {display_name:<15} {dots} ({val})\n"
        
        output += "\n"
        
        # Disciplines
        output += "|wDisciplines:|n\n"
        disciplines = ['animalism', 'auspex', 'celerity', 'dominate', 'fortitude',
                      'obfuscate', 'potence', 'presence', 'protean', 'blood_sorcery', 
                      'oblivion', 'thin_blood_alchemy']
        
        has_disciplines = False
        for disc in disciplines:
            val = get_character_trait_value(char, disc) or 0
            if val > 0:
                has_disciplines = True
                dots = '●' * val + '○' * (5 - val)
                display_name = disc.replace('_', ' ').title()
                output += f"  {display_name:<20} {dots} ({val})\n"
        
        if not has_disciplines:
            output += "  |xNone|n\n"
        
        output += "\n"
        
        # Footer
        output += "|w" + "=" * 78 + "|n\n"
        
        self.caller.msg(output)


class CmdSheetShort(Command):
    """
    Display abbreviated character stats.
    
    Usage:
        +st
        st
    
    Shows vital statistics in a compact format.
    """
    
    key = "+st"
    aliases = ["st"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        char = self.caller
        
        output = f"\n|w{char.key}|n "
        
        # Vampire info
        if hasattr(char.db, 'vampire') and isinstance(char.db.vampire, dict):
            vamp = char.db.vampire
            clan = vamp.get('clan', 'Unknown')
            gen = vamp.get('generation', 13)
            hunger = vamp.get('hunger', 0)
            output += f"({clan} Gen {gen}) "
            output += f"Hunger: |r{'●' * hunger}|n{'○' * (5 - hunger)} "
        
        # Health/Willpower (if implemented)
        if hasattr(char.db, 'pools') and isinstance(char.db.pools, dict):
            pools = char.db.pools
            health = pools.get('current_health', pools.get('health', 0))
            willpower = pools.get('current_willpower', pools.get('willpower', 0))
            output += f"Health: {health} Willpower: {willpower}"
        
        output += "\n"
        self.caller.msg(output)
