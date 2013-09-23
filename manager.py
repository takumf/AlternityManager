from sys import argv, exit
from os import path
from functools import partial
from itertools import starmap
from alternityGeneral import *
import commands
import manip

knownGeneralSkills={}

def speciesFreeSkills():
    return genDat({'human':"athletics,vehicle_operation,stamina,knowledge,awareness,interaction".split(","),
                   'fraal':"vehicle_operation,knowledge,awareness,resolve,interaction,telepathy".split(","),
                   'mechalus':"athletics,vehicle_operation,stamina,knowledge,computer_science,awareness".split(","),
                   'sesheyan':"melee_weapons,acrobatics,stamina,knowledge,awareness,interaction".split(","),
                   "t_sa":"athletics,manipulation,stamina,knowledge,awareness,interaction".split(","),
                   'weren':"athletics,unarmed_attack,stamina,knowledge,awareness,interaction".split(",")})

def freeSkillsFor(character):
    return speciesFreeSkills().get(sanitize(character.species), [])

def freeSkillPointsFor(character):
    return { 4:15,
             5:20,
             6:25,
             7:30,
             8:35,
             9:40,
             10:45,
             11:50,
             12:55,
             13:60,
             14:65,
             15:70,
             16:75,
        }[character.int]
def broadSkillsAtCharacterCreationFor(character):
    return { 4:2,
             5:2,
             6:3,
             7:3,
             8:4,
             9:4,
             10:5,
             11:5,
             12:6,
             13:6,
             14:7,
             15:7,
             16:8,
        }[character.int]

def halfish(value):
    return (value-(value%2))/2

def quarterish(value):
    return halfish(halfish(value))

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

def abilityCalc(name, baseScore):
    return (baseScore, halfish(baseScore), resmod(name, baseScore))

def skillTnCalc(baseScore):
    return (baseScore, halfish(baseScore), quarterish(baseScore))

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

def purchasedGenSkillsOf(character):
    freeSkills = freeSkillsFor(character)
    return genDat(filt(lambda k,v: v.get("parent")==None and v.get("purchased") and v.get('name') not in freeSkills, skillsOf(character).items()))
    
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

def showAbilities(character):
    def _abilShow(nm, val):
        def _cleanit(component):
            return ("%s"%(presentable(str(component)))).rjust(2)
        def _statLine(base, untr, res):
            return "%s ( %s ) %s"%(base, untr, res)
        def _tidyStat():
            return _statLine(*map(_cleanit, abilityCalc(nm,val)))
        def _presentValues():
            return "%s: %s"%(presentable(nm), _tidyStat())
        return inform(nm, _presentValues())
    map(lambda x: _abilShow(x, character.get(x)), alternityAbilities())
    return note(("Total ability scores: %s (60 free)"%(sum(map(lambda x: character.get(x), alternityAbilities())))).rjust(40))

def nmDisp(txt, indent):
    return ("%s%s"%("" if indent else "   ", txt)).ljust(27, ".")

def startsWithAny(subject, startChars):
    for c in startChars.upper():
        if subject.upper().startswith(c):
            return True
    return False

def skillExpense(character, skillName):
    def _costPerBoost(cost, level):
        return (cost)+level
    def _totalCost(cc, level):
        return sum(map(cc, range(0, level)))
    def _professionMatches(skillProf, chProf):
        return startsWithAny(chProf, skillProf)
    def _calcExpense(chProf, gainedFree, cost, profession, level, parent, purchased, **rest):
        if gainedFree or not purchased:
            return 0
        if parent is None:
            return cost-1 if _professionMatches(profession, chProf) else cost
        return _totalCost(partial(_costPerBoost, cost-1 if _professionMatches(profession,chProf) else cost),
                          level)
    return _calcExpense(character.profession,
                        skillName in freeSkillsFor(character),
                        **character.get(skillName))

def skillPointsSpent(character):
    def _calcy(sk):
        return skillExpense(character, sk)
    return sum(map(_calcy, skillsOf(character)))

def skillTargetNumbers(character, skill):
    def _calc(base, bonus, purchased):
        if bonus or purchased:
            return skillTnCalc(base+bonus)
        return skillTnCalc(halfish(base))
    def _prepThenCalc(level, stat, parent, purchased=False, **junk):
        return _calc(character.get(stat, 0),
                     level if parent else 0,
                     purchased)
    return _prepThenCalc(**character.get(skill))

def showSkills(character):
    def _composeSkillTxt(name, untrained, parent, stat, cost, level, profession, purchased=False, **remaining):
        def _lvlAnnotate():
            return str(level).rjust(2) if parent else "  "
        def _tnAnnotate(ordinary, good, amazing):
            return ("[%s/%s/%s]"%(ordinary, good, amazing)).ljust(9)
        def _tns():
            if parent:
                return skillTnCalc(character.get(stat)+levelBonus if level>0 else 0)
            return skillTnCalc(character.get(stat) if purchased else halfish(character.get(stat)))
        levelBonus=level if parent else 0
        showable=[]
        basic="%s %s %s %s"%(nmDisp(presentable(name), not parent),
                             _lvlAnnotate(),
                             _tnAnnotate(*_tns()),
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
    return inform(character, 
                  ("Skill Points Spent:".rjust(30) + " %s (%s free)\n"%(skillPointsSpent(character), freeSkillPointsFor(character))),
                  ("Broad Skills purchased:".rjust(29) + " %s (%s at creation)"%(len(purchasedGenSkillsOf(character)), broadSkillsAtCharacterCreationFor(character))))


def showCharacter(character):
    msg("%s: %s, %s"%(character.name, character.species, character.profession))
    showAbilities(character)
    showSkills(character)
    return character

def consumeInput(prompt="manage"):
    return raw_input("%s> "%(prompt)).strip().lower().split()

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

def managerSpecialCommand(character, command, args):
    def _cmd(cmd):
        if cmd in dir(commands):
            return getattr(commands, cmd)(character, *args)
        print "Unknown command: %s"%(command)
        return (True, "")
    return _cmd(command.strip("/"))

def managerStatManipulation(character, stat, args):
    return manip.genericManipulations(character, stat, *args)

def signifyResult(character, result, *messages):
    showCharacter(character)
    print "\n%s\n"%(" ".join(messages))
    return result

def handleManagerInput(character):
    def _procInCmd(command=None, *data):
        def _callMe():
            if command.startswith("/"):
                return managerSpecialCommand
            return managerStatManipulation
        if command is None:
            return True
        return signifyResult(character, 
                             *(_callMe()(character, command, data)))
    def _safelyConsumeInput():
        try:
            return consumeInput()
        except EOFError:
            return ["/quit"]
    return _procInCmd(*_safelyConsumeInput())

def managerLoop(character):
    showCharacter(character)
    while handleManagerInput(character):
        pass
    return character

def manageChar(character):
    return managerLoop(character)

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
    try:
        exit(main(*argv))
    except KeyboardInterrupt:
        exit(0)
