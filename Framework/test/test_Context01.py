from Framework import Context

class Component (object):
    def foo (self):
        return "A component"
        
c = Context ()
c.addService (Component ())
assert c.Component ().foo () == "A component"