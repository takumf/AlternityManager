import re
from random import randint

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


