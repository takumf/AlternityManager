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

def presentable(text):
    return " ".join(map(str.capitalize, text.split("_")))

def sanitize(text):
    if text:
        return text.lower().replace(" ", "_")
    return None

def genClassDef(data):
    if not hasattr(data, "update"):
        raise Exception("You gave me a poop data: %s"%(data))
    cmd='''class _TmpStat(GenericStats):
    def _setter(self, k, v):
        self[k]=v
        return v\n'''
    for x in data:
        cmd+='''    %s=property(lambda s: s.get("%s"), lambda s,v: s._setter("%s", v))\n'''%(x, x, x)
    try:
        exec cmd
        return _TmpStat(data)
    except:
        print "Fail\n\n"
        print cmd
        print "\n\n"
    return {}

def genDat(data):
    return genClassDef(dict(data))

def alternityAbilities():
    return "str dex con int wil per".split()

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
    def _nsk(stat, parent, profession, untrained, name, cost):
        try:
            return genDat({'stat':stat, 'profession':profession, 'untrained':untrained, 'name':name, 'cost':int(cost), 'parent':parent, 'level': 0}.items())
        except:
            print {'stat':stat, 'profession':profession, 'untrained':untrained, 'name':name, 'cost':cost, 'parent':parent}
        return {}
    def _handleSkill(skillSource):
        return map(lambda x: (x, _nsk(**skillSource.get(x))), skillSource)
    return genDat(_handleSkill(rawSkills()))

def initializeCharacter(nm="Unknown", sp="Human", pr="Combat Spec"):
    def _abil():
        return initializeAbilities().items()
    def _skil():
        return initializeSkills().items()
    def _both():
        return _abil()+_skil()
    def _vitals():
        return [("name", nm), ("species", sp), ("profession", pr)]
    return genDat(_both()+_vitals())

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

def resmod(nm, val):
    if nm in "con per".split():
        return None
    if val < 5: 
        return -2
    if val < 7:
        return -1
    if val > 18:
        return 5
    if val > 16:
        return 4
    if val > 14:
        return 3
    if val > 12:
        return 2
    if val > 10:
        return 1
    return 0

def showAbilities(character):
    def _abilShow(nm, val):
        def _resMod():
            rm=resmod(nm, val)
            if rm is not None:
                return rm
            return ""
        print "%s: %s ( %s ) %s"%(presentable(nm), ("%s"%(val)).rjust(2), halfish(val), _resMod())
        return nm
    for x in alternityAbilities():
        _abilShow(x, character.get(x))
    print "Total ability scores: %s"%(sum(map(lambda x: character.get(x), alternityAbilities())))
    return True

def nmDisp(txt, indent):
    return ("%s%s"%("" if indent else "   ", txt)).ljust(27, ".")

def expense(cost, level, offset=0):
    def _foo(lvl):
        return (cost-1+offset)+lvl
    if level>0:
        return sum(map(_foo, range(1,level)), cost)
    return 0

def startsWithAny(this, these):
    for c in these.upper():
        if this.upper().startswith(c):
            return True
    return False

def skillPointsSpent(character):
    def _calcy(sk):
        def _calcit(cost, level, profession, **junk):
            return expense(cost, 
                           level,
                           -1 if startsWithAny(character.profession, profession) else 0)
        return _calcit(**character[sk])
    return sum(map(_calcy, skillsOf(character)))
                                         
def showSkills(character):
    def _composeSkillTxt(name, untrained, parent, stat, cost, level, profession, **remaining):
        ordinary=character.get(stat)+level
        good=halfish(ordinary)
        amazing=halfish(good)
        showable=[]
        basic="%s %s [%s/%s/%s] %s"%(nmDisp(presentable(name), not parent),
                                     level,
                                     ordinary,
                                     good, 
                                     amazing,
                                     expense(cost, level, -1 if startsWithAny(character.profession, profession) else 0))
        for x in childSkillsOf(character, name):
            showable.extend(_composeSkillTxt(**character.get(x)))
        if level>0 or showable:
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
    print "Total Skill Points Spent: %s"%(skillPointsSpent(character))
    return character

def showCharacter(character):
    print "%s: %s, %s"%(character.name, character.species, character.profession)
    showAbilities(character)
    showSkills(character)
    return character

def createNewCharacter():
        return initializeCharacter(raw_input("Name: "),
                                   raw_input("Species: "),
                                   raw_input("Profession: "))

def manageChar(character):
    def boostSkill(stat, amount):
        character[stat].level+=amount
        return True
    def _boost(stat, amount):
        if stat in skillsOf(character).keys():
            return boostSkill(stat, amount)
        character[stat]+=amount
        return True
    def setSkill(stat, amount):
        character[stat].level=amount
        return True
    def _set(stat, amount):
        if stat in skillsOf(character).keys():
            return setSkill(stat, amount)
        character[stat]=amount
        return True
    def _adjust(stat, val=None, *args):
        if val is None:
            print "       No value given for %s"%(stat)
            return True
        if val.startswith("+") or val.startswith("-"):
            return _boost(stat, int(val))
        return _set(stat, int(val) if val.isdigit() else val)
    def _specialCommand(command, args):
        def _dflt(*junk):
            print "           Unknown command: %s"%(command)
            return True
        def _lst(*junk):
            '''List all known stats'''
            print "==== Known stats..."
            toggle=False
            for x in sorted(character.keys()):
                print x.ljust(23),
                if toggle:
                    print ""
                toggle=not toggle
            print ""
            return True
        def _quit(*junk):
            '''Leave the character editor'''
            return None
        def _processCommand(commandsCollection):
            def _hlp(*junk):
                '''Show this help info'''
                print "==== Known commands..."
                for x in sorted(commandsCollection.keys()):
                    print "\t/%s\t%s"%(x, commandsCollection.get(x).__doc__)
                return True
            commandsCollection['help']=_hlp
            return commandsCollection.get(command.strip("/"), _dflt)(*args)
        return _processCommand({"list": _lst,
                                "quit": _quit})
    def processInp(stat, *args):
        if stat.startswith("/"):
            return _specialCommand(stat, args)
        if stat in character:
            return _adjust(stat, *args)
        print "Unknown stat: %s"%(stat)
        return True
    def _inp():
        try:
            showCharacter(character)
            return processInp(*raw_input("> ").lower().split())
        except EOFError:
            return None
    while _inp()!=None:
        pass
    return character

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
    try:
        x=_go()
        fpth="%s.alternity"%(sanitize(x.name))
        f=open(fpth, "wt")
        f.write("%s"%(x))
        f.close()
        return 0
    except Exception as e:
        print e
        return 1

if __name__=="__main__":
    exit(main(*argv))
