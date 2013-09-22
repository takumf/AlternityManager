from alternityGeneral import alternityAbilities

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

def genericManipulations(character, stat, val=None, *args):
    if stat not in character:
        return tryAlternatives(character, stat, stat, val, *args)
    if stat in alternityAbilities():
        return abilityManipulation(character, stat, val, args)
    return skillManipulation(character, stat, val, args)
