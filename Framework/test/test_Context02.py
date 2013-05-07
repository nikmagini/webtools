from Framework import Context

class A(object):
    """docstring for A"""
    def __init__(self, arg):
        self.arg = arg
        
class B(object):
    """docstring for B"""
    def __init__(self, arg):
        self.arg = arg
        

c1=Context ()
c2=Context (c1)
c3=Context (c1)
c1.addService (A("Foo"))
assert c2.A ().arg == "Foo"
c2.addService (A("Bar"))
c2.addService (B("Bar"))
assert c1.A ().arg == "Foo"
assert c2.A ().arg == "Bar"
assert c3.A ().arg == "Foo"
c4=Context (c2)
assert c4.A ().arg == "Bar"