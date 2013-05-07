from Framework import Context

class A:
    def __init__ (self, arg):
        self.__arg = arg
    def arg (self):
        return self.__arg

mainContext = Context ()
mainContext.addService (A (0))
context = {}

for i in range (1, 3):
    context[i] = Context (mainContext)
    context[i].addService (A (i))

for i in range (1, 3):
    assert context[i].A ().arg () != 0 
    assert context[i].A ().arg () == i