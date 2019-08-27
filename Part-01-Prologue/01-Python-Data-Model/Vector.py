import math

class Vector:
    """
    Implements 2D real vectors, and associated methods such as addition and scalar mutliplication
    """
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    # Define the representation of the object - called by print() by default
    # Note: !r ensures the attribute's own internal representation (via it's __repr__) is used
    # e.g. Vector("a", "b") is a valid instance of this class
    # Without the "!r", it would be displayed (per __str__() below) as "(a,b)"; 
    # With the "!r" it is displayed as "('a', 'b')" as '...' is the interal representation of strings
    def __repr__(self):
        return "Vector({!r}, {!r})".format(self.x, self.y) 
    
    # But can override this to print in alternative format - __str__ is used by print over __repr__, if available:
    def __str__(self):
        return "({!r},{!r})".format(self.x, self.y)
    
    # Absolute value
    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    # Define length as integer-part of the abs value (len must return integer)
    def __len__(self):
        return int(self.__abs__())  

    # Vector addition
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x, y)

    # __iadd__() & similar allow the += notation, e.g. x += 1 to increment x by 1
    def __iadd__(self, other):
        return self.__add__(other)

    # Scalar multiplication
    def __mul__(self, scalar):
        return Vector(scalar * self.x, scalar * self.y)
    
    def __rmul__(self, scalar):
        return Vector(scalar * self.x, scalar * self.y)

  

vec = Vector(1, 1)
print(vec, abs(vec))
print("(1,1) + (0,1) = ", vec + Vector(0,1))
print("(1,1) * 2 = ", vec * 2)
print("2 * (1,1) = ", 2 * vec) # Note: this would fail without the __rmul__() method, as * by default expects items in the same order as the args for __mul__()

# bool() returns True by default, if no __bool__ or __len__ methods are implemented
# if __len__() is implemented, then returns False if len() is 0; else returns True
print(vec, bool(vec)) # True - as len != 0 (we defined len as integer part of abs value)
print("(0,0)", bool(Vector(0,0))) # False as len = 0

vec2 = Vector(0,0)
vec2 += Vector(1,1)
vec2 += Vector(1,1)
print("vec2 ", vec2) # expect (2,2)

# Our definition of __add__() works with strings - which is something of an unintended consequence
print(Vector("a", "b"))
print(Vector("a", "b") + Vector("c", "d"))