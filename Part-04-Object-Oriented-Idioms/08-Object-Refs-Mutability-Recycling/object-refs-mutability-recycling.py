# Chapter 8 - Object References, Mutability, Recycling [p219]

# In Python, objects and their names are distinct - variables are labels, not boxes.
# So when we assign variables, we're merely assigning the /label/ rather than the contents of the box.
# Hence the below:
a = [1,2,3]
b = a
a.append(4)
print(b) # [1, 2, 3, 4] - b is just an alternative label for the box, so changes when the boxs' contents change

# cf:
c = a.copy()
a.append(5)
print(b) # [1, 2, 3, 4, 5]
print(c) # [1, 2, 3, 4] - whereas c is label of a new copy of the box to which a and b refer

# The object on the right-hand-side of the assignment is always created first, before the variable label is assigned to it

class Gizmo:
    
    def __init__(self):
        print("Instance id: {}".format(id(self)))
        
g1 = Gizmo() # Instance id: 139753138106264

try:
    g2 = Gizmo() * 10 # Instance id: 139753138167936 - Gizmo is instantiated, before the Exception occurs
except Exception as e:
    print(type(e), e) # <class 'TypeError'> unsupported operand type(s) for *: 'Gizmo' and 'int'

print(g1) # <__main__.Gizmo object at 0x7fbce3d32f98>

try:
    print(g2)
except Exception as e:
    print(type(e), e) # <class 'NameError'> name 'g2' is not defined

# So Gizmo was instantiated, but g2 was never assigned (and hence doesn't exist) before the Exception occured


# Identity, Equality, Aliasing [p221]
charles = {"name": "Charles", "born": 1832}
lewis = charles
print(charles is lewis) # True
print(id(charles), id(lewis), id(charles) == id(lewis)) # 139671702041080 139671702041080 True

# charles and lewis label the same underlying object in memory. "is" checks for this - by checking equality of the underlying id

# Modifying either, changes the other:
lewis["balance"] = 950
print("lewis:", lewis) # lewis: {'name': 'Charles', 'born': 1832, 'balance': 950}
print("charles:", charles) # charles: {'name': 'Charles', 'born': 1832, 'balance': 950}

# But creating a new object with the same contents creates a fresh copy of this content in a new place in 
# memory - hence "is" returns False:
alex = {'name': 'Charles', 'born': 1832, 'balance': 950}
print(alex is lewis) # False
print(alex is charles) # False
print(id(alex), id(charles), id(alex) == id(charles)) # 140093124276872 140093124276728 False
print(alex is not charles) # True

# However, since the /content/ is the same, an equality test with "==" remains True:
print(alex == charles) # True
print(alex == lewis) # True

# Charles and lewis are aliases - two variables assigned to the same underlying object

# Note that an object's identity does not change once it has been created, although its value(s) might:
l = [1,2,3]
id_l_1 = id(l)
print(l)

# add item
l.append(4) # add item
id_l_2 = id(l)
print(l)
print("add item:", id_l_1, id_l_2, id_l_1 == id_l_2)

# remove item
l.pop()
id_l_3 = id(l)
print(l)
print("remove item:", id_l_1, id_l_3, id_l_1 == id_l_3)

# edit item
l[0] = 6
id_l_4 = id(l)
print(l)
print("edit item:", id_l_1, id_l_4, id_l_1 == id_l_4)
print(all([id_l_1 == id_l_2, id_l_1 == id_l_3, id_l_1 == id_l_4]))

# In CPython, id() returns the memory address of the object.

# "is" is faster than "==", as it doesn't need to find and invoke a special method. By contrast, "==" is just syntactic
# sugar for callling the object's __eq__() method. This method for the base object class actually does simple compare 
# objects' id's - although most built-in classes override that with the own equality check that compares values instead.
# Testing for equality can be expensive though, e.g. on large collections, or deeply-nested ones.

# This distinction between equality and identity can lead to some edge-case weirdness if storing mutable objects
# inside immutable ones - e.g. a list inside a tuple - that renders the immutable object not /that/ immutable:
t1 = (1, 2, [3,4])
t2 = (1, 2, [3,4])
id_t1_1 = id(t1) 
id_t2_1 = id(t2) 
print(id_t1_1, id_t2_1, id_t1_1 == id_t2_1) # 139749937038608 139749937039040 False
print(t1 == t2) # True

# But we can modify the list inside the tuple:
id_list_1 = id(t1[-1])
print(id_list_1) # 139741476050440
t1[-1].append(5)
print(t1) # (1, 2, [3, 4, 5]) - t1 has been modified
id_list_2 = id(t1[-1])
print(id_list_1, id_list_2, id_list_1 == id_list_2) # 139897021220680 139897021220680 True
# So the list in the last spot in t1 is still the same object - at the same place in memory

id_t1_2 = id(t1) 
print(id_t1_1, id_t1_2, id_t1_1 == id_t1_2) # 139980681692432 139980681692432 True
# And t1 remains at the same position in memory - has the same identity - 
# but of course an equality test with t2 now fails:
print(t1 == t2) # False

# Note: this makes tuples containing mutable objects unhashable:
try:
    print(hash(t1))
except Exception as e:
    print(type(e), e) # <class 'TypeError'> unhashable type: 'list'

# Whereas a tuple containing immutable objects is hashable:
print(hash((1,2,3)))
print(hash(("a", "b", "c")))

# This issue also affects copies - should a copy duplicate all inner objects (e.g. nested lists), or can it share them?
# Using the constructor (e.g. list()) or [:] to create a copy, creates only a shallow copy - duplicating the outermose
# container, but copying only references to the inner objects. The same is true of the copy method. 
l1 = [1, [2, 3], (4, 5, 6)]
l2 = list(l1) # creates a copy
l3 = l1.copy()

print("\nCompare l1 vs l2")
print(l1 == l2) # True
print(l1 is l2) # False

print("\nCompare l1 vs l3")
print(l1 == l3) # True
print(l1 is l3) # False

# Check inner list
print("\nCheck inner list")
print(l1[1] == l2[1]) # True
print(l1[1] is l2[1]) # True 

print(l1[1] == l3[1]) # True
print(l1[1] is l3[1]) # True 

# Check inner tuple
print("\nCheck inner tuple")
print(l1[2] == l2[2]) # True
print(l1[2] is l2[2]) # True 

print(l1[2] == l3[2]) # True
print(l1[2] is l3[2]) # True 

# Modify inner list:
l1[1].append(7)
print("\nCheck modified inner lists:")
print(l1) # [1, [2, 3, 7], (4, 5, 6)]
print(l2) # [1, [2, 3, 7], (4, 5, 6)]
print(l3) # [1, [2, 3, 7], (4, 5, 6)]

# But of course, modifying the outer list doesn't change the copies:
l1.append(8)
l2.append([8,9])
print("\nCheck modified outer lists:")
print(l1) # [1, [2, 3, 7], (4, 5, 6), 8]
print(l2) # [1, [2, 3, 7], (4, 5, 6), [8, 9]]
print(l3) # [1, [2, 3, 7], (4, 5, 6)]

# Also note, we can modify the inner tuple. But since this is not done in-place (instead, destroys and re-creates the object
# in memory), it doesn't affect the other lists:
l1[2] += (9, 10) # not an in-place operation (whereas would be with lists vs tuples), as tuples are immutable
print("\nCheck modified inner tuples:")
print(l1) # [1, [2, 3, 7], (4, 5, 6, 9, 10), 8]
print(l2) # [1, [2, 3, 7], (4, 5, 6), [8, 9]]
print(l3) # [1, [2, 3, 7], (4, 5, 6)]

l1[1] += [11, 12]
print("\nInner list in-place +:")
print(l1) # [1, [2, 3, 7, 11, 12], (4, 5, 6, 9, 10), 8]
print(l2) # [1, [2, 3, 7, 11, 12], (4, 5, 6), [8, 9]]
print(l3) # [1, [2, 3, 7, 11, 12], (4, 5, 6)]

# The copy module provides functions deepcopy and copy to provide deep and shallow (resp) copying of arbitrary objects
# deepcopy copies all inner elements to fresh locations in memory
import copy

l4 = copy.copy(l1)
l5 = copy.deepcopy(l1)

print("\nCheck copy module copies")
print(l1)
print(l4)
print(l5)

print(l1 == l4) # True
print(l1 == l5) # True

print(l1 is l4) # False
print(l1 is l5) # False

print("\nCheck inner list equality:")
print(l1[1] == l4[1]) # True
print(l1[1] == l5[1]) # True

print("\nCheck inner list identity:")
print(l1[1] is l4[1]) # True
print(l1[1] is l5[1]) # False

print("\nModify inner list:")
l4[1].append(13)
print(l1)
print(l4)
print(l5)
print(l1 == l5, l4 == l5, l1 == l4) # False False True


# The copy() and deepcopy() functions from the copy module work on arbitrary objects, e.g. Classes, as below:
class Bus:
    
    def __init__(self, passengers = None):
        if passengers is None:
            self.passengers = []
        else:
            self.passengers = list(passengers)
    
    def pickup(self, name):
        self.passengers.append(name)
    
    def dropoff(self, name):
        self.passengers.remove(name)

bus1 = Bus(["A", "B", "C"])
bus2 = copy.copy(bus1)
bus3 = copy.deepcopy(bus1)

print("\nCompare buses' identity")
print(bus1 is bus2, bus1 is bus3, bus2 is bus3) # False False False

# Each instance is indeed a separate object in memory. However, the shallow-copy version did not copy the attributes of bus1
# whereas the deepcopy did:
bus1.passengers.remove("C")
print("\nCompare passengers:")
print(bus1.passengers) # ['A', 'B']
print(bus2.passengers) # ['A', 'B']
print(bus3.passengers) # ['A', 'B', 'C']
print(bus1.passengers is bus2.passengers, bus1.passengers is bus3.passengers) # True False


# Note that deepcopy can be tricky - e.g. with cyclic references, could get into an infinite loop.
# Consider:
a = [1, 2]
b = [a, 3]
print(a) # [1, 2]
print(b) # [[1, 2], 3]
print(a is b[0]) # True

# Now append b to a - this creates an infinite chain of nested lists (note the self-similarity)
a.append(b)
print("\na is self-similar:")
print(a, ";",len(a)) # [1, 2, [[...], 3]] ; 3
print(a[2], ";", len(a[2])) # [[1, 2, [...]], 3] ; 2
print(a[2][0], ";",len(a[2][0])) # [1, 2, [[...], 3]] ; 3
print(a[2][0][2], ";",len(a[2][0][2])) # [[1, 2, [...]], 3] ; 2

# The is list inifitely-deep, e.g. pick some arbitrary depth:
print(a[2][0][2][0][2][0][2][0][2][0][2][0] is a) # True
print(a[2][0][2][0][2][0][2][0][2][0][2] is a) # False
print(a[2][0][2][0][2][0][2][0][2][0][2] is b) # True

# Shallow copy only copies the inner list:
c = copy.copy(a)
print("\nCheck shallow copy:")
print(c) # [1, 2, [[1, 2, [...]], 3]]
print(a is c)  # False
print(a[2] is c[2]) # True
print(c[2][0][2][0][2][0][2][0][2][0][2][0] is a) # True
print(c[2][0][2][0][2][0][2][0][2][0][2][0] is a[2][0][2][0]) # True
print(c[2][0][2][0][2][0][2][0][2][0][2][0] is c[2][0][2][0]) # True - note comparing c to itself

# deepcopy copies all inner items into separate locations in memory
c = copy.deepcopy(a)
print("\nCheck deep copy:")
print(c) # [1, 2, [[1, 2, [...]], 3]]
print(a is c)  # False
print(a[2] is c[2]) # False
print(c[2][0][2][0][2][0][2][0][2][0][2][0] is a) # False
print(c[2][0][2][0][2][0][2][0][2][0][2][0] is a[2][0][2][0]) # False
print(c[2][0][2][0][2][0][2][0][2][0][2][0] is c[2][0][2][0]) # True - comparing c to itself, so True makes sense here

# deepcopy'ing to extreme depth may not always be desired - e.g. if refering to external resources, or singletons that 
# should not be copies. 
# Can control copy behaviour through the __copy__ and __deepcopy__ special methods


# For function arguments, Python uses "call by sharing" - each formal parameters gets a copy of each reference in the
# arguments. Essentially, the parameters in the function are aliases of the actual arguments

# So, can pass mutable objects as parameters (and change them), but cannot change their identity
def f(a, b):
    print(id(a))
    a += b
    print(id(a))
    return a

print("\nTest function args:")
print(f(1,2)) # 3

print("\nTest function args - list:")
l1 = [1,2]
l2 = [3,4]
print(id(l1)) # 140240386207624
print(f(l1, l2)) # [1, 2, 3, 4]
print(l1) # [1, 2, 3, 4] - l1 modified
print(id(l1)) # 140240386207624
# id's within the function:
# 140240386207624
# 140240386207624


print("\nTest function args - tuple:")
t1 = (1,2)
t2 = (3,4)
print(id(t1)) # 140575136337672
print(f(t1, t2)) # (1, 2, 3, 4)
print(t1) # (1, 2) - t1 not modified, as the += within the function was not in-scope
print(id(t1)) # 140575136337672 - unchanged
# id's within the function:
# 140575136337672 - same as t1 before +=
# 140575118390120 - different from t1, after the += modification; this object only lived in the scope of the function and can't be accessed after calling


# However this means mutable objects are not a good idea for default argument values 
# E.g. in Bus above, passengers default was None, and we then created an empty list within the function
# cf below, which uses an empty list as the default value:
class HauntedBus:
    
    def __init__(self, passengers = []):
        self.passengers = passengers # self.passengers is an alias for passengers, itself an alias for the empty list
    
    def pickup(self, name):
        self.passengers.append(name)
    
    def dropoff(self, name):
        self.passengers.remove(name)
        
print("\nTest HauntedBus:")
bus1 = HauntedBus(["A", "B"])
print(bus1.passengers) # ['A', 'B']
bus1.pickup("C")
bus1.dropoff("A")
print(bus1.passengers) # ['B', 'C']

print("\nBus2:")
bus2 = HauntedBus()
print(bus2.passengers) # []
bus2.pickup("D")
print(bus2.passengers) # ['D']

print("\nBus3:")
bus3 = HauntedBus()
print(bus3.passengers) # ['D']

print("\nBus2:")
bus3.pickup("E")
print(bus2.passengers) # ['D', 'E']

print("\nBus3:")
bus2.dropoff("D")
print(bus3.passengers) # ['E']

print(bus2.passengers is bus3.passengers) # True

# So bus2.passengers and bus3.passengers are both aliases to the same object in memory - the empty list originally 
# created when bus2 was instantiated. Hence modifying it with one instance changes it for the other instance.
# Note: the default value is created when the function is evaluated - here, when bus2 is instantiated, but for
# modules, this will be when they are loaded.
# This, again, is why None was used above - to circumvent this

print(HauntedBus.__init__.__defaults__) # (['E'],)
print(HauntedBus.__init__.__defaults__[0] is bus2.passengers) # True

# Defensive programming with mutable params: when working with functions with mutable parameters, need to consider whether
# any potential changes made to it within the function should carry-over outside the function as well.

# For instance, the class below mutates the arguments its provided with:
class TwilightBus:
    
    def __init__(self, passengers = None):
        if passengers is None:
            self.passengers = []
        else:
            self.passengers = passengers # cf: Bus above, where we copied passengers via self.passengers = list(passengers)
    
    def pickup(self, name):
        self.passengers.append(name)
    
    def dropoff(self, name):
        self.passengers.remove(name)

team = ["A", "B", "C"]
team_bus = TwilightBus(team)
team_bus.dropoff("A")
team_bus.dropoff("B")
print(team) # ['C']
print(team is team_bus.passengers) # True


# In Python, objects are never explicitly destroyed. However, when they become unreachable, then they may be garbage collected.
 
# As such del deletes name, not objects:
l = [1,2,3]
m = l
print(l is m) # True

del l
print(m) # [1, 2, 3]

try:
    print(l)
except Exception as e:
    print(type(e), e) # <class 'NameError'> name 'l' is not defined
    
# An object that is del'd is garbage collected only if that removes the last reference to that object, or
# if the object is unreachable (e.g. circular references as above).
# An object may be garbage collected if its last label is reassigned, e.g. the list [1,2,3] below:
l = [1,2,3]
l = [4,5,6]

# weakref.finalize gives us a callback to register when an object has been destroyed
print("\nTest weakref.finalize")
from weakref import finalize

s1 = {1,2,3}
s2 = s1

def bye():
    print("Goodbye...")

ender = finalize(s1, bye)
print(ender.alive) # True
# If the code ends at this point, then run, "Goodbye..." is printed after True above. 
# Since s1 is destroyed as the script's run ends.

del s1
print(ender.alive) # True
s2 = {1}
# prints "Goodbye..." now since the original set is no-longer reachable, and hence was destroyed
print(ender.alive) # False

# Note that the reference to s1 made when creating the finalize function doesn't keep the original set alive,
# since this was a "weak reference". These are references to objects that do not increase their reference count
# under the hood. Hence the weak reference doesn't prevent the object from being garbage collected. 

# This can be useful, e.g., in a cache, where don't want to keep the object alive simply due to it being referenced in a cache.

# In Python, weakref's are a callable that returns the referenced object, or None if it no longer exists:
import weakref

a_set ={0,1}
wref = weakref.ref(a_set)
print(wref) # <weakref at 0x7fd073d4b6d8; to 'set' at 0x7fd073da1ac8>
print(wref()) # {0, 1}

a_set = {1,2}
print(wref()) # None
print(wref) # <weakref at 0x7f3f89c4b6d8; dead>
print(wref() is None) # True

# Note: the code gives different results if ran in a Python console session - the second call to wref() still returns {0,1}
# if invoked immediate after changing a_set - since the console uses "_" to refer to the most recent object, which keeps
# the reference to the original set alive

# The weakref package includes various weak-reference data structures (collections), e.g. WeakKeyDictionary (entry removed if the
#  key is destroyed), WeakValueDictionary (same, but for values), WeakSet.
# These are useful for creating caches. E.g. the Cheese cache below:

class Cheese:
    
    def __init__(self, kind):
        self.kind = kind
    
    def __repr__(self):
        return "Cheese({})".format(self.kind)
    

stock = weakref.WeakValueDictionary()
catalog = [Cheese("A"), Cheese("B"), Cheese("C")]
for cheese in catalog:
    stock[cheese.kind] = cheese
print(stock.keys())
for i in stock.items():
    print(i)
print(stock["A"]) #  Cheese(A)

# Now deleting the catalog /should/ leave stock empty
print("\ndel catalog:")
del catalog
for i in stock.items():
    print(i)
# But the above unexpected prints ('C', Cheese(C))

# This is due to "cheese" variable (from the iteration over catalog) holds on to the reference to the last object in catalog
# hence, it is still present in stock.
# So removing that variable leaves stock empty as expected:
print("\ndel cheese:")
del cheese
del i # need to remove this, due to the iteration above
for i in stock.items():
    print(i)
# The above now prints nothing - stock is empty


# A use-case for WeakSet might be for a class to hold referneces to all instances of itself - using a regular set,
# these instances would never be garbage collected, since the class iteself would continue to hold references to them.

# Note that base lists and dicts can't be weakly-referenced
l = [1,2,3]
try:
    wref = weakref.ref(l)
except Exception as e:
    print(type(e), e) # <class 'TypeError'> cannot create weak reference to 'list' object
    

d = {"a": 1, "b": 2}
try:
    wref = weakref.ref(d)
except Exception as e:
    print(type(e), e) # <class 'TypeError'> cannot create weak reference to 'dict' object
    

# However, simply creating a base subclass that does nothing can circumvent this:
class MyList(list):
     pass
 
l = MyList([1,2,3])
print(l) # [1, 2, 3]

wref = weakref.ref(l)
print(wref) # <weakref at 0x7f6ea128d908; to 'MyList' at 0x7f6ea128d8b8>
print(wref()) # [1, 2, 3]

# Now reassign l, the weakref dies:
l = [1,2,3]
print(wref) # <weakref at 0x7f1b7534d908; dead>
print(wref()) # None

# Sets can be weakly referenced, however tuples and int can't (an nor can their subclasses).
# Note this is due to limitations of the CPython interpreter


# Note that for certain string literals and small integers, all references to them refer to the same underlying objects - this is 
# called "interning". E.g:
s1 = "abc"
s2 = "abc"
print(s1 is s2) # True

i1 = 5
i2 = 5
print(i1 is i2) # True
