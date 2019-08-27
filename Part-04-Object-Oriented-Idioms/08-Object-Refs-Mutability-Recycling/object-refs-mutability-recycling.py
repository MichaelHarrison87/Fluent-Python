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