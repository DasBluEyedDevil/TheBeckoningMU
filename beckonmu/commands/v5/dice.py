"""V5 Dice Commands"""
from evennia.commands.command import Command
from world.v5_dice import roll_pool, rouse_check
from traits.utils import get_character_trait_value

class CmdRoll(Command):
    key = "+roll"
    locks = "cmd:all()"
    help_category = "Dice"
    def func(self):
        if not self.args:
            self.caller.msg("Usage: +roll <pool>")
            return
        try:
            pool = int(self.args.split()[0])
        except:
            self.caller.msg("Invalid pool")
            return
        r = roll_pool(pool)
        self.caller.msg(f"Rolled {pool}: {r.successes + r.criticals * 2} successes")

class CmdRollStat(Command):
    key = "+rollstat"
    locks = "cmd:all()"
    help_category = "Dice"
    def func(self):
        if not self.args or '+' not in self.args:
            self.caller.msg("Usage: +rollstat attr+skill")
            return
        a, s = self.args.split()[0].split('+')
        av = get_character_trait_value(self.caller, a.lower())
        sv = get_character_trait_value(self.caller, s.lower())
        if av is None or sv is None:
            self.caller.msg("Trait not found")
            return
        pool = av + sv
        hunger = 0
        if hasattr(self.caller.db, 'vampire'):
            hunger = self.caller.db.vampire.get('hunger', 0)
        r = roll_pool(pool, hunger=hunger)
        self.caller.msg(f"{a}+{s}: {r.successes + r.criticals * 2} successes")

class CmdRouseCheck(Command):
    key = "+rouse"
    locks = "cmd:all()"
    help_category = "Dice"
    def func(self):
        bp = 0
        if hasattr(self.caller.db, 'vampire'):
            bp = self.caller.db.vampire.get('blood_potency', 0)
        success, die = rouse_check(bp)
        if success:
            self.caller.msg(f"Rouse: {die} - Success!")
        else:
            if not hasattr(self.caller.db, 'vampire'):
                self.caller.db.vampire = {}
            h = self.caller.db.vampire.get('hunger', 0)
            nh = min(h + 1, 5)
            self.caller.db.vampire['hunger'] = nh
            self.caller.msg(f"Rouse: {die} - Failed. Hunger: {nh}/5")
