from functools import partial
from sys import exit, stdin

def sanitize(text):
    if text:
        return text.lower().replace(" ", "_").replace("'", "_").replace("-","_")
    return None

def processIndividualSkill(parent, stat, name, cost, prof, untr):
    return {'parent':parent,
            'stat':stat,
            'name':sanitize(name),
            'cost':cost,
            'profession':prof,
            'untrained':untr}

def _lns(txt):
    return filter(None, map(str.strip, txt.split("\n")))

def _csln(line):
    return line.split(",")

def processSkillGroup(skGroup):
    def specialtySkillUnder(name, specialty):
        return processIndividualSkill(name, *_csln(specialty))
    def skillGroup(broad, *specialties):
        def _doBroadSkillFirst(parent):
            return [parent]+map(partial(specialtySkillUnder,
                                        parent.get("name")),
                                specialties)
        return _doBroadSkillFirst(processIndividualSkill(None,
                                                         *_csln(broad)))
    return skillGroup(*_lns(skGroup))

def convertChunksIntoSkillGroups(groups):
    return sum(map(processSkillGroup, groups), [])

def splitCsvIntoChunks(rawStream):
    return convertChunksIntoSkillGroups(rawStream.split("\n\n"))

def makeNestedDictionaryOfSkillsDictionary(skills):
    def _individualSkill(skl):
        return (skl.get('name'), skl)
    return dict(map(_individualSkill, skills))

def convertCSVinput():
    print makeNestedDictionaryOfSkillsDictionary(splitCsvIntoChunks(stdin.read()))
    return 0

if __name__=="__main__":
    exit(convertCSVinput())
