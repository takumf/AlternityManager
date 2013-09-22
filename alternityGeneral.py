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
