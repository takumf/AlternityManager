def alternityAbilities():
    return "str dex con int wil per".split()

class GenericStats(dict):
    def __repr__(self):
        return "genDat(%s)"%(dict(self.items()))

def first(initial=None, *remaining):
    return initial

def filt(proc, seq):
    return filter(lambda x: proc(*x), seq)

def presentable(text):
    return " ".join(map(str.capitalize, text.split("_")))

def sanitize(text):
    if text:
        return text.lower().replace(" ", "_").replace("'", "_").replace("-","_")
    return None

def note(*words):
    print " ".join(words)
    return True

def msg(*words):
    return note(" ====", *words)

def inform(ret, *words):
    return first(ret, note(*words))

def _classDefLine():
    return '''class _TmpStat(GenericStats):
    def _setter(self, k, v):
        self[k]=v
        return v\n'''

def _propGenLine(varnm):
    return '''    %s=property(lambda s: s.get("%s"), lambda s,v: s._setter("%s", v))\n'''%(varnm, varnm, varnm)

def _instTmp(deftxt, data):
    try:
        exec deftxt
    except:
        return inform({}, "Fail\n\n%s\n\n"%(deftxt))
    return _TmpStat(data)

def genClassDef(data):
    if not hasattr(data, "update"):
        raise Exception("You gave me a poop data: %s"%(data))
    return _instTmp(reduce(lambda c,v: c+_propGenLine(v), 
                           data, 
                           _classDefLine()),
                    data)

def numericTxt(data):
    def _dat():
        return "%s"%(data)
    def _chk(t):
        return t.isdigit()
    def _signsOk(d):
        if d.startswith("-") or d.startswith("+"):
            return d[1:]
        return d
    return _chk(_signsOk(_dat()))
