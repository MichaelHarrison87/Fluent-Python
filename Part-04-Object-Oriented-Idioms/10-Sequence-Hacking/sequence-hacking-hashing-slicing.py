# Chapter 10 - Sequence Hacking, Hashing, Slicing [p275]

# This chapter creates a multidimensional Vector class that allows for arbitrary dimensionality.

# We could use *args to allow for an arbitrary number of dimensions in the constructor 
# (i.e. __init__), a la Vecto2D(x, y) from Chapter 9. 
# 
# However best-practice for a sequence constructor is to take the data in as an iterable argument - which
# is what all built-in types do. E.g. Should be able to construct it using a list, tuple, range() etc...

from array import array
import reprlib
import math

class Vector_v1:
    typecode = "d"
    
    def __init__(self, components):
        self._components = array(self.typecode, components)
        
    def __iter__(self):
        return iter(self._components)
    
    def __repr__(self):
        """Note: we use reprlib to print "..." for very long sequences, rather than 
        printing out the whole sequence (for presentation convenience). Called a limited-length
        representation.
        
        In addtion, the representation of arrays is like:
        "array('d', [1.0, 2.0, 3.0])"
        So we search inside this to extract the underlying components - and strip out "array("d" and
        the closing ")" etc..
        """
        components = reprlib.repr(self._components)
        components = components[components.find("["):-1] # extract components
        return "Vector({})".format(components)
    
    def __str__(self):
        return str(tuple(self))
    
    def __bytes__(self):
        return (bytes([ord(self.typecode)])) + bytes(self._components)
    
    def __eq__(self, other):
        return tuple(self) == tuple(other)
    
    def __abs__(self):
        return math.sqrt(sum(x**2 for x in self))
    
    def __bool__(self):
        return bool(abs(self))
    
    # Alternative constructor
    @classmethod
    def from_bytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)
    
# List constructor
print(Vector_v1([3.1, 4.2])) # (3.1, 4.2)
print(repr(Vector_v1([3.1, 4.2]))) # Vector([3.1, 4.2])

# Tuple constructor
print(Vector_v1((1.5, 2.2, 3.8))) # (1.5, 2.2, 3.8)

# Try incompatible type:
try:
    print(Vector_v1([1, 2, "a"]))
except Exception as e:
    print(repr(e)) # TypeError('must be real number, not str')

# Range constructor
print(Vector_v1(range(3,6))) # (3.0, 4.0, 5.0)

# Test other methods
v1 = Vector_v1([1,1,1]) # 
print(abs(v1), math.sqrt(3)) # 1.7320508075688772 1.7320508075688772 - i.e. (1,1,1) is length sqrt(3) as expected
print(v1 == Vector_v1((1,1,1))) # True
print(v1 == Vector_v1(range(4))) # False
print(bool(v1)) # True

for comp in v1:
    print(comp)
# prints:
# 1.0
# 1.0
# 1.0

print(bytes(v1)) # b'd\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf0?'

v1_alt = Vector_v1.from_bytes(b'd\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf0?')
print(v1_alt) # (1.0, 1.0, 1.0)
print(v1 == v1_alt) # True

# Demo the length clipping in repr:
print(Vector_v1(range(10))) # (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)
print(repr(Vector_v1(range(10)))) # Vector([0.0, 1.0, 2.0, 3.0, 4.0, ...])

# Protocols and Duck Typing

# Note: don't need to inherit from any class to create a sequence object - simply need to implement
# the required methods that fulfill the sequence protocal. Specifically, for Python, __len__ and
# __getitem__. Any class satisfying this can then be used anywhere a sequence is expected.

# So we can see that a class is a sequence due to the way it behaves, regardless of what it may be a subtype of.
# This is called duck typing - just need to satisfy a protocol (set of behaviours) to be treated as equiv to a type.

# Note: Vector above doesn't implement __len__ or __getitem__, so is not a sequence. 
# We can't get its len:
try:
    print(len(v1))
except Exception as e:
    print(repr(e)) # TypeError("object of type 'Vector_v1' has no len()")


# Nor unpack it:
try:
    x1, y1 = v1
except Exception as e:
    print(repr(e)) # ValueError('too many values to unpack (expected 2)')

# Nor get items via index:
try:
    x1 = v1[0]
except Exception as e:
    print(repr(e)) # TypeError("'Vector_v1' object is not subscriptable")
    
# So we create Vector v2 which implements these:
class Vector_v2(Vector_v1):
    
    def __len__(self):
        return len(self._components)
    
    def __getitem__(self, index):
        return self._components[index]

print("\nVector v2")
v2 = Vector_v2([3,4])
print(v2, len(v2)) # (3.0, 4.0) 2
x2, y2 = v2
print(x2, y2) # 3.0 4.0
print(v2[0], v2[1]) # 3.0 4.0
print(Vector_v2(range(11))[-1]) # 10.0

# And we can even slice:
print(Vector_v2(range(11))[3:7]) # array('d', [3.0, 4.0, 5.0, 6.0])

# Albeit we'd probably rather return a new Vector instance, than an array.

# We can examine how slicing works through __getitem__ with a simple example:

class MySeq:
    def __getitem__(self, index):
        return index
    
my_seq = MySeq()
print(my_seq[0]) # 0
print(my_seq[:3]) # slice(None, 3, None)
print(my_seq[3:]) # slice(3, None, None)
print(my_seq[3:7]) # slice(3, 7, None)
print(my_seq[3:7:2]) # slice(3, 7, 2) - step size 2
print(my_seq[1:3, 6:9]) # (slice(1, 3, None), slice(6, 9, None)) - a tuple of slices

# So under the hood we have a slice object, with args start, stop and step. We can actually use this directly
l = list(range(10))
print(l[slice(1, 9)]) # [1, 2, 3, 4, 5, 6, 7, 8]
print(l[slice(None, 5, 2)]) # [0, 2, 4]
print(l[slice(5, None, 3)]) # [5, 8]

# Examining the slice object itself:
print(slice) # <class 'slice'>
print(dir(slice))

# slices have a .indice(len) property that normalises the range of indices returned by the slice, 
# governed by its len argument 

# E.g. if slice is longer than the sequence:
print(l[5:20]) # [5, 6, 7, 8, 9] - excess range ignored
print(slice(5, 20, None).indices(10)) # (5, 10, 1) - returns the tuple (start, stop, step); but the stop provided is truncated based on the length in indices 

# indices also resolves negative indices:
print(l[-3:]) # [7, 8, 9]
print(l[slice(-3, None, None)]) # [7, 8, 9] - equiv to above
print(slice(-3, None, None).indices(10)) # (7, 10, 1) - indices calculates the (start, stop, step) equiv in positive indices
print(l[slice(7, 10, 1)]) # [7, 8, 9] - equiv to above


# We can implement a slice-aware __getitem__ that returns another Vector instance when sliced:
import numbers

class Vector_v3(Vector_v1): 
    
    def __len__(self):
        return len(self._components)
    
    def __getitem__(self, index):
        cls = type(self)
        
        if isinstance(index, slice):
            return cls(self._components[index])
        
        elif isinstance(index, numbers.Integral):
            return self._components[index]
        
        else:
            msg = '{cls.__name__} indices must be integers'
            raise TypeError(msg.format(cls=cls))    
            
            
v3 = Vector_v3(range(5))
print(v3) # (0.0, 1.0, 2.0, 3.0, 4.0)
print(v3[1:4]) # (1.0, 2.0, 3.0)
print(type(v3[1:4])) # <class '__main__.Vector_v3'>
print(v3[0]) # 0.0
x3, y3, *rest = v3
print(x3, y3) # 0.0 1.0
print(rest, type(rest)) # [2.0, 3.0, 4.0] <class 'list'>
print(list(v3)) # [0.0, 1.0, 2.0, 3.0, 4.0]

try:
    print(v3[1.5])
except Exception as e:
    print(repr(e)) # TypeError('Vector_v3 indices must be integers')
    
print(v3[::-1], type(v3[::-1])) # (4.0, 3.0, 2.0, 1.0, 0.0) <class '__main__.Vector_v3'>

# But doesn't support multiple slices:
try:
    print(v3[1:3, 4:])
except Exception as e:
    print(repr(e)) # TypeError('Vector_v3 indices must be integers')
 
# Since our Vector is created from an iterable, we can't access components by name (e.g. v.x, v.y) as in the
# Vector2D class from last chapter.

# We /could/ create @property-decorated methods for each of the various components to allow this, but 
# it's cumbersome
# Instead, the __getattr__ can be used - it is called by the interpreter when attribute lookup fails (i.e. 
# the object does not have the desired attribute). The __getattr__ method is then called with the name of the
# attribute as a string, as its argument (after self, of course).

class Vector_v4(Vector_v3):
    shortcut_names = 'xyzt'
    
    def __getattr__(self, name):
        cls = type(self)
        
        if len(name) == 1:
            pos = cls.shortcut_names.find(name)
            
            if 0 <= pos < len(self._components):
                return self._components[pos]
        
        msg = '{.__name__!r} object has no attribute {!r}'
        raise AttributeError(msg.format(cls, name))
    
v4 = Vector_v4(range(10))
print(v4.x) # 0.0
print(v4.y) # 1.0
print(v4.z) # 2.0
print(v4.t) # 3.0

try:
    print(v4.q)
except Exception as e:
    print(repr(e)) # AttributeError("'Vector_v4' object has no attribute 'q'")
    
# However the implementation above has a subtle error. If we try to reassign one of these named attributes:
v4.x = 10.0

# It doesn't actually change the underlying object:
print(v4) # (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0) - first element still 0.0
print(v4._components) # array('d', [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
print(v4[0]) # 0.0

# Although accessing it again via __getattr__ does give the altered value
print(v4.x) # 10

# But we can update the components if we access them directly:
v4._components[0] = 8
print(v4) # (8.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)
print(v4[0]) # 8.0

# Although note that our Vector class doesn't support item assignment directly (via indexing):
try:
    v4[0] = 9.0
except Exception as e:
    print(repr(e)) # TypeError("'Vector_v4' object does not support item assignment")


# But the named attribute remains unchanged - it doesn't "revert back"
print(v4.x) # 10

# Prior to reassigning, the named attributed equaled their equivalent in the underlying object:
print(v4.y == v4[1]) # True
print(v4.y == v4._components[1]) # True

# And are in fact the same object in memory:
print(v4.y is v4[1]) # False
print(v4.y is v4._components[1]) # False
print(id(v4.y), id(v4[1]), id(v4.y) == id(v4[1])) # 140513768879256 140513768879256 True
print(id(v4.y), id(v4._components[1]), id(v4.y) == id(v4._components[1])) # 140513768879256 140513768879256 True

# So reassigning the underlying object directly changes the attribute:
print(v4.y) # 1.0
v4._components[1] = 8
print(v4.y) # 8.0

# And changing all the object in memory (but not its location) for all access patterns:
print(id(v4.y), id(v4[1]), id(v4.y) == id(v4[1])) # 140513768879256 140513768879256 True
print(id(v4.y), id(v4._components[1]), id(v4.y) == id(v4._components[1])) # 140513768879256 140513768879256 True

# Note: the above id's are the same as before v4._components[1] was reassigned


# But when we re-assign the attribute, we've move the reference to another object in memory
v4.y = 20.0
print(v4) # (8.0, 8.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)
print(id(v4.y), id(v4[1]), id(v4.y) == id(v4[1])) # 140513768879112 140513768879256 False
print(id(v4.y), id(v4._components[1]), id(v4.y) == id(v4._components[1])) # 140513768879112 140513768879256 False

# Note the id of v4[1] and v4._components[1] remain unchanged


# The happens because the line v4.x = 8.0 in fact /creates/ an x attribute, whereas previously trying to access it
# resulted in a call to __getattr__ after the attempt failed. Subsequent attempts to access x therefore /succeed/
# and return the newly-created attribute. Meanwhile the first element of _components remains entirely unchanged.

# Examining the structure of v4, we can see it now has an x and y attribute - but not z or t
print(dir(v4)) 

# Although we can still "access" z and t with the same syntax:
print(v4.z) # 2.0


# We'll instead deal with this by making the __setattr__ raise an AttributeError if attempting to assign
# values via the shortcut names (x, y, z ,t)

class Vector_v5(Vector_v4):
    
    def __setattr__(self, name, value):
        cls = type(self)
        
        if len(name) == 1:
            
            if name in cls.shortcut_names:
                error = 'readonly attribute {attr_name!r}'
            elif name.islower():
                error = "can't set attributes 'a' to 'z' in {cls_name!r}"
            else:
                error = '' # blank error message
            
            if error: # raise exception if error is not blank
                msg = error.format(cls_name = cls.__name__, attr_name = name)
                raise AttributeError(msg)
        
        super().__setattr__(name, value)

v5 = Vector_v5([3,4,5])
print(v5.x)
try:
    v5.x = 10
except Exception as e:
    print(repr(e)) # AttributeError("readonly attribute 'x'")

# Note: the above still lets us create 2- or more-character attributes, but prevents accidentally
# overwriting x,y,z,t

# We could allow for such overwriting by editing __setattr__, or __setitem__ - but we want Vector to be 
# immutable (so that we can hash it)

# Hashing and Faster ==

# We want to implement a __hash__ method - as together with __eq__, this will make our object hashable.
# To do this, we'll take the bitwise XOR of all the vector's components.
# We can use reduce from functools to do this.

# reduce successively applies an operation to each element of a collections.
import functools

# e.g. 5! = 5 * 4 * 3 * 2 * 1 can be done:
print(functools.reduce(lambda x,y: x*y, range(1,6))) # 120
print(5 * 4 * 3 * 2 * 1) # 120

# We could have also used an operator from the operator module in lieu of a hash
import operator
print(functools.reduce(operator.mul, range(1,6))) # 120

# So now we'll implement a __hash__ for our vector class:

class Vector_v6(Vector_v5):
    
    def __hash__(self):
        hashes = (hash(x) for x in self._components)
        return functools.reduce(operator.xor, hashes, 0) # 0 is the initialiser - which returns if trying to reduce an empty collection 
    # Note: use initialiser 0 as doing xor - for * or &, should use 1
    
v6 = Vector_v6(range(10))
print(hash(v6)) # 1
dict_v6 = {v6: 1}
print(dict_v6) # {Vector([0.0, 1.0, 2.0, 3.0, 4.0, ...]): 1}

# Note: an alternative approach to hashing each component would be to use map, e.g.:
# hashes = map(hash, self._components)
# map returns a generator, which yields values only when needed - and hence saves memory

# Our __eq__ method (which just took tuple(self), tuple(other)) is also inefficient, as it copies the 
# entire contents of both objects. 
# A better implementation is:
def eq(self, other):
    if len(self) != len(other):
        return False # can't be equal if different lengths
    
    for a, b in zip(self, other):
        if a != b:
            return False
    
    # If all elements match:
    return True

print(eq(v6, range(10))) # True
print(eq(v6, Vector_v6([1,2,3]))) # False

# This uses zip - which again is a generator, that returns tuples of corresponding elements in each 
# of its arguments. Although using a for loop over all elements is clearly a reduce pattern - we can
# instead do this via (say) all():

def eq_v2(self, other):
    return len(self) == len(other) and all(a == b for a, b in zip(self, other))

print(eq_v2(v6, range(10))) # True
print(eq_v2(v6, Vector_v6([1,2,3]))) # False


# Recall: zip iterates in parallel over any number of iterables, returning a tuple of corresponding values:
print("\n\nZip:")
z = zip("ABC", range(3), [10, 20, 30], {"a": 1, "b": 2, "c": 3}, {"d", "e", "f"})
for i in range(3):
    print(next(z))
# Prints:
# ('A', 0, 10, 'a', 'e')
# ('B', 1, 20, 'b', 'f')
# ('C', 2, 30, 'c', 'd')

# zip stops when the shortest iterable is exceeded:
z2 = zip("abcd", [1,2,3])
print(list(z2)) # [('a', 1), ('b', 2), ('c', 3)]

# However there is a zip_longest in itertools that instead stops at the longest iterable:
from itertools import zip_longest

z3 = zip_longest("abcd", [1,2,3])
print(list(z3)) # [('a', 1), ('b', 2), ('c', 3), ('d', None)] 

# "missing" elements from shorter iterables return None by default - but we can specify it:
z4 = zip_longest("abcdefg", [1,2,3], fillvalue = -1) 
print(list(z4)) # [('a', 1), ('b', 2), ('c', 3), ('d', -1), ('e', -1), ('f', -1), ('g', -1)]


# We can extend our Vector to print in (hyper-)spherical coordinates, if format string ends in "h"
# These coords are a single magnitude r, then (n-1) angles - for an n-dimensional sphere.
import itertools

class Vector_v7(Vector_v6):
    
    def angle(self, n):
        """Get nth angle"""
        r = math.sqrt(sum(x**2 for x in self[n:]))
        a = math.atan2(r, self[n-1])
        if (n == len(self) - 1) and (self[-1] < 0):
            return 2 * math.pi - a
        else:
            return a
    
    def angles(self):
        return (self.angle(n) for n in range(1, len(self)))
    
    def __format__(self, fmt_spec=''):
        if fmt_spec.endswith('h'):
            fmt_spec = fmt_spec[:-1]
            coords = itertools.chain([abs(self)], self.angles()) # chain "links" multiple iterators in sequence
            outer_fmt = '<{}>'
        else:
            coords = self
            outer_fmt = '({})'
        
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(', '.join(components))
    
    
v7 = Vector_v7([1, 1, 1])
print(v7) # (1.0, 1.0, 1.0)
print(format(v7, "h")) # <1.7320508075688772, 0.9553166181245093, 0.7853981633974483>
print(format(Vector_v7([1,1]), ".6fh")) # <1.414214, 0.785398> - i.e. <sqrt(2), pi/4