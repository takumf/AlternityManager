from sys import modules
from alternityGeneral import genDat, skillsOf, numericTxt, first, filt

def howdy(character, *args, **more):
    '''Say hello to the character!'''
    return "Howdy, %s!\n%s"%(character.name, " ".join(args))

def list(character, *args, **more):
    '''List all known character data.'''
    def _listStats(stats):
        def _spaceTxt(txt):
            return txt.ljust(30)
        def _composeLst(interval):
            return " ".join(map(_spaceTxt, stats[interval:interval+2]))
        return "\n".join(map(_composeLst, range(0,len(stats), 2)))
    return "Known stats...\n%s"%(_listStats(sorted(character.keys())))

def newskill(character, stat=None, name=None, cost=4, parent=None, profession="-", untrained=True, *junk):
    '''Add a new skill to the character data.  Example: /newskill int mandarin_language 4 knowledge'''
    if name in character:
        return "%s already appears to exist in character data"%(name)
    if not stat or not name:
        return "Must give the stat the skill falls under and its name.  Should also provide a cost and parent skill name (if applicable)"
    try:
        untr=eval(presentable(untrained))
    except NameError:
        untr=bool(untrained)
    character[name]=genDat({'parent':parent or None, 
                            'stat':stat,
                            'name':name,
                            'cost':int(cost) if numericTxt(cost) else 4,
                            'parent':parent or None,
                            'profession':profession,
                            'purchased':False,
                            'untrained':untr,
                            'level':0})
    skillsOf(character, True)
    return "Added skill data to character: %s"%(character[name])
    
def bonus(character, bonusName=None, val=None, *args):
    '''Manage weird bonuses the character gets such as those that come with species or professions.'''
    def _addBonus(num):
        character.bonuses.append((bonusName, num))
        return "Added %s to %s's %s."%(val, character.name, bonusName)
    def _deleteBonus():
        character.bonuses=filter(lambda x: x[0]!=bonusName and x[1]!=val, character.bonuses)
        return "Removed %s from %s's character data."%(bonusName, character.name)
    def _doAppropriateThing():
        if bonusName is None:
            return '''Manage character bonuses.  To add:
    /bonus bonus_name numeric_value +
To remove:
    /bonus bonus_name numeric_value -'''
        if numericTxt(val) and not args or args[0]!="-":
            return _addBonus(int(val))
        if val and args and args[0]=="-":
            return _deleteBonus()
        return "Bonus: %s now has value of %s"%(bonusName, val)
    return _doAppropriateThing()
