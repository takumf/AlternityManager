import re
from random import randint
from sys import argv, exit
from alternityGeneral import alternityAbilities, numericTxt, genDat
from manager import first, consumeInput
import manager

def totallyTimeToQuit():
    return True

def roll(r):
    def translateMatch(match):
        num=int(match.group(1)) if len(match.group(1)) > 0  else 1
        sides=int(match.group(2)) if len(match.group(2)) > 0 else 0
        if sides < 1 or num < 1:
            return "0"
        if num == 1:
            return str(randint(1,sides))
        return "(%s)"%("+".join(map(lambda x: str(randint(1,sides)), range(num))))

    report=re.sub("(\d*)d(\d+)", translateMatch, r)
    return (eval(report), report, r)

def rollPenalty(r):
    def translatePenaltyToDice(penalty):
        if penalty > 4:
            return "d20+%sd20"%(penalty-4)
        if penalty < -4:
            return "d20%sd20"%(penalty+4)
        return "d20"+ {
            -4:"-d12", -3: "-d8", -2: "-d6", -1: "-d4", 
            0: "+d0", 1: "+d4", 2: "+d6", 3: "+d8", 4: "+d12" 
        }[penalty]
    return roll(translatePenaltyToDice(r))

def rollReport(tn, results):
    def _finalize(value, arithmetic, rollNotation):
        def _narrate(ordinary, good, amazing):
            if value <= amazing:
                return "Amazing success."
            if value <= good:
                return "Good success."
            if value <= ordinary:
                return "Ordinary success."
            if arithmetic.startswith("1+"):
                return "Automatic success."
            if arithmetic.startswith("20"):
                return "Critical failure."
            return "Failure."
        def _txt(*intersperses):
            return "%s -> %s %s (%s) vs [%s/%s/%s]\n"%intersperses
        return _txt(rollNotation, _narrate(*tn), value, arithmetic, *tn)
    return _finalize(*results)

def rollVersusStat(character, stat, situation=0, *stipulations):
    def _abilityCheck():
        return rollReport(manager.skillTnCalc(character.get(stat)), rollPenalty(int(situation)))
    def _otherRoll():
        return 0
    def _skillCheck():
        return rollReport(manager.skillTargetNumbers(character, 
                                                     stat),
                          rollPenalty(int(situation)))
    if stat not in character:
        return ""
    if stat in alternityAbilities():
        return _abilityCheck()
    if callable(character[stat]):
        return character[stat](_otherRoll())
    if not numericTxt(situation):
        return "Bad situation modifier: %s"%(situation)
    return _skillCheck()

def annotatedRoll(value, arithmetic, diceNotation):
    return "Rolling: %s -> %s = %s"%(diceNotation, arithmetic, value)

def promptForRoll(character):
    def _input():
        try:
            return consumeInput("roll")
        except EOFError:
            return ["/quit"]
    def _doRoll(wantedRoll, *args):
        if wantedRoll=="/quit":
            return totallyTimeToQuit
        if wantedRoll in character:
            return rollVersusStat(character, wantedRoll, *args)
        try:
            return annotatedRoll(*roll(wantedRoll))
        except NameError, SyntaxError:
            return "Don't know how to roll \"%s\""%(wantedRoll)
    return _doRoll(*_input())
    
def characterRollerLoop(character, rollResults=None):
    if not character:
        print "Bad character data"
        return 1
    while rollResults!=totallyTimeToQuit:
        manager.showCharacter(character)
        if rollResults:
            print "\n\t%s\n"%(rollResults)
        rollResults=promptForRoll(character)
    return 0

def rollerLoop(rollResults=None):
    while rollResults != totallyTimeToQuit:
        if rollResults:
            print "\n\t%s\n"%(rollResults)
        rollResults=promptForRoll({})

def main(proggy, *args):
    def _loadAndUse(f):
        return characterRollerLoop(first(eval(f.read()), 
                                f.close()))
    def _charf():
        return args[-1] if args else None
    def _load(f):
        return _loadAndUse(open(f,"rt")) if f else -1
    return _load(_charf()) if len(args) > 0 else rollerLoop()

if __name__=="__main__":
    try:
        exit(main(*argv))
    except KeyboardInterrupt:
        exit(0)

