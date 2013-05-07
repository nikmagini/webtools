class ContextExeption (Exception):
    def __init__ (self):
        Exception.__init__ (self, "Circular dependencies among states")

class Context (object):
    """ A shared application state.
    
     Context is a collection of #Service objects shared among various clients, representing an
    application state. The general idea is that Context does not know about specific items that
    need to be shared among the clients, but the clients know how to look up specific extensions
    in the context. Context is merely a means up keeping the application context data together in
    a way that clients do not need to care about its origin.
    
     State Context objects can be chained in a tree-like structure. This allows an #Service
    setting in the child to override the definition in the parent, or to be scoped purely into the
    child. Services that cannot be found in the child are looked up in the parent until a
    definition is found or the context tree root is reached. Services can be introduced anywhere
    on the path, which can be used to give them appropriate scope.
    
     The idea behind Context is that application parts that need to access the shared state have a
    context in which they look up the state-related services: the Context is the environment in
    which the object runs in. The context hierarchy allows the visibility of the services to be
    scoped to the appropriate level. Do not overuse the Context; while it is a simple and powerful
    concept, it is not always the best fit. Applications have many object hierarchies that are not
    isomorphic, trying to hammer them all to match Context is not a good idea. Use Context mainly
    for its intended purpose: as the environment in which application objects can locate the
    shared state. """
    def __init__ (self, parent=None):
        self.__parent = parent
        self.__serviceNames = []
        self.__children = []
        if self.__parent:
            self.__parent.addChild (self)
        
    def addService (self, service):
        name = service.__class__.__name__
        self.__serviceNames.append (name)
        accessor = lambda : service
        setattr (self, name, accessor)
        self.__rewireChildren (self, name)
    
    def removeService (self, name):
        # TODO: remove by class or by object.
        # FIXME: needs to propagate parent services.
        if name in self.__serviceNames:
            delattr (self, name)
            self.__rewireChildren (self, name)
    
    def addChild (self, child):
        self.__children.append (child)
        child.__rewire (None)
        
    def __rewireChildren (self, original, name):
        for child in self.__children:
            if child == original:
                raise ContextException ()
            child.__rewire (name)
            child.__rewireChildren (original, name)
            
    def __rewire (self, name):
        if name in self.__parent.__serviceNames:
            accessor = getattr (self.__parent, name)
            setattr (self, name, accessor)
        elif name == None:
            for name in self.__parent.__serviceNames:
                accessor = getattr (self.__parent, name)
                setattr (self, name, accessor)                
                
    def __raiseException (self, name):
        raise AttributeError (name)