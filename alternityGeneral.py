knownCharacterSkills=None

def alternityAbilities():
    return "str dex con int wil per".split()

class GenericStats(dict):
    def __repr__(self):
        return "genDat(%s)"%(dict(self.items()))

def first(initial=None, *remaining):
    return initial

def nth(lst, n):
    return first(*lst[n:])

def filt(proc, seq):
    return filter(lambda x: proc(*x), seq)

def presentable(text):
    return " ".join(map(str.capitalize, text.split("_")))

def sanitize(text):
    if text:
        return text.lower().replace(" ", "_").replace("'", "_").replace("-","_")
    return None

def note(*words):
    print " ".join(words)
    return True

def msg(*words):
    return note(" ====", *words)

def inform(ret, *words):
    return first(ret, note(*words))

def _classDefLine():
    return '''class _TmpStat(GenericStats):
    def _setter(self, k, v):
        self[k]=v
        return v\n'''

def _propGenLine(varnm):
    return '''    %s=property(lambda s: s.get("%s"), lambda s,v: s._setter("%s", v))\n'''%(varnm, varnm, varnm)

def _instTmp(deftxt, data):
    try:
        exec deftxt
    except:
        return inform({}, "Fail\n\n%s\n\n"%(deftxt))
    return _TmpStat(data)

def genClassDef(data):
    if not hasattr(data, "update"):
        raise Exception("You gave me a poop data: %s"%(data))
    return _instTmp(reduce(lambda c,v: c+_propGenLine(v), 
                           data, 
                           _classDefLine()),
                    data)

def genDat(data):
    return genClassDef(dict(data))

def halfish(value):
    return (value-(value%2))/2

def quarterish(value):
    return halfish(halfish(value))

def numericTxt(data):
    def _dat():
        return "%s"%(data)
    def _chk(t):
        return t.isdigit()
    def _signsOk(d):
        if d.startswith("-") or d.startswith("+"):
            return d[1:]
        return d
    return _chk(_signsOk(_dat()))

def rawSkills():
    def _fcrap(content):
        return eval(first(content.read(), content.close()))
    return _fcrap(open("skills.py", "rt"))

def reconstituteSkills(character):
    return genDat(filt(lambda k,v: hasattr(v, "update"), character.items()))

def skillsOf(character, reconstitute=False):
    global knownCharacterSkills
    if knownCharacterSkills is None or reconstitute:
        knownCharacterSkills=reconstituteSkills(character)
    return knownCharacterSkills

def alternityPerks():
    def _newPerk(name, ability, kind, *costs):
        return (sanitize(name), genDat({"name":sanitize(name),
                                        "ability":sanitize(ability),
                                        "type":kind,
                                        "cost":costs}))
    def _perks():
        return dict([
            _newPerk("Alien Artifact", "-", "Special", -5, 8),
            _newPerk("Ambidextrous", "dex", "Active", 4),
            _newPerk("Animal Friend", "wil", "Conscious", 4),
            _newPerk("Celebrity", "per", "Conscious", 3),
            _newPerk("Concentration", "int", "Conscious", 3),
            _newPerk("Danger Sense", "wil", "Active", 4),
            _newPerk("Faith", "wil", "Conscious", 5),
            _newPerk("Filthy Rich", "per", "Conscious", 6),
            _newPerk("Fists of Iron", "str", "Active", 2, 5),
            _newPerk("Fortitude", "con", "Active", 4),
            _newPerk("Good Luck", "wil", "Conscious", 3),
            _newPerk("Great Looks", "per", "Active", 3),
            _newPerk("Hightened Ability", "-", "Active", 10),
            _newPerk("Observant", "wil", "Active", 3),
            _newPerk("Photo Memory", "per", "Conscious", 3),
            _newPerk("Powerful Ally", "per", "Conscious", 4),
            _newPerk("Psionic Awareness", "int", "Conscious", 4),
            _newPerk("Reflexes", "dex", "Active", 4),
            _newPerk("Reputation", "wil", "Active", 3),
            _newPerk("Tough as Nails", "str", "Active", 4),
            _newPerk("Vigor", "con", "Active", 2,3,4),
            _newPerk("Willpower", "wil", "Active", 4),
            _newPerk("Bad Luck", "wil", "-", -6),
            _newPerk("Clueless", "int", "-", -2,-4,-6),
            _newPerk("Clumsy", "dex", "-", -5),
            _newPerk("Code of Honor", "wil", "-", -3),
            _newPerk("Delicate", "str", "-", -3),
            _newPerk("Dirt Poor", "per", "-", -5),
            _newPerk("Forgetful", "int", "-", -5),
            _newPerk("Fragile", "con", "-", -3),
            _newPerk("Infamy", "per", "-", -2, -4, -6),
            _newPerk("Oblivious", "wil", "-", -4),
            _newPerk("Obsessed", "int", "-", -2, -4, -6),
            _newPerk("Old Injury", "str", "-", -2, -4, -6),
            _newPerk("Phobia", "wil", "-", -2, -4, -6),
            _newPerk("Poor Looks", "per", "-", -3),
            _newPerk("Powerful Enemy", "per", "-", -2, -4, -6),
            _newPerk("Primitive", "int", "-", -2, -4, -6),
            _newPerk("Slow", "dex", "-", -6),
            _newPerk("Spineless", "wil", "-", -2, -4, -6),
            _newPerk("Temper", "wil", "-", -2, -4, -6),
        ])
    return genDat(_perks())

def alternityDamageTracks():
    def _ident(x):
        return x
    return genDat({'stun':_ident, 'wound':_ident, 'mortal':halfish, 'fatigue':halfish})
