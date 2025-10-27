"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    def at_object_creation(self):
        """Called when character is first created."""
        super().at_object_creation()

        # Initialize vampire data structure (Phase 6)
        if not self.db.vampire:
            self.db.vampire = {
                "clan": None,  # Set during chargen
                "generation": 13,  # Default for neonates
                "blood_potency": 0,  # 0-10 scale
                "hunger": 1,  # 0-5, starts at 1
                "humanity": 7,  # 0-10, default 7
                "predator_type": None,  # Set during chargen
                "current_resonance": None,  # Choleric, Melancholic, Phlegmatic, Sanguine
                "resonance_intensity": 0,  # 0=none, 1=fleeting, 2=intense, 3=dyscrasia
                "bane": None,  # Clan bane description
                "compulsion": None,  # Current compulsion
            }

        # Legacy hunger tracking (Phase 5 compatibility)
        if not hasattr(self.db, 'hunger'):
            self.db.hunger = 1

    def migrate_vampire_data(self):
        """Migrate old character data to new vampire structure.

        Called to upgrade existing characters to Phase 6 structure.
        """
        # Initialize vampire dict if missing
        if not self.db.vampire:
            self.db.vampire = {
                "clan": None,
                "generation": 13,
                "blood_potency": 0,
                "hunger": getattr(self.db, 'hunger', 1),  # Migrate from old location
                "humanity": 7,
                "predator_type": None,
                "current_resonance": None,
                "resonance_intensity": 0,
                "bane": None,
                "compulsion": None,
            }

        # Sync old hunger location with new
        if hasattr(self.db, 'hunger'):
            self.db.vampire['hunger'] = self.db.hunger

    @property
    def hunger(self):
        """Property for easy hunger access.

        Prioritizes vampire dict but falls back to legacy location if vampire dict
        is missing. Syncs values if they differ.
        """
        if self.db.vampire:
            # Check if legacy hunger exists and differs from vampire dict
            legacy_hunger = getattr(self.db, 'hunger', None)
            vampire_hunger = self.db.vampire.get('hunger', 1)

            # If legacy hunger is set and differs, sync to vampire dict
            if legacy_hunger is not None and legacy_hunger != vampire_hunger:
                self.db.vampire['hunger'] = legacy_hunger
                return legacy_hunger

            return vampire_hunger
        return getattr(self.db, 'hunger', 1)

    @hunger.setter
    def hunger(self, value):
        """Set hunger level."""
        value = max(0, min(5, value))  # Clamp 0-5
        if self.db.vampire:
            self.db.vampire['hunger'] = value
        self.db.hunger = value  # Keep legacy location synced
