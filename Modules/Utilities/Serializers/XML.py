#FIXME: make sure that no " ends up in the attributes!!!

class ListSerializerToXml (object):
    def __init__ (self, listName, itemName, exclusionList=[]):
        self.listName = listName
        self.itemName = itemName
        self.exclusionList = exclusionList
        self.DATA_TYPE = "text/xml"
            
    def __call__ (self, objectList):
        returnString = "<%s>" % self.listName
        for item in objectList:
            returnString += "<%s" % self.itemName
            returnString += self.serializeObjectAttributes (item, self.exclusionList)
            returnString += "/>"
        returnString += "</%s>" % self.listName
        return returnString

class PythonListSerializer (ListSerializerToXml):
    def serializeObjectAttributes (self, item, exclusionList):
        returnString = ""
        for k,v in item.items ():
            if not k in exclusionList:
                returnString += ' %s="%s"' % (k,v)
        return returnString

class SQLObjectSerializer (ListSerializerToXml):
    def serializeObjectAttributes (self, item, exclusionList):
        returnString = ""
        for k,v in item.__dict__.items ():
            if ("_SO_val_" in k):
                k = k.replace ("_SO_val_", "")
                if not k in exclusionList:
                    returnString += ' %s="%s"' % (k, v)
        returnString += ' id="%s"' % item.id
        return returnString
        
class PythonDictSerializer (object):
    def __init__ (self, label):
        self.label = label
        self.DATA_TYPE = "text/xml"
        
    def __call__ (self, dictionary):
        returnString = "<" + self.label 
        for item in dictionary.items ():
            k,v = item
            returnString += " %s='%s'" % item
        returnString += "/>"
        return returnString

class XMLSerializer (object):
    def __init__ (self):
        pass
    def __call__ (self, pythonObject):
        assert "This class is not implemented yet" == False
        assert False
