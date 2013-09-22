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
    return (eval(report), report)


