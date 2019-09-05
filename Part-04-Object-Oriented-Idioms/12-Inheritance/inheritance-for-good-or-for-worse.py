# Chapter 12 - Inheritance: For Good or For Worse [p347]

# There is a problem in Python when subclassing built-in types (e.g. lists, dicts) - as the CPython 
# interpreter does not call special methods overridden by user-defined classes.
# For instance:
class DoppleDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value]*2)
    

print("\nDoppelDict:")      
dd = DoppleDict(a = 1)
dd['b']  = 2
dd.update(c = 3)
print(dd) # {'a': 1, 'b': [2, 2], 'c': 3}

# So the usual dictionary assignment patter d[key] = value uses the overriden __setitem__, however neither
# the built-in dict's constructor nor update method used it - these operate as for an ordinary dict.

# Note: typically in object-oriented code, methods should be searched for first in the child class - even in 
# methods inherited from the parent that use that method. So if dict's constructor used __setitem__, it should
# use the overriden version when that constructor is called by DoppelDict.

# We see similar with __getitem__:
class AnswerDict(dict):
    def __getitem__(self, key):
        return 10
    
print("\nAnswerDict:")    
ad = AnswerDict(a=1, b=2)
print(ad) # {'a': 1, 'b': 2}
print(ad['a']) # 10 - uses overriden __getitem__
print(ad['b']) # 10 - uses overriden __getitem__
print(ad) # {'a': 1, 'b': 2} - remains as it was constructed

d = {}
d2 = {'c': 3}
d.update(d2)
print(d) # {'c': 3} - update should "merge" two dictionaries

d.update(ad)
print(d) # {'c': 3, 'a': 1, 'b': 2}
print(d['a']) # 1 - uses __getitem__ from dict


# Instead the collections module has UserDict, UserList etc... which are intended to be overridden by the
# user, and work with overridden methods properly:
import collections

class DoppleDict_v2(collections.UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value]*2)
    
print("\nDoppelDict_v2:")    
dd = DoppleDict_v2(a = 1)
dd['b']  = 2
dd.update(c = 3)
print(dd) # {'a': [1, 1], 'b': [2, 2], 'c': [3, 3]}

# Now methods (update, and the constructor) of the parent UserDict use the overridden __setitem__ as expected

class AnswerDict_v2(collections.UserDict):
    def __getitem__(self, key):
        return 10
    
print("\nAnswerDict_v2:")    
ad = AnswerDict_v2(a=1, b=2)
print(ad) # {'a': 1, 'b': 2}
print(ad['a']) # 10 - uses overriden __getitem__
print(ad['b']) # 10 - uses overriden __getitem__
print(ad) # {'a': 1, 'b': 2} - remains as it was constructed

d = {}
d2 = {'c': 3}
d.update(d2)
print(d) # {'c': 3} - update should "merge" two dictionaries

d.update(ad)
print(d) # {'c': 3, 'a': 10, 'b': 10} - update uses overridden __getitem__
print(d['a']) # 10 - uses overridden __getitem__ 

# This issue with built-in types happens because they are implemented in C under the hood. Whereas 
# UserDict etc are implemented in Python, hence subclassing them works as expected.


# Multiple Inheritance and Method Resolution Order

# Multiple inheritance means subclasses can inherit from multiple parents. However there is a problem
# when there are competing methods with the same name in both parents - which to inherit from?
# For instance, consider the "diamond problem" below - where we have Class:Method pairs:
#
#        A:Ping
# B:Pong        C:Pong
#       D:Ping,Pong        

# So B & C inherit from A, while D inherits from both B and C - which version do we get if we call D.Ping()?

class A:
    def Ping():
        print("Ping")

class B(A):
    def Pong():
        print("Pong: B")

class C(A):
    def Pong():
        print("Pong: C")
    
class D(B,C):
    pass

print("\nTest Multiple Inheritance:")
A.Ping() # "Ping"

print("\n")
B.Ping() # "Ping"
B.Pong() # "Pong: B"

print("\n")
C.Ping() # "Ping"
C.Pong() # "Pong: C"

print("\n")
D.Ping() # "Ping"
D.Pong() # "Pong: B"

# D.Pong() calls B.Pong(), since B was first in the list of parent classes in the class D line.
# Instead putting C first instead calls C.Pong():
class D2(C, B):
    pass

print("\n")
D2.Ping() # "Ping"
D2.Pong() # "Pong: C"

# Although can call superclass methods directly but pass in the subclass as the instance:

class Sup_1:
    def honk(self):
        print("Honk 1: {}".format(self))
        

class Sup_2:
    def honk(self):
        print("Honk 2: {}".format(self))


class Sub(Sup_1, Sup_2):
    pass


sup_1_inst = Sup_1()
sup_1_inst.honk() # Honk 1: <__main__.Sup_1 object at 0x7ff6a03735f8>

sup_2_inst = Sup_2()
sup_2_inst.honk() # Honk 2: <__main__.Sup_2 object at 0x7ff6a03735c0>

sub_inst = Sub()
sub_inst.honk() #  Honk 1: <__main__.Sub object at 0x7f086f0425f8>

# So Sub inherits honk from Sup_1. But we can use Sub_2's honk as a class method, 
# and pass it our Sub instance in lieu of self:
Sup_2.honk(sub_inst) # Honk 2: <__main__.Sub object at 0x7f8e26d03630>

# The order in which methods are called is called the Method Resolution Order (MRO), and we can access it
# via the __mro__ property of the class:
print(Sub.__mro__) # (<class '__main__.Sub'>, <class '__main__.Sup_1'>, <class '__main__.Sup_2'>, <class 'object'>)

# Can also get it via the __class__ attribute of instances
print(sub_inst.__class__.__mro__) # (<class '__main__.Sub'>, <class '__main__.Sup_1'>, <class '__main__.Sup_2'>, <class 'object'>)

# So the MRO above is: self -> first parent in parent list -> second parent in parent list -> object

# Note __mro__ is a readonly attribute:
try:
    sub_inst_v2 = Sub()
    mro_list = list(sub_inst_v2.__class__.__mro__)
    mro_list[1] = Sup_2
    mro_list[2] = Sup_1
    sub_inst_v2.__class__.__mro__ = tuple(mro_list)
except Exception as e:
    print(repr(e)) # AttributeError('readonly attribute')

# super() is the usual way to ensure methods are inherited from their superclasses. Although can call
# methods from parent classes directly, to bypass the MRO:
class Sub_2(Sup_1, Sup_2):
    
    def krunk(self):
        super().honk() # inherited per the MRO
        print("krunk")
    
    def krank(self):
        Sup_2.honk(self)
        print("krank")
        
    def kronk(self):
        s2 = Sup_2()
        s2.honk()
        print("kronk")

sub_2_inst = Sub_2()

sub_2_inst.krunk()
# Honk 1: <__main__.Sub_2 object at 0x7f6708773860>
# krunk

sub_2_inst.krank()
# Honk 2: <__main__.Sub_2 object at 0x7f6708773860>
# krank

sub_2_inst.kronk()
# Honk 2: <__main__.Sup_2 object at 0x7fb91ee83908> - note this is a Sup_2 object
# kronk

# Note: we needed to provide self as an argument to Sup_2.honk() in krank, as it is an unbound method which otherwise
# was being called with no arguments.

# Whereas in kronk, we instantiated a Sup_2 instance, and so that was passed as the arg to honk() - hence the
# object print is a Sup_2 object vs Sub_2 object for krank