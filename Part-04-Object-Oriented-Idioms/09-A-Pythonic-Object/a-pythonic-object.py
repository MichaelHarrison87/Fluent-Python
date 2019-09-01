# Chapter 9 - A Pythonic Object [p247]

# We stary by implementing a simple 2D vector class, with __repr__, __str__, and __bytes__ methods - the 
# latter being invoked when bytes() is called on the object
from array import array
import math

class Vector2D:
    
    typecode = "d"
    
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    # Implement an alternative constructor, that creates the vector from bytes (since we can convert vectors into 
    # bytes, want to go the other way)
    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0]) # the first byte contains the typcode
        memv = memoryview(octets[1:]).cast(typecode) # convert the remaining bytes into the desired type
        return cls(*memv) # unpack the memoryview to the class' constructor
        
    def __iter__(self):
        return (i for i in (self.x, self.y))
    
    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self)
    
    def __str__(self):
        return str(tuple(self))
    
    def __bytes__(self):
        return (bytes([ord(self.typecode)]) + bytes(array(self.typecode, self)))
    
    def __eq__(self, other):
        return tuple(self) == tuple(other)
    
    def __abs__(self):
        return math.hypot(self.x, self.y)
    
    def __bool__(self):
        return bool(abs(self))
    
    
print("\nv1:")
v1 = Vector2D(3, 4)
print(v1) # (3.0, 4.0)
print(str(v1)) # (3.0, 4.0)
print(repr(v1)) # Vector2D(3.0, 4.0)

print(v1.x, v1.y) # 3.0 4.0
x, y  = v1
print(x, y) # 3.0 4.0

v1_clone = eval(repr(v1))
print(v1_clone == v1) # True
print(v1_clone is v1) # False

print(bytes(v1)) # b'd\x00\x00\x00\x00\x00\x00\x08@\x00\x00\x00\x00\x00\x00\x10@'
print(abs(v1)) # 5.0
print(bool(v1), bool(Vector2D(0,0))) # True False

# Note: our implmenetation of __eq__ means that similar iterables can compare as equal to Vector2d:
print(v1 == [3,4]) # List - True
print(v1 == (3,4)) # Tuple - True
print(v1 == {3,4}) # Set - True

print("\nv2:")
v2 = Vector2D.frombytes(b'd\x00\x00\x00\x00\x00\x00\x08@\x00\x00\x00\x00\x00\x00\x10@')
print(v2) # (3.0, 4.0)
print(v1 == v2) # True
print(v1 is v2) # False


# Note: classmethods operate on the class itself, not instances - hence cls in its arguments, vs self for the other methods.
# Common use of classmethods are to provide alterantive constructors, as above. Note: these can't be ordinary methods that work
# on instances, since we can't use these before the instance is created. Instead we need to call the classmethod in order to create 
# the instance.

# By contrast, staticmethods don't operate on either classes or instances, they're just plain function packages inside the class

# The format() build-in calls the object's __format__(format_spec) method, where format_spec specifies the format, e.g:
brl = 1/2.43
print("\nformat():")
print(brl) # 0.4115226337448559
print(format(brl, "0.4f")) # 0.4115
print(format(brl, "0.3f")) # 0.412

# format_spec can also be specified by whatever appears after the colon, in a replacement field delimited by {} inside a
# format string, when calling the str.format() method
print("1 BRL = {rate:0.2f} USD".format(rate=brl)) # 1 BRL = 0.41 USD

# See the Format Specification Mini-Language to see what the format_spec can achieve: 
# https://docs.python.org/3/library/string.html#formatspec
# It has presentation codes for various built-in types:

print(format(42, "b")) # bytes - 101010 (2 + 8 + 32 = 42)
print(format(2/3, ".1%")) # percentage (1 s.f.) - 66.7%

# The Mini-Language is extensible, since each class can interpet the format_spec as it chooses. 
# E.g. dates:
from datetime import datetime
now = datetime.now()
print(format(now, '%H:%M:%S')) # 01:49:53
print("It's now {:%I:%M %p}".format(now)) # It's now 01:49 AM

# If __format__ is not implmented, then the method inherited from object calls str(my_object).
# So applying for Vector2D (without __format__) still produces a result:
print(str(v1)) # (3.0, 4.0)
print(format(v1)) # (3.0, 4.0)

# However, get an error if try to pass a format spec:
try:
    print(format(v1, ".3f"))
except Exception as e:
    print(type(e), e) # <class 'TypeError'> unsupported format string passed to Vector2D.__format__
    
# We can implement one:
class Vector2D_fmt_1(Vector2D):
    
    def __format__(self, fmt_spec=""):
        components = (format(c, fmt_spec) for c in self) # apply the format spec to each part individually
        return "({}, {})".format(*components) # Now print out the formatted components
    
v3 = Vector2D_fmt_1(3, 4)
print(v3) # (3.0, 4.0)
print(format(v3, ".3f")) # (3.000, 4.000)
print(format(v3, ".1e")) # (3.0e+00, 4.0e+00)

# We can extend the Mini-Language to print the vector in polar coordinates if the format spec ends in "p":
class Vector2D_fmt_polar(Vector2D):
    
    def angle(self):
        return math.atan2(self.x, self.y)
    
    def __format__(self, fmt_spec=""):
        if fmt_spec.endswith("p"):
            fmt_spec = fmt_spec[:-1] # remove last character
            coords = (abs(self), self.angle())
            outer_fmt = "<{}, {}>"
        else:
            coords = self
            outer_fmt = "({}, {})"
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(*components)
            
v4  = Vector2D_fmt_polar(3, 4)
print("\nPolar Format")
print(v4) # (3.0, 4.0)
print(format(v4, ".3f")) # (3.000, 4.000)
print(format(v4, "p")) # <5.0, 0.6435011087932844>
print(format(Vector2D_fmt_polar(1,1), "p")) # <1.4142135623730951, 0.7853981633974483> - i.e. <sqrt(2), pi/4>
print("{vec:.0f} in polar coords: {vec:.2fp}".format(vec=Vector2D_fmt_polar(1,1))) # (1, 1) in polar coords: <1.41, 0.79>

# A Hashable Vector2D [p257]
# At the momemt, our Vector2D is not hashable, since we haven't provided a __hash__ method:
try:
    hash(v4)
except Exception as e:
    print(repr(e)) # TypeError("unhashable type: 'Vector2D_fmt_polar'")

# Making it hashable also requires making it immutables, which it isn't at the moment, since we can edit its attributes at will:
print(v4) # (3.0, 4.0)
v4.x = 5
v4.y = 7
print(v4) # (5, 7)

# We can use the @property decorator to make the components read-only:
class Vector2D_hashable:
    typecode = "d"
    
    def __init__(self, x, y):
        self.__x = float(x)
        self.__y = float(y)
        
        # "__" makes the attribute private - can't be accessed from outside 
        self.z = x+y
        self._z = x+y
        self.__z = x+y
    
    @property
    def x(self):
        return self.__x
    
    @property
    def y(self):
        return self.__y

    @property
    def q(self):
        return 2*self.__x
    
    def __iter__(self):
        return (i for i in (self.x, self.y))
    
    # To be hashable, also need an __eq__ method - as objects which evaluate as equal need to have the same hash
    def __eq__(self, other):
        return tuple(self) == tuple(other)
    
    # __hash__ needs to return an int, and account for the hashes of object attributes used in __eq__ (as equal objects 
    # must have the same hash). 
    # Python documentation recommends using bitwise XOR (^) to mix the hashes of components
    def __hash__(self):
        return hash(self.x) ^ hash(self.y)
    
    def __repr__(self):
        return "({}, {})".format(self.x, self.y)
        
    

# The @property decorator also allows the functions it decorates to be called as if they were attributes:
v5 = Vector2D_hashable(3, 4)
print("\nHashable Vector2D")
print(v5) # (3.0, 4.0)
print(v5.x) # 3.0
print(v5.y) # 4.0
print(v5.typecode) # d

# Test __eq__:
print("\nTest __eq__:")
print(v5 == Vector2D_hashable(3,4)) # True
print(v5 == Vector2D_hashable(1,1)) # False

# Also, the double underscore "__" a prefix makes attributes private:
try:
    print(v5.__x)
except Exception as e:
    print(repr(e)) # AttributeError("'Vector2D_hashable' object has no attribute '__x'")
    
print(v5.z) # 7 - not private
print(v5._z) # 7 - not private
try:
    print(v5.__z)
except Exception as e:
    print(repr(e)) # AttributeError("'Vector2D_hashable' object has no attribute '__z'")

print("\nTest __hash__:")
print(hash(v5)) # 7
print(hash(Vector2D_hashable(3,4))) # 7
print(hash(Vector2D_hashable(1,1))) # 0
print(hash(Vector2D_hashable(2,2))) # 0 - if x and y are equal, always get same hash

# Note: 3 in binary is 011, while 4 is 100. So bitwise XOR is 111:
# 011
# 100
# ---
# 111
# 111 = 4+2+1 = 7, as shown above

print(hash(Vector2D_hashable(5,2))) # 7 - bitwise XOR also gives binary result 111

# Of course, the equality operator still distinguished these two objects:
print(v5 == Vector2D_hashable(5,2)) # False

# Now that our class is hashable, we can use it as dict keys:
try:
    d = {Vector2D(1,1): 1, Vector2D(1,2): 2}
except Exception as e:
    print(repr(e)) # TypeError("unhashable type: 'Vector2D'")

d = {Vector2D_hashable(1,1): 1, Vector2D_hashable(1,2): 2}
print(d) # {(1.0, 1.0): 1, (1.0, 2.0): 2}
print(d[Vector2D_hashable(1,1)]) # 1

# And as sets:
try:
    s = {Vector2D(1,1), Vector2D(2,1), Vector2D(1,1)}
except Exception as e:
    print(repr(e)) # TypeError("unhashable type: 'Vector2D'")


s = {Vector2D_hashable(1,1), Vector2D_hashable(2,1), Vector2D_hashable(1,1)}
print(s) # {(1.0, 1.0), (2.0, 1.0)}

# Note that the private attributes prefixed with "__" are not entirely private - they're just made hardered to access.
# They're stored in the instance's __dict__, with with a prefix themselves of _ClassName:
print(v5.__dict__) # {'_Vector2D_hashable__x': 3.0, '_Vector2D_hashable__y': 4.0, 'z': 7, '_z': 7, '_Vector2D_hashable__z': 7}

# So can access the "private" attributes:
print(v5._Vector2D_hashable__x) # 3.0
print(v5._Vector2D_hashable__y) # 4.0

# And we can change them:
v5._Vector2D_hashable__x = 5
print(v5) # (5, 4.0)

# Although the derived attribute z has not updated:
print(v5.z) # 7 - same as before
print(v5._z) # 7

# But calling the hash does update properly - since its only evaluated when it's called
print(hash(v5)) # 1 - has 

# The intent is just to prevent accidentally overwriting them. Note: this is why the ClassName is also prefixed: 
# if we subclassed the class, and then created a new attribute which accidentally had the same name (including "__" prefix)
# then this would otherwise override the parent's version and potentially lead to bugs. Prefixing with the ClassName prevents this.

# Some people recommend avoiding the "annoyingly private" name-mangling via the "__" prefix, and instead to mangle names
# manually when considered appropriate (e.g. _MyClass_myattribute vs myattribute).

# The single underscore "_" prefix is also a Python convention to indicate that the atrribute shouldn't be accessed externally,
# although the convention is in no way enforced. 
# Although a semi-exception is that prefixing objects with "_" inside a module prevents that object from being imported via the
# "from module import * " command.

# So while the above attributes were "immutable", in fact they weren't, given the correct access pattern.
v6 = Vector2D_hashable(3,4)
print(v6)


# x - as an @property - can be accessed, but can't be edited
print(v6.x)
try:
    v6.x = 4
except Exception as e:
    print(repr(e)) # AttributeError("can't set attribute")

# z is just a simple attribute - so is mutable
print(v6.z) # 7
v6.z = 8
print(v6.z) # 7

# As is _z:
print(v6._z) # 7
v6._z = 10
print(v6._z) # 10

# Whereas __z can't be accessed directly, have to account for the name-mangling
try:
    print(v6.__z)
except Exception as e:
    print(repr(e)) # AttributeError("'Vector2D_hashable' object has no attribute '__z'")

try:
    v6.__z = 12
except Exception as e:
    print(repr(e)) # AttributeError("can't set attribute")

print(v6._Vector2D_hashable__z) # 7
v6._Vector2D_hashable__z = 12
print(v6._Vector2D_hashable__z) # 12


# The q @property function works as x does - allows access as if an attribute, but can't override it. Note: we don't have
# any underlying __q atrribute.
print(v6.q) # 6.0

try:
    v6.q = 14
except Exception as e:
    print(repr(e)) # AttributeError("can't set attribute")


# As mentioned above, Python stores instance attributes inside a dict attached to the object. (v5.__dict__ above).
# This can have memory implications - since dicts have memory overhead due to the underlying hashtable always keeping
# at least 1/3 of its slots free.
# So if we have (say) millions of instances with few attributes - may get substantial unnecessary memory overhead.

# But we can use __slots__ to change how the interpreter stores a class' instances' attributes - e.g. 
# as a tuple rather than a dict. 

# __slots__ is an attribute - and we provide it with an iterable containing the names (as strings) of the attributes
# we want to store in that iterable.
# But note: can't have any other attributes than those named in the __slots__ iterable.
# Also, if using __slots__, need to include "__weakref__" in the list of attribute names, to allow instances to be
# weakly-referenced (it's done by default for user-created classes without __slots__ defined).

# And finally: need to include __slots__ also in any subclasses, as the inherited attribute is ignored by the interpreter


# Note: we defined the attribute typecode in our vector class as a class attribute - i.e. initialising it outside of the 
# __init__ method, and not as an instance method (e.g. self.typecode). However in our __bytes__ method, we used it as
# an instance variable - via self.typecode.
# In effect, we used a class attribute to provide a default value to an instance attribute.

# It is possible to create a typecode instance variable it for specific instances - but any code that uses 
# self.typecode would then use the instance version, rather than the class version (which remains untouched).
v7 = Vector2D(1,1)
print(v7.typecode) # "d" - 8 byte double-precision float
print(bytes(v7)) # b'd\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf0?'

# Can change v7's typecode, but changes it only for this instance, not the class as a whole:
v7.typecode = "f" # 4 byte single-precision float
print(bytes(v7)) # b'f\x00\x00\x80?\x00\x00\x80?'
print(v7.typecode) # "f"
print(Vector2D.typecode) # "d"

# We can change the class attribute for all instances (which haven't overridden the attribute) by accessing it via the class
print("\nReassign typecode")
v8 = Vector2D(1,2)
print(v8.typecode)
print(bytes(v8))

# Changing the class attribute applies to already-created instances
Vector2D.typecode ="f"
print(v8.typecode)
print(bytes(v8))
Vector2D.typecode ="d"

# However the more idiomatic approach is to create a subclass and change the attribute.
class Vector2D_short(Vector2D):
    typecode = "f" 
    
v9 = Vector2D_short(2,1)
print(v9) # (2.0, 1.0)
print(v9.typecode) # "f"
print(bytes(v9)) # b'f\x00\x00\x00@\x00\x00\x80?'
print(repr(v9)) # Vector2D_short(2.0, 1.0) 

#Last line explains why __repr__ didn't hardcode the class name, as otherwise subclasses would get wrong name 
# (or else, override __repr__ themselves with the correct name)

