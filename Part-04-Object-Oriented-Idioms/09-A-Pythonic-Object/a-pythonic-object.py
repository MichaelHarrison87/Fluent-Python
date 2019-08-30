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


# A Hashable Vector2D [p257]

