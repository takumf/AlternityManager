from alternityGeneral import alternityAbilities, alternityPerks, sanitize, alternityDamageTracks
from itertools import starmap

def setAbilityValue(character, stat, val):
    def speciesLimitSatisfied():
        def _notDoneYetNeedsToBeImplemented():
            return True
        return _notDoneYetNeedsToBeImplemented()
    if not speciesLimitSatisfied():
        return (True, "The %s of %s does not fit within the species limits."%(stat, val))
    oldValue=character[stat]
    character[stat]=int(val)
    return (True, "Changed %s from %s to %s"%(stat, oldValue, character[stat]))

def boostAbilityValue(character, stat, val):
    return setAbilityValue(character, 
                           stat,
                           character[stat]+int(val))

def abilityManipulation(character, stat, val, args):
    def _report():
        return (True, "%s is currently %s"%(stat, character[stat]))
    if val is None:
        return _report()
    if val.startswith("+") or val.startswith("-"):
        return boostAbilityValue(character, stat, val)
    if val.isdigit():
        return setAbilityValue(character, stat, val)
    return _report()

def setSkillValue(character, skill, valRaw):
    def _trainedVal(v):
        if character[skill].parent:
            return v
        return "trained" if v or character[skill].purchased else "untrained"
    val=int(valRaw)
    oldValue=_trainedVal(character[skill].level)
    character[skill].purchased=True if val else False
    character[skill].level=int(val) if character[skill].parent else 0
    return (True, "Changed %s from %s to %s"%(skill, 
                                              oldValue,
                                              _trainedVal(val)))

def boostSkillValue(character, skill, val):
    return setSkillValue(character, 
                         skill,
                         character[skill].level+int(val))

def skillManipulation(character, stat, val, args):
    def _purchased():
        if character[stat].parent:
            return character[stat].level
        return "trained" if character[stat].purchased else "untrained"
    def _report():
        return (True, "%s is currently %s"%(stat, _purchased()))
    if val is None:
        return _report()
    if val.isdigit():
        return setSkillValue(character, stat, val)
    if val.startswith("+") or val.startswith("-"):
        if val[1:].isdigit():
            return boostSkillValue(character, stat, val)
    return _report()

def tryAlternatives(character, original, stat, val=None, *args):
    print "%s/%s/%s"%(original, stat, val)
    if stat in character:
        return genericManipulations(character, stat, val, *args)
    if val:
        return tryAlternatives(character, 
                               original, 
                               "_".join([stat, val]),
                               *args)
    return (True, '''"%s" is an unknown stat.'''%(original))

def perkManagement(character, rawPerk, *args):
    def _manipPerks(perkChart, perk, val, *arguments):
        if val=="-" and perk in character.perks:
            character.perks.remove(perk)
            return '''Removed "%s" from perks.'''%(perk)
        if val=="+" and perk in perkChart.keys():
            character.perks.append(perk)
            return '''Adding "%s" to perk list'''%(perk)
        return '''Use "-" to remove and "+" to add a perk.\n\tExample: %s +\nTo add %s to perk list.'''%(perk, perk)
    def _identifyPerk(perkChart):
        def _getPerkNameAndArgs(pn, arg1=None, *arggies):
            if pn in perkChart.keys():
                return _manipPerks(perkChart, pn, arg1, *arggies)
            if arg1:
                return _getPerkNameAndArgs("%s_%s"%(pn, arg1), *arggies)
            return "Known perks/flaws: %s"%(rawPerk, ", ".join(perkChart.keys()))
        return _getPerkNameAndArgs(sanitize(rawPerk), *args)
    return (True, "%s\nPerks/Flaws: %s"%(_identifyPerk(alternityPerks()),
                                         ", ".join(character.perks)))

def bonusManagement(character, *args):
    def _showBonuses():
        def _sho(k,v):
            return "%s=%s"%(k,v)
        return ", ".join(starmap(_sho, character.bonuses))
    return (True, "Bonuses: %s\nUse the /bonus command to add and remove bonuses."%(_showBonuses()))

def damageManipulation(character, track, val, *args):
    def _setDmg(value):
        character[track]=value
        return character[track]
    def _adjust(amount):
        return _setDmg(character[track]+amount)
    def _manip():
        if not val:
            return "%s has sustained %s %ss"%(character.name, 
                                              character.get(track),
                                              track)
        try:
            (_adjust if val.startswith("-") or val.startswith("+") else _setDmg)(int(val))
        except ValueError:
            return "Need an integer value for the amount of damage taken"
        return "%s %s damage now %s"%(character.name, track, character.get(track))
    return (True, _manip())

def genericManipulations(character, stat, val=None, *args):
    if stat.startswith("perk") or stat.startswith("flaw"):
        return perkManagement(character, val, *args)
    if stat.startswith("bonus"):
        return bonusManagement(character, val, *args)
    if stat not in character:
        return tryAlternatives(character, stat, stat, val, *args)
    if stat in alternityDamageTracks():
        return damageManipulation(character, stat, val, *args)
    if stat in alternityAbilities():
        return abilityManipulation(character, stat, val, args)
    return skillManipulation(character, stat, val, args)
