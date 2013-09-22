from sys import modules

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
