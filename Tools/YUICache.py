from os.path import dirname, basename, join
import re, os

class YUIContentFactory (object):
    def __init__ (self):
        self.__fileTypeMap = {"png": "image/png",
                              "gif": "image/gif",
                              "css": "text/css",
                              "js": "text/javascript"}
        
        self.__remappingRE = re.compile ("(url\s*\()([^)]*/|)([^)]*)(\))")
        self.__labelRE = re.compile ("([^-]*)(-beta|)(-min|-debug|)[.](.*)")
        self.__comparators = [PreferAttribute ("extension", "js"), 
                              PreferName ("-beta"),
                              PreferName ("-min"),
                              PreferName ("-debug"),
                              PreferName ("/skins/sam"),
                              PreferName ("/build/assets"),
                              PreferFirst ()]

    def create (self, fullPath):
        content = YUIContent (fullPath)
        content._YUIContent__labelRE = self.__labelRE
        content._YUIContent__remappingRE = self.__remappingRE
        content._YUIContent__comparators = self.__comparators
        if content.extension not in self.__fileTypeMap.iterkeys ():
            return None
        content.contentType = self.__fileTypeMap[content.extension]
        return content

class PreferName (object):
    def __init__ (self, string):
        self.__string = string

    def __call__ (self, a, b):
        string = self.__string
        truthTable = [ self.__string in fullPath
                       for fullPath in [a.fullPath, b.fullPath]]
        if truthTable == [False, False]:
            return 0
        elif truthTable == [True, True]:
            return 0
        elif truthTable == [True, False]:
            return 1
        elif truthTable == [False, True]:
            return -1
        assert (False)

class AvoidName (PreferName):
    def __init__ (self, string):
        PreferName.__init__ (self, string)

    def __call__ (self, a, b):
        return - PreferName.__call__ (self, a, b)


class PreferAttribute (object):
    def __init__ (self, attribute, value):
        self.__attribute = attribute
        self.__value = value
    def __call__ (self, a, b):
        a = getattr (a, self.__attribute)
        b = getattr (b, self.__attribute)
        if a == b:
            return 0
        if a == self.__value:
            return 1
        if b == self.__value:
            return -1
        return 0

class PreferFirst (object):
    def __call__ (self, a, b):
        return 1
        
class YUIContent (object):
    extension = property (lambda self : self.__getExtension ())
    contentType = property (lambda self : self.__contentType,
                            lambda self, value : self.__setContentType (value))
    fullPath = property (lambda self : self.__fullPath,
                         lambda self,value : self.__setFullPath (value))
    data = property (lambda self : self.__data,
                     lambda self, value : self.__setData (value))
    beta = property (lambda self : "-beta" in self.fullPath)
    debug = property (lambda self : "-debug" in self.fullPath)
    minimized = property (lambda self : "-min" in self.fullPath)
    label = property (lambda self : self.__getLabel ())
    lenght = property (lambda self : self.__lenght)
         
    def __init__ (self, fullPath):
        self.fullPath = fullPath
        self.__contentType = None
    
    
    def __getExtension (self):
        try:
            return basename (self.__fullPath).rsplit (".", 1)[1]
        except IndexError:
            return ''
            
    def __setFullPath (self, value):
        self.__fullPath = value
        self.data = None
        
    def __setContentType (self, value):
        self.__contentType = value
    
    def __setData (self, data):
        self.__data = data
        if data:
            self.__lenght = len (data)
        else:
            self.__lenght = 0
    
    def __getLabel (self):
        label = basename (self.fullPath).replace ("-beta","").replace ("-min", "").replace ("-debug", "")
        return label
    
    def load (self):
        self.data = file (self.__fullPath).read ()

    def relocate (self):
        self.data = self.__remappingRE.sub ("\\1\\3\\4", self.data)
    
    def __repr__ (self):
        return "<YUIContent label=%s fullPath=%s>" % (self.label, self.fullPath)

    def __cmp__ (self, other):
        for comparator in self.__comparators:
            comparison = comparator (self, other)
            if comparison:
                "%s %s %s" % (self.fullPath, {1: ">", -1: "<"}[comparison], other.fullPath)
                return comparison
        assert (False)
        return 0

class YUICache (object):
    def __init__ (self, yuiDir):
        self.__yuiDir = join (yuiDir, "build")
        self.__locationCache = {}
        self.__contentFactory = YUIContentFactory ()
        self.__preload (skinName="sam")
    
    def __preload (self, skinName):
        directories = os.walk (self.__yuiDir)
        for directory, dirs, files in directories:
            if "/assets/" in directory and skinName not in directory:
                continue
            if "/examples/" in directory:
                continue
            if "/tests/" in directory:
                continue
            for filename in files:
                fullPath = os.path.join (directory, filename)
                content = self.__contentFactory.create (fullPath)
                if not content:
                    continue
                
                self.__registerContentInCache (content.label, content)
                relPath = dirname (fullPath.replace (self.__yuiDir, ""))
                assert (content.label != None)
                relName = join (relPath, content.label)
                origName = join (relPath, filename)
                self.__registerContentInCache (relName, content)
                self.__registerContentInCache (origName, content)
                self.__registerContentInCache (content.label.rsplit (".")[0], content)
    
    def __relocateData (self, data):
        return self.__remappingRE.sub ("\\1\\3\\4", data)
    
    def __registerContentInCache (self, ID, content):
        try:
            if self.__locationCache.has_key (ID) and self.__locationCache[ID] > content:
                return False
            content.load ()
            if content.contentType == "text/css":
                content.relocate ()
            self.__locationCache[ID] = content
            return True
        except IOError:
            return False
        return False
    
    def getContentByLabel (self, key):
        try:
            return self.__locationCache[key]
        except KeyError:
            return None 
    def size (self):
        return len (self.__locationCache)
    
    def iteritems (self):
        return self.__locationCache.iteritems ()
    