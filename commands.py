from sys import modules
from alternityGeneral import genDat, skillsOf, numericTxt, first, filt

def quit(*args, **more):
    '''Save data and exit the character manager.'''
    return (None, "Quitting...")

def howdy(character, *args, **more):
    '''Say hello to the character!'''
    return (True, "Howdy, %s!\n%s"%(character.name, " ".join(args)))

def help(*args, **more):
    '''This help message.'''
    def _cmdTxt(txt):
        return ("/%s"%(txt)).rjust(10)
    def _doHelp(module):
        def _funcs():
            def _predicate(thing):
                if thing in ["altyCmd"]:
                    return False
                return callable(getattr(module, thing))
            return filter(_predicate, dir(module))
        msg=""
        for x in _funcs():
            msg+= "%s: %s\n"%(_cmdTxt(x),
                            getattr(module, x).__doc__)
        return (True, "Known commands...\n%s\n"%(msg))
    return _doHelp(modules[__name__])

def list(character, *args, **more):
    '''List all known character data.'''
    def _listStats(stats):
        def _spaceTxt(txt):
            return txt.ljust(30)
        def _composeLst(interval):
            return " ".join(map(_spaceTxt, stats[interval:interval+2]))
        return "\n".join(map(_composeLst, range(0,len(stats), 2)))
    return (True, "Known stats...\n%s"%(_listStats(sorted(character.keys()))))

def newskill(character, stat=None, name=None, cost=4, parent=None, profession="-", untrained=True, *junk):
    '''Add a new skill to the character data.  Example: /newskill int mandarin_language 4 knowledge'''
    if name in character:
        return (True, "%s already appears to exist in character data"%(name))
    if not stat or not name:
        return (True, "Must give the stat the skill falls under and its name.  Should also provide a cost and parent skill name (if applicable)")
    character[name]=genDat({'parent':parent or None, 
                            'stat':stat,
                            'name':name,
                            'cost':int(cost) if numericTxt(cost) else 4,
                            'parent':parent or None,
                            'profession':profession,
                            'purchased':False,
                            'untrained':eval(untrained) if hasattr(untrained, "split") else bool(untrained),
                            'level':0})
    skillsOf(character, True)
    return (True, "Added skill data to character: %s"%(character[name]))
    
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
    return (True, _doAppropriateThing())
