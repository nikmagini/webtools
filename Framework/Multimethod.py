g_multimethodRegistry = {}

class MultiMethodException (Exception):
    pass
    
class MultiMethodNoMatch (MultiMethodException):
    pass

# This is the maximum number of arguments that a multimethod can have.
D_MAX_NUMBER_OF_MM_ARGS = 16

def sortByDistance (a, b):
    dA, fA = a
    dB, fB = b
    return dA - dB

class MultiMethod (object):
    def __init__ (self):
        self.__name = None
        # Creates the registry with all the possible multimethod functions
        self.registry = []
        # Creates the score vectors per argument position.
        self.scores = []
        for i in range (0,D_MAX_NUMBER_OF_MM_ARGS):
            self.scores.append ({})
            self.registry.append ({})
        
    def register (self, argType, pos, function):
        if not self.__name:
            self.__name = function.__name__
        # Let's make sure the function is called as the multimethod.
        # If this is not the case, then something went bogus.
        assert self.__name == function.__name__
        if not self.registry[pos].has_key (argType):
            self.registry[pos][argType] = []
        self.registry[pos][argType].append (function)
        print "Registering function %s as exact match for class %s at position %s" % (function,
                                                                                      argType,
                                                                                      pos)
        
    def __call__ (self, *args):
        assert len (args) < len (self.scores)        
        # Build the score vectors
        pos = 0
        for arg in args:
            argType = arg.__class__    
            print "Analyzing argument of type %s in position %s" % (argType, pos)
            if not self.scores[pos].has_key (argType):
                print "First time we call multimethod %s" % self.__name
                self.scores[pos][argType] = []
                distance = 0
                # For every class in the inheritance chain, register a function and it's
                # distance in the scores table.
                targetType = argType
                while argType:
                    if argType in self.registry[pos].keys ():
                        for fn in self.registry[pos][argType]:
                            print "Score for %s with %s in position #%s: %s" % (fn.__signature__, argType, pos, distance)
                            self.scores[pos][targetType].append ((distance, fn))
                    # FIXME: does not support multiple parents!
                    distance = distance + 1 
                    argType = argType.__base__
            for argType in self.scores[pos].keys ():
                self.scores[pos][argType].sort (cmp=sortByDistance)
                print self.scores[pos][argType]
            pos += 1
            
        pos = 0        
        for distance, function in self.scores[0][args[0].__class__]:
            print "Intial candidate %s with distance %s from %s " % (function.__signature__, distance, args[0].__class__) 
            for pos in range (1, len (args)):
                isWorse=False
                className = args[pos].__class__
                print "Checking candidates for %s at position %s" % (className, pos)
                bestDistance, someBestFunction = self.scores[pos][className][0]
                print "Best distance for this argument: %s" % bestDistance
                for newDistance, newFunction in self.scores[pos][className]:
                    print "Checking candidate: %s with score: %s" % (newFunction.__signature__, newDistance)
                    if newDistance > bestDistance:
                        print "%s is worse in position %s" % (newFunction.__signature__, pos)
                        isWorse = True
                        break
                    if newFunction == function:
                        print "Candidate function found %s." % newFunction.__signature__
                        isWorse = False
                        if pos == len (args)-1:
                            return function (*args)
                        break
                    isWorse=True
                if isWorse:
                    break
        assert False and "Nothing found"


def multimethod (*args):
    def decorator (function):
        # Gets the multimethod name
        if not g_multimethodRegistry.has_key (function.__name__):
            g_multimethodRegistry[function.__name__] = mm = MultiMethod ()
        else:
            mm = g_multimethodRegistry[function.__name__]
        
        # Registers the argument types in the function
        pos = 0
        argLabel = ""    
        for arg in args:
            argLabel += "%s_" % arg
            mm.register (arg, pos, function)
            pos = pos + 1
        function.__signature__ = argLabel
        
        def wrapper (*__args):
            return mm (*__args)
        return wrapper
    return decorator
