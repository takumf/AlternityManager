from sys import exit, argv, stderr
from os import path
from itertools import starmap
from alternityGeneral import *

knownSkills=rawSkills()

def err(num, *msg):
    stderr.write("%s\n"%("\n".join(msg)))
    return num

def primeBasic(name, number):
    if number!=0:
        print "%s %s"%(name, number)
    return True

def createSkill(name, stat, parent, cost, profession, untrained, **junk):
    print "/newskill %s %s %s %s %s %s"%(stat, name, cost, parent, profession, untrained)

def primeSkill(name, level, **junk):
    def _determineValue(level, parent, purchased, **junk):
        if parent:
            return level
        return 1 if purchased else 0
    if name not in knownSkills:
        createSkill(name, **junk)
    return primeBasic(name, _determineValue(level, **junk))

def primeBonuses(bonuses):
    for b,v in bonuses:
        primeBasic("/bonus %s"%(b), v)

def primePerks(perks):
    return map(lambda x: primeBasic("perk %s"%(x), "+"), perks)

def generatePrimeData(character):
    def decideWhatToDoWithThisStat(stat):
        if hasattr(character.get(stat), "stat"): 
            return primeSkill(**character.get(stat))
        if stat=="bonuses":
            return primeBonuses(character.bonuses)
        if stat=="perks":
            return primePerks(character.perks)
        if stat in ["name", "species", "profession"]:
            return True
        primeBasic(stat, character.get(stat))
    print character.name
    print character.species
    print character.profession
    map(decideWhatToDoWithThisStat, character)
    return 0

def primeChr(rawCharacterInfo):
    return generatePrimeData(eval(rawCharacterInfo))
    # except:
    #     return err(2, "Can not prime this data.  Need to edit it by hand.")

def primeThisGuy(characterFile):
    return first(primeChr(characterFile.read()), characterFile.close())

def main(proggy, fpath=None, *args):
    if fpath and path.exists(fpath):
        return primeThisGuy(open(fpath, "rt"))
    return err(1, "Generates data to reconstruct character in case of corruption or backwards incompatibility.",
               "To use, run like so:\n $ python %s character.alternity"%(proggy))

if __name__=="__main__":
    try:
        exit(main(*argv))
    except KeyboardInterrupt:
        exit(0)
