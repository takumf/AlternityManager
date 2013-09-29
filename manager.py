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
    def _idSpeciesSkills(knownSkills, specieskw):
        return knownSkills.get(specieskw) or knownSkills.get("human")
    return _idSpeciesSkills(speciesFreeSkills(), 
                            sanitize(character.species if hasattr(
                                character, "species") else character))

def freeSkillPointsFor(character):
    return (character.int-1)*5

def broadSkillsAtCharacterCreationFor(character):
    return halfish(character.int)

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
    return _rawModCalc()

def abilityCalc(name, baseScore):
    return (baseScore, halfish(baseScore), resmod(name, baseScore))

def skillTnCalc(baseScore):
    return (baseScore, halfish(baseScore), quarterish(baseScore))

def extractBonuses(character, label):
    return sum([v for k,v in character.bonuses if k==label])

def initializeAbilities():
    def _gen(abils):
        return genDat(zip(abils, [7]*len(abils)))
    return _gen(alternityAbilities())

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
            if skillName in freeSkillsFor(sp):
                skillContent.purchased=True
            return (skillName, skillContent)
        return _speciesFreebies(*pair)
    def _abil():
        return initializeAbilities().items()
    def _dmg():
        return map(lambda x: (x, 0), alternityDamageTracks())
    def _skil():
        return map(_applySpeciesFreebies, initializeSkills().items())
    def _numerics():
        return _abil()+_skil()
    def _vitals():
        return [("name", nm), ("species", sp), ("profession", pr)]
    def _extra():
        return [("perks", []), ("bonuses", [])]
    return genDat(_numerics()+_vitals()+_extra()+_dmg())

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
        def _bns():
            return extractBonuses(character, "%s_resmod"%(nm))
        def _depictIt(base, untrained, res):
            return map(_cleanit, [base, untrained, "" if res is None else plusify(res+_bns())])
        def _cleanit(component):
            return ("%s"%(presentable(str(component)))).rjust(2)
        def _statLine(base, untr, res):
            return "%s ( %s ) %s"%(base, untr, res)
        def _tidyStat():
            return _statLine(*_depictIt(*abilityCalc(nm, val)))
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

def baseActionCheck(character):
    def _profBonus():
        return {sanitize("Combat Spec"):3,
                sanitize("Diplomat"):1,
                sanitize("Free Agent"):2,
                sanitize("Tech Op"):1}.get(sanitize(character.profession), 0)
    return halfish(character.int+character.dex)+_profBonus()

def actionCheckScore(character):
    def _scores(base):
        return ("%s+"%(base+1), base, halfish(base), quarterish(base))
    return map(str, _scores(baseActionCheck(character)))

def actionsPerRound(character):
    def _calc(cw):
        if cw<16:
            return 1
        if cw<24:
            return 2
        if cw<32:
            return 3
        return 4
    return _calc(character.con+character.wil)

def lastResortMaxAndCost(character):
    def _calc(rates):
        return rates.get(first(*filter(lambda x: character.per<x, 
                                       sorted(rates.keys())))) or (4,1)
    return _calc({8: (0,0), 11: (1,3), 13: (2,2), 15: (3, 1)})

def movementRates(character):
    def _ratesDict():
        return {8: (6,4,2,1,2,6,12),
                10: (8,6,2,1,2,8,16),
                12: (10,6,2,1,2,10,20),
                14: (12,8,2,1,2,12,24),
                16: (14,10,4,2,14,28),
                18: (16,10,4,2,4,16,32),
                20: (18,12,4,2,4,18,36),
                22: (20,12,4,2,4,20,40),
                24: (22,14,4,2,4,22,44),
                26: (24,16,6,3,6,24,48),
                28: (26,16,6,3,6,24,52),
                30: (28,18,6,3,6,28,56),
                32: (30,20,6,4,8,30,60)}
    def _rateLabels():
        return ["sprint", "run", "walk", "easy_swim", "swim", "glide", "fly"]
    def _highestMovement():
        return (32,22,8,4,8,32,64)
    def _calc(strdex, rates):
        return rates.get(first(*filter(lambda x: strdex<x, 
                                       sorted(rates.keys()))), 
                         _highestMovement())
    def _mr():
        return _calc(character.str+character.dex, _ratesDict())
    return genDat(zip(_rateLabels(), _mr()))

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
    return sum(map(_calcy, skillsOf(character)))+totalPerkExpenses(character)

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

def determinePerkCost(character, perkName):
    def _calcCost(perkChart):
        def _calc(name=None, cost=[100], **junk):
            if name:
                return nth(cost, character.perks.count(name)-1) or first(*cost)
            return 100
        return _calc(**perkChart.get(sanitize(perkName)))
    return _calcCost(alternityPerks())

def totalPerkExpenses(character):
    return sum(map(partial(determinePerkCost, character),
                   set(character.perks)))

def showPerks(character):
    def _labelPerkData(name=None, cost=None, **perkJunk):
        return "%s (%s)"%(presentable(name), 
                          determinePerkCost(character, name))
    def _perkNamWithCosts(perkChart):
        def _lblPerk(perk):
            return _labelPerkData(**perkChart.get(perk, {}))
        return ", ".join(map(_lblPerk, set(character.perks)))
    return _perkNamWithCosts(alternityPerks())

def showDerivedStats(character):
    def mrTxt(k,v):
        return "%s: %s"%(presentable(k),str(v).ljust(3))
    print "Action Check: %s Actions/Round: %s"%(("/".join(actionCheckScore(character))).ljust(15),
                              actionsPerRound(character))
    for x in starmap(mrTxt, movementRates(character).items()):
        print "%s"%(x),
    print ""
    print "Perks/Flaws: %s"%(showPerks(character))

def showDamageTracks(character):
    def _speciesDmgBonus():
        return halfish(character.con) if sanitize(character.species)=="weren" else 0
    def _sho(track):
        def _calc(taken, calcer):
            def _print(cap):
                print "%s: %s %s%s"%(
                    presentable(track).rjust(8),
                    ("%s"%(cap)).rjust(2),
                    ("%s%s"%("*"*taken, "o"*(cap-taken))).ljust(calcer(20)),
                    "\n" if calcer==halfup else ""),
            return _print(calcer(character.con+_speciesDmgBonus())+extractBonuses(character, 
                                                               track))
        return _calc(character.get(track),
                      alternityDamageTracks().get(track))
    return all(map(_sho, ["stun", "fatigue", "wound", "mortal"]))

def showCharacter(character):
    msg("%s: %s, %s"%(character.name, character.species, character.profession))
    map(lambda x: x(character), [showAbilities, 
                                 showDamageTracks, 
                                 showDerivedStats, 
                                 showSkills])
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
    def _cleanupNm(species):
        return species.replace("_", "'").capitalize()
    note("Choose species:", ", ".join(map(_cleanupNm, speciesFreeSkills().keys())))
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
