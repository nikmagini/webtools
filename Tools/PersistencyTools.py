class serializable_property (property):
    def __init__ (self, getter=None, setter=None, deleter=None, documentation=None):
        property.__init__ (self, getter, setter, deleter, documentation)
        self.serializable = True

class Serializable (object):
    def __init__ (self, obj, serializer):
        self.obj = obj
        self.serializer = serializer

    def __call__ (self):
        return (self.obj, self.serializer)
        
class Serializer (object):
    def __init__ (self, classType):
        self.classType = classType
        
    def __iter__ (self):
        properties = []
        for key, prop in self.classType.__dict__.iteritems ():
            if getattr (prop, "serializable", False) == True:
                properties.append ((key, self.classType.__dict__[key].fget))
        return iter (properties)
