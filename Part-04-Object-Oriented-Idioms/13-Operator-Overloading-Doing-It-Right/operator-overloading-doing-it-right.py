# Chapter 13 - Operator Overloading: Doing It Right [p371]

# This chapter covers the infix operatores (e.g. +, |, ==) and unary operators (e.g. -, ~). 
# Infix operators refer to those placed between two operands (a + b, c * d etc)

# Unary are those that operate on only a single operand (-1, ~my_bool). In fact, + can be used as unary
# operator too:

a = -1
print(+a) # -1


# Operator overloading in Python follows the following rules:
# Can't overload operators for built-in types
# Can't create new operators, only overload existing ones
# Certain operators can't be overloaded: logical is, and, or, not (although their bitwise equivalents &, |, ~ can be)


# We can implement operator functionality in our own classes by implementing the appropriate dunder methods:
# __abs__, __pos__, __neg__ etc.
# These of course all take self as their first (and for unary operators, only) argument. However, they should
# not modify self at all - instead should return a new object.

# For infix operators, the Python interpreter follows rules when the operands are of mixed types. 
# E.g. for "a + b":

# Checks if a has an __add__ method, and if so calls a.__add__(b). Unless that method if NotImplemented.
# If not, or it returns NotImplements, checks if b has __radd__ and if so returns b.__radd__(a), unless that is NotImplemented
# Else, raises a TypeError with an unsupported operand types message

# (Note: NotImplemented is not the same as NotImplementedError - the former is a special singleton value that
# is /returned/ by infix operator special methods that inform the interpreter it cannot handle the given
# operand. NotImplementedError is an excpetion, usually raised by stub methods in abstract classes)

# __radd__ is the "right-side" or reversed version of add. There are equivs for other operators, e.g. 
# rsub, rmul

# For certain operators, only certain operand types are valid. E.g. with our Vector class from previous chapter,
# we might only want * to mean scalar multiplication (rather than matrix mult, or dot product).
# One approach here could be to use "goose typing", and check the other operand vs some suitable abstract 
# base class (here, numbers.Real - covers ints & floats but not complex numbers) via isinstance:
from array import array
import numbers

class Vector:
    
    typecode = 'd'
    
    def __init__(self, components):
        self._components = array(self.typecode, components)
    
    def __iter__(self):
        return iter(self._components)
     
    def __str__(self):
        return str(tuple(self))
        
    def __mul__(self, scalar):
        if isinstance(scalar, numbers.Real):
            return Vector(scalar * n for n in self)
        else:
            return NotImplemented
        
    def __rmul__(self, scalar):
        return self * scalar
    
v1 = Vector([1,2,3]) 
print(v1) # (1.0, 2.0, 3.0)
print(v1 * 2) # (2.0, 4.0, 6.0)
print(2 * v1) # (2.0, 4.0, 6.0)
print(v1 * True) # (1.0, 2.0, 3.0) - booleans are subtypes of ints
print(v1 * False) # (0.0, 0.0, 0.0)

try:
    print(v1 * Vector([4,5,6]))
except Exception as e:
    print(repr(e)) # TypeError("unsupported operand type(s) for *: 'Vector' and 'Vector'")