def AlwaysFalse (*args, **kwds):
        return False

class ValueProxy (object):
    def __init__ (self, value):
        self.value = value
    def __call__ (self, *__args, **__kw):
        return self.value

class FetchFromArgs(object):
    def __init__ (self, what):
        self.what = what
    def __call__ (self, *__args, **__kw):
        if __kw.has_key (self.what):
            return __kw[self.what]
        return None
