from sys import argv, exit
from os import path
from functools import partial
from itertools import starmap

knownCharacterSkills=None
knownGeneralSkills={}

class GenericStats(dict):
    def __repr__(self):
        return "genDat(%s)"%(dict(self.items()))

def first(initial=None, *remaining):
    return initial

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

def alternityAbilities():
    return "str dex con int wil per".split()

def speciesFreeSkills():
    return genDat({'human':"athletics,vehicle_operation,stamina,knowledge,awareness,interaction".split(","),
                   'fraal':"vehicle_operation,knowledge,awareness,resolve,interaction,telepathy".split(","),
                   'mechalus':"athletics,vehicle_operation,stamina,knowledge,computer_science,awareness".split(","),
                   'sesheyan':"melee_weapons,acrobatics,stamina,knowledge,awareness,interaction".split(","),
                   "t_sa":"athletics,manipulation,stamina,knowledge,awareness,interaction".split(","),
                   'weren':"athletics,unarmed attack,stamina,knowledge,awareness,interaction".split(",")})

def freeSkillsFor(character):
    return speciesFreeSkills().get(sanitize(character.species), [])

def halfish(value):
    return (value-(value%2))/2

def quarterish(value):
    return halfish(halfish(value))

def abilityCalc(baseScore):
    return [baseScore, halfish(baseScore)]

def skillTnCalc(baseScore):
    return [baseScore, halfish(baseScore), quarterish(baseScore)]

def initializeAbilities():
    def _gen(abils):
        return genDat(zip(abils, [7]*len(abils)))
    return _gen(alternityAbilities())

def rawSkills():
    def _fcrap(content):
        return eval(first(content.read(), content.close()))
    return _fcrap(open("skills.py", "rt"))

def initializeSkills():
    def _nsk(stat, parent, profession, untrained, name, cost, purchased=False):
        try:
            return genDat({'stat':stat, 
                           'profession':profession, 
                           'untrained':untrained, 
                           'name':name, 
                           'cost':int(cost), 
                           'parent':parent, 
                           'purchased':purchased,
                           'level': 0})
        except:
            print {'stat':stat, 'profession':profession, 'untrained':untrained, 'name':name, 'cost':cost, 'parent':parent}
        return {}
    def _handleSkill(skillSource):
        return map(lambda x: (x, _nsk(**skillSource.get(x))), skillSource)
    return genDat(_handleSkill(rawSkills()))

def initializeCharacter(nm="Unknown", sp="Human", pr="Combat Spec"):
    def _applySpeciesFreebies(pair):
        def _speciesFreebies(skillName, skillContent, *extraneousPoop):
            if skillName in speciesFreeSkills().get(sp.lower(), []):
                skillContent.purchased=True
            return (skillName, skillContent)
        return _speciesFreebies(*pair)
    def _abil():
        return initializeAbilities().items()
    def _skil():
        return map(_applySpeciesFreebies, initializeSkills().items())
    def _numerics():
        return _abil()+_skil()
    def _vitals():
        return [("name", nm), ("species", sp), ("profession", pr)]
    return genDat(_numerics()+_vitals())

def skillsOf(character):
    global knownCharacterSkills
    if knownCharacterSkills is None:
        knownCharacterSkills=genDat(filt(lambda k,v: hasattr(v, "update"), character.items()))
    return knownCharacterSkills

def genSkillsOf(character, stat):
    global knownGeneralSkills
    if stat not in knownGeneralSkills:
        knownGeneralSkills[stat]=genDat(filt(lambda k,v: v.get("parent")==None and v.get('stat')==stat, skillsOf(character).items()))
    return knownGeneralSkills.get(stat)


def childSkillsOf(character, parent):
    return genDat(filt(lambda k,v: v.get("parent")==parent, skillsOf(character).items()))

def abilitiesOf(character):
    return genDat(filt(lambda k,v: k in alternityAbilities(), character.items()))

def plusify(number):
    if number is not None:
        return "%s%s"%("+" if number>=0 else "", number)
    return ""

def resmod(nm, val):
    def _rawModCalc():
        if nm in "con per".split():
            return None
        if val<5:
            return -2
        if val<7:
            return -1
        if val>18:
            return 5
        return max(0, (val-9)/2)
    return plusify(_rawModCalc())

def showAbilities(character):
    def _abilShow(nm, val):
        def _resMod():
            return resmod(nm, val)
        def _statVal():
            return ("%s"%(val)).rjust(2)
        return inform(nm, "%s: %s ( %s ) %s"%(presentable(nm), 
                                              _statVal(), 
                                              halfish(val), 
                                              _resMod()))
    map(lambda x: _abilShow(x, character.get(x)), alternityAbilities())
    return note(("Total ability scores: %s"%(sum(map(lambda x: character.get(x), alternityAbilities())))).rjust(40))

def nmDisp(txt, indent):
    return ("%s%s"%("" if indent else "   ", txt)).ljust(27, ".")

def startsWithAny(subject, startChars):
    for c in startChars.upper():
        if subject.upper().startswith(c):
            return True
    return False

def skillExpense(character, skillName):
    def _costPerBoost(cost, level):
        return (cost-1)+level
    def _totalCost(cc, il, level):
        return sum(map(cc, range(il, level)))
    def _calcExpense(chProf, gainedFree, cost, profession, level, **rest):
        return _totalCost(partial(_costPerBoost, cost-1 if profession==chProf else cost),
                          1 if gainedFree else 0,
                          level)
    return _calcExpense(character.profession,
                        skillName in freeSkillsFor(character),
                        **character.get(skillName))

def showSkillExpense(character, skillNameRaw):
    def _se(skillName):
        profession=character.get(skillNameRaw).profession
        professionMatches=startsWithAny(character.profession, 
                                        profession)
        professionBenefit=-1 if professionMatches else 0
        msg("%s: Cost %s.  %s points spent"%(
            presentable(skillName), 
            character.get(skillNameRaw).cost+professionBenefit,
            skillExpense(character, skillName) ))
        if skillName in freeSkillsFor(character):
            note("    This is a free skill for your species")
        if professionMatches:
            note("    This skill falls under your profession")
        return note("")
    return _se(sanitize(skillNameRaw))

def skillPointsSpent(character):
    def _calcy(sk):
        return skillExpense(character, sk)
    return sum(map(_calcy, skillsOf(character)))
                                         
def showSkills(character):
    def _composeSkillTxt(name, untrained, parent, stat, cost, level, profession, purchased=False, **remaining):
        levelBonus=level if parent else 0
        ordinary=character.get(stat)+levelBonus if purchased or level>0 else 0
        good=halfish(ordinary)
        amazing=halfish(good)
        showable=[]
        basic="%s %s [%s/%s/%s] %s"%(nmDisp(presentable(name), not parent),
                                     level if parent else ".",
                                     ordinary,
                                     good, 
                                     amazing,
                                     skillExpense(character, name))
        for x in childSkillsOf(character, name):
            showable.extend(_composeSkillTxt(**character.get(x)))
        if level>0 or purchased or showable:
            return [basic]+showable
        return showable
    def _showSkill(**things):
        txt="\n".join(_composeSkillTxt(**things))
        if txt:
            print txt
    def _skilGroupShow(dat):
        for k,v in sorted(dat.items()):
            _showSkill(**v)
    def _skillsUnderStat(stat):
        return genSkillsOf(character, stat)
    map(_skilGroupShow, 
        map(_skillsUnderStat, 
            alternityAbilities()))
    return inform(character, ("Total Skill Points Spent: %s"%(skillPointsSpent(character))).rjust(40))

def showCharacter(character):
    msg("%s: %s, %s"%(character.name, character.species, character.profession))
    showAbilities(character)
    showSkills(character)
    return character

def consumeInput():
    return raw_input("> ").lower().split()

def validatePrompt(promptTxt, validatorFunc):
    def _getInput():
        return raw_input("%s: "%(promptTxt))
    txt=_getInput()
    while not validatorFunc(txt):
        txt=_getInput()
    return txt

def namePrompt():
    return validatePrompt("Name", lambda x: True)

def speciesPrompt():
    return validatePrompt("Species", lambda x: True)

def professionPrompt():
    return validatePrompt("Profession", lambda x: True)

def createNewCharacter():
        return initializeCharacter(namePrompt(),
                                   speciesPrompt(),
                                   professionPrompt())

def horriblyUglyBloatyCruftyManageChar(character):
    def boostSkill(stat, amount):
        character[stat].level+=amount
        return msg("Boosted %s by %s"%(stat, amount))
    def _boost(stat, amount):
        if stat in skillsOf(character).keys():
            return boostSkill(stat, amount)
        character[stat]+=amount
        return True
    def setSkill(stat, amount):
        character[stat].purchased=True if amount else False
        if character.get(stat).parent is not None:
            character[stat].level=amount
        return True
    def _set(stat, amount):
        if stat in skillsOf(character).keys():
            if hasattr(amount, "real"):
                return setSkill(stat, amount)
            return msg("Need a number to set for the skill level")
        character[stat]=amount
        return True
    def _adjust(stat, val=None, *args):
        if val is None:
            return msg("No value given for %s"%(stat))
        if val.startswith("+") or val.startswith("-"):
            return _boost(stat, int(val))
        if stat in alternityAbilities() and not val.isdigit():
            return msg("Need a number for ability setting.")
        return _set(stat, int(val) if val.isdigit() else val)
    def _specialCommand(command, args):
        def _dflt(*junk):
            return msg("           Unknown command: %s"%(command))
        def _lst(*junk):
            '''List all known stats'''
            msg("Known stats...")
            toggle=False
            for x in sorted(character.keys()):
                print x.ljust(23),
                if toggle:
                    print ""
                toggle=not toggle
            return msg("")
        def _quit(*junk):
            '''Leave the character editor'''
            return None
        def _skexp(skillName, *junk):
            '''Show additional information about a skill'''
            return showSkillExpense(character, skillName)
        def _processCommand(commandsCollection):
            def _hlp(*junk):
                '''Show this help info'''
                msg("Known commands...")
                for x in sorted(commandsCollection.keys()):
                    print "\t/%s\t%s"%(x, commandsCollection.get(x).__doc__)
                return True
            commandsCollection['help']=_hlp
            return commandsCollection.get(command.strip("/"), _dflt)(*args)
        return _processCommand({"list": _lst,
                                "quit": _quit,
                                "skill": _skexp})
    def processInp(stat=None, *args):
        if stat is None:
            return msg("")
        if stat.startswith("/"):
            return _specialCommand(stat, args)
        if stat in character:
            return _adjust(stat, *args)
        return msg("Unknown stat: %s"%(stat))
    def _inp():
        try:
            showCharacter(character)
            return processInp(*consumeInput())
        except EOFError, KeyboardInterrupt:
            return None
    while _inp()!=None:
        pass
    return character

def manageChar(character):
    return horriblyUglyBloatyCruftyManageChar(character)

def saveCharacterData(charDat):
    def _write(f):
        return first(0,
                     f.write("%s"%(charDat)),
                     f.close())
    def _saveFile(fpth):
        return _write(open(fpth, "wt"))
    if charDat:
        return _saveFile("%s.alternity"%(sanitize(charDat.name)))
    return 1

def main(proggy, *args):
    def loadCharacter(f):
        def _handle(ch):
            if "-d" in args:
                return showCharacter(ch)
            return manageChar(ch)
        return _handle(first(eval(f.read()), f.close()))
    def _go():
        if args and path.exists(args[-1]):
            return loadCharacter(open(args[-1], "rt"))
        return manageChar(createNewCharacter())
    return saveCharacterData(_go())

if __name__=="__main__":
    exit(main(*argv))
