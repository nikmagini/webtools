from Framework import Context

class A (object):
    def __init__ (self, foo):
        self.__foo = foo
    def foo (self):
        return self.__foo
    
class B (object):
    def __init__ (self, foo):
        self.__foo = foo
    def foo (self):
        return self.__foo

class C (object):
    def __init__ (self, foo):
        self.__foo = foo
    def foo (self):
        return self.__foo


c1=Context ()
c2=Context (c1)
c1.addService (A ("Service A on C1"))
c2.addService (A ("Service A on C2"))
c1.addService (B ("Service B on C1"))
c2.addService (C ("Service C on C2"))

assert type (c1.A ()) == type (A (""))
assert type (c2.A ()) == type (A (""))
assert type (c1.B ()) == type (B (""))
assert type (c2.B ()) == type (B (""))
assert type (c2.C ()) == type (C (""))
assert type (c1.A ().foo()) == type (str())

assert c1.A ().foo () == "Service A on C1"
assert c2.A ().foo () == "Service A on C2"
assert c1.B ().foo () == "Service B on C1"
assert c2.B ().foo () == "Service B on C1"
assert c2.C ().foo () == "Service C on C2"
try:
    c1.C ().foo
    assert False
except AttributeError:
    pass
