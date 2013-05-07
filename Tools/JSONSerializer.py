#FIXME: make sure that no " ends up in the attributes!!!
from PersistencyTools import Serializable 


def serializeObject (obj):
    return serializers[type(obj)] (obj)

class ListSerializerToJSON (object):
    def __init__ (self):
        self.DATA_TYPE = "application/json"
          
    def __call__ (self, objectList):
        items = ", ".join ([ serializeObject (item)
                             for item in objectList])
        return "[%s]" % items

class PythonListSerializer (ListSerializerToJSON):
    pass
    
class SQLObjectSerializer (ListSerializerToJSON):
    def serializeObjectAttributes (self, item, exclusionList):
        realExclusionList = [ "_SO_val_%s" % k
                              for k in exclusionList]
        items = [ "'%s': '%s'" % (k.replace ("_SO_val_", ""), v)
                  for k,v in item.__dict__.iteritems ()
                  if ("_SO_val_" in k) and (k not in realExclusionList)]
        items.append ('"id": "%s"' % item.id)
        return ", ".join (items)
        
class PythonDictSerializer (object):
    def __init__ (self):
        self.DATA_TYPE = "application/json"
        
    def __call__ (self, dictionary):
        pairs = ", ".join ([ "'%s': %s" % (k, serializeObject (v))
                             for k, v  in dictionary.iteritems () ])
        return "{%s}" % pairs

class SerializableSerializer (object):
    def __init__ (self):
        self.DATA_TYPE = "application/json"
    
    def __call__ (self, serializable):
        obj, serializer = serializable ()
        pairs = ", ".join (["'%s': %s" % (propertyName, serializeObject (propertyDumper (obj)))
                            for propertyName, propertyDumper in serializer])
        return "{%s}" % pairs

class JSONSerializer (object):
    def __init__ (self):
        pass
    def __call__ (self, pythonObject):
        assert "This class is not implemented yet" == False
        assert False
serializers = {
str: lambda obj : "'%s'" % (obj),
int: str,
unicode: lambda obj : "'%s'" % obj,
float: str,
list: PythonListSerializer (),
dict: PythonDictSerializer (),
Serializable: lambda obj : SerializableSerializer ()(obj)
}
