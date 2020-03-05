# Chapter 20 - Attribute Descriptors [p625 (651 of 766)]

# Descriptors are a way of reusing the same access logic in multiple attributes

# A descriptor is a class that implements a protocol consisting of __get__, __set__
# and __delete__. Though n practice, often only __get__ and __set__ are 
# implemented, and __delete__ ignored as not needed

# For instance, property() is a class (not a function) which implements this 
# protocol:
print(type(property()), "\n", dir(property()))

# The @property decorator is just syntactic sugar on top of property(), so relies
# on descriptors too. As do the @classmethod and @staticmethod decorators

# A descriptor would be an alternative object-oriented approach to implementing
# the quantity property from Chapter 19 - where the latter took a functional 
# approach, using closures.

# We'll distinguish between the following:

# Descriptor Class: the class implementing the descriptor protocol

# Managed Class: the class where descriptor instances are declared as attributes

# Descriptor Instance

# Managed Instance

# Storage Attribute: an attribute of the managed instance, which holds the value
# of a managed attribute for that particular instance; these are distinct from
# descriptor instances, which are always class attributes

# Managed Attribute: a public attribute in the managed class, which will be 
# handled by a descriptor instance

class Quantity:

    def __init__(self, storage_name):
        # storage_name is the (instance) attribute, which is the name of the 
        # attribute that will hold the value in managed instances.
        self.storage_name = storage_name
    
    def __set__(self, instance, value):
        """Called when there's an attempt to assign to the managed attribute.
        Args:
            self: the descriptor instance (e.g. LineItem.price, LineItem.weight)
            instance: the managed instance (e.g. instance of LineItem)
            value: the value being assigned
        """
        if value > 0:
            # Add value to the managed instance's __dict__, with key/name storage_name
            # If we had instead done setattr(instance, value), this would have leade
            # to this __set__ method being called again - resulting in infinite recursion
            instance.__dict__[self.storage_name] = value 
        else:
            raise ValueError('value must be > 0')

    # Note that since each managed attribute will have the same name as its storage
    # attribute (and we don't have any special get logic), there's no need for 
    # a __get__ method.

class LineItem:

    # The below are /class/ attributes - initialising
    weight = Quantity("weight")
    price = Quantity("price")

    def __init__(self, description, weight, price):
        self.description = description

        # The below invokes the __set__ method of the Quantity instances 
        self.weight = weight
        self.price = price
    
    def subtotal(self):
        return self.weight * self.price

    
li1 = LineItem('melons', 10, 1.5)
print(li1.price, li1.weight, li1.subtotal())  # 1.5 10 15.0
print('Instance:', type(li1.price), type(li1.weight))  # <class 'float'> <class 'int'>
print('Class:', type(LineItem.price), type(LineItem.weight))  # Class: <class '__main__.Quantity'> <class '__main__.Quantity'>
print('Descriptor instance ids:', id(LineItem.price), id(LineItem.weight))  #  139975176276384 139975176347808 - distinct, i.e. these are indeed the instances, not the descriptor class itself

try:
    li = LineItem('bananas', -10, 1.5)
except Exception as e:
    print(repr(e))


# Note that the descriptor instances themselves are class attributes of the managed class
# - here, of LineItem. Hence if the descriptor's __set__ had assigned value to self,
# i.e. the descriptor instance, these would be the same across all instances of LineItem:

class QuantityWrong:

    def __init__(self, storage_name):
        self.storage_name = storage_name
    
    def __set__(self, instance, value):
        """We incorrectly assign value to self's __dict__, rather than instance's
        Note: the access in LineItem, e.g. self.price = price appears to invoke
        this __set__ method (via __setattr__?) with both instance and value, as
        __set__ expects 3 args, get a TypeError if call it with 2 (by removing 
        the unused instance arg)
        """
        if value > 0:
            self.__dict__[self.storage_name] = value 
        else:
            raise ValueError('value must be > 0')
    

class LineItemWrong:

    # The below are /class/ attributes - initialising
    weight = QuantityWrong("weight")
    price = QuantityWrong("price")

    def __init__(self, description, weight, price):
        self.description = description

        # The below invokes the __set__ method of the Quantity instances 
        self.weight = weight
        self.price = price


print("\nQuantityWrong:")
li1_wrong = LineItemWrong('wrong melons', 10, 1.5)
print(li1_wrong.price, li1_wrong.weight)  # <__main__.QuantityWrong object at 0x7f63467984c0> <__main__.QuantityWrong object at 0x7f6346798490>  - returns descriptor instances rather than values
print(li1_wrong.price.__dict__['price'], li1_wrong.weight.__dict__['weight'])  # 1.5 10  - have to dig into the descriptor instance dict to get the value

print("Now create bananas:")
li2_wrong = LineItemWrong('wrong bananas', 8, 0.75)
print('Price IDs:', id(li1_wrong.price), id(li2_wrong.price), id(li1_wrong.price) == id(li2_wrong.price))  #  139806513947840 139806513947840 True  - same object in both managed instances, as its a class attribute
print('Price Attribute:', li1_wrong.price.__dict__['price'], li2_wrong.price.__dict__['price'])  # 0.75 0.75  - same value in the dict for both instances

print('Weight IDs:', id(li1_wrong.weight), id(li2_wrong.weight), id(li1_wrong.weight) == id(li2_wrong.weight))  # 139806513947792 139806513947792 True - again same object across managed instances, but distinct from the price id's , as its a different descriptor instance
print('Weight Attribute:', li1_wrong.weight.__dict__['weight'], li2_wrong.weight.__dict__['weight'])  # 8 8 - same values, as for price


# Note that we need to ensure agreement between the storage_name arg passed to 
# Quantity(), and the variable name it is assigned to. This leaves us prone to
# typo errors, e.g price = Quantity('weight'), which would overwrite the
# weight attribute whenever price is set. 

# Instead, we could generate a unique string for the storage_name of each
# Quantity instance. For instace, attaching a number to some prefix, and
# incrementing it each time an attribute is added (i.e. the Quantity() is used):

class Quantity_2:
    __counter = 0   # counts numbers of Quantity_2 instances

    def __init__(self):     # no longer instantiate with storage_name, as it's now generated
        cls = self.__class__
        prefix = cls.__name__
        index = cls.__counter
        self.storage_name = f'_{prefix}#{index}'  # e.g. '_Quantity#0', '_Quantity#1' etc - this name isn't publically exposed or used, so it doesn't need to refer to what the actual instance is (e.g. 'weight', 'price') 
        cls.__counter += 1
    
    def __get__(self, instance, owner):
        print(f'\nInstance: {instance}\nOwner:{owner}')
        return getattr(instance, self.storage_name)     # get the storage_name from the managed instance
    
    def __set__(self, instance, value):
        if value > 0:
            setattr(instance, self.storage_name, value)  # set the value of the variable with the name of storage_name's value in the managed instance 
        else:
            raise ValueError('value must be > 0')


class LineItem_2:
    weight = Quantity_2()
    price = Quantity_2()

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price

print('\nLineItem_2:')
lineitem_2_1  = LineItem_2('melons', 10, 1.7)
lineitem_2_2  = LineItem_2('oranges', 20, 2.5)
print('lineitem_2_1:', lineitem_2_1.price, lineitem_2_1.weight, lineitem_2_1.subtotal()) # lineitem_2: 1.7 10 17.0
print('lineitem_2_2:', lineitem_2_2.price, lineitem_2_2.weight, lineitem_2_2.subtotal()) # lineitem_2_2: 2.5 20 50.0
lineitem_2_1.weight = 15
lineitem_2_1.price = 2
print('lineitem_2_1:', lineitem_2_1.price, lineitem_2_1.weight, lineitem_2_1.subtotal()) # lineitem_2_1: 2 15 30

try:
    lineitem_2_wrong = LineItem_2('bananas', -10, 1.7)
except Exception as e:
    print(repr(e))

try:
    lineitem_2_wrong = LineItem_2('apples', 10, -1.7)
except Exception as e:
    print(repr(e))


# Note: since storage_name above now had a different value from the variables which instantiate Quantity
# (weight = Quantity('weight) above), we could use setattr and getattr on it without trigger infinite
# recursion as previously - so we didn't have to manually manipulate the managed instance's __dict__.
# Although we did need to include a __get__ method

# Also: we can't mangle the storage_name with the name of the managed class (e.g. __LineItem_quantity0)
# since the class definition run before the class itself is built by the interpreter. So we don't have
# that information when each desctiptor instance is created. However the __counter variable ensures
# that storage_name is unique for all descriptor instances across all managed classes (and instances) it 
# may be used in.

# __get__ takes 3 arguments: self, instance & owner, where owner is a reference to the managed class
# itself (i.e. LineItem) vs the managed instance. This lets the descriptor get attributes from the
# managed class, if required.

# Note, if we try to get a managed attribute from the managed class directly, __get__
# gets None as its argument for instance. We then get an AttributeError, since getattr
# tries to find the stroage_name value in None

try:
    print(LineItem_2.weight)
except Exception as e:
    print(repr(e))  # AttributeError("'NoneType' object has no attribute '_Quantity_2#0'")


# In this case, it's useful to return the descriptor instance itself when __get__ is invoked
# via the managed class directly


# Now imagine we want to validate the description attribute of LineItem as well, e.g. 
# ensuring it is not blank. This suggests a slightly different paradigm - one class
# to handle getting/setting managed attributes, and another to handle their verfication
# (with this being subclassed to handle specific forms of verification - i.e. text vs
# numbers here). 

# The validate method here would be an abstract method, with concrete 
# subclasses to handle negative and blank input repsectively. This is an example of
# the Template Method design pattern. We implement it below:

import abc

class AutoStorage:
    __counter = 0 

    def __init__(self):
        cls = self.__class__
        prefix = cls.__name__
        index = cls.__counter
        self.storage_name = f'_{prefix}#{index}' 
        cls.__counter += 1
    
    def __get__(self, instance, owner):
        if instance is None:
            return self     # return the desctiptor instance if accessing the managed attribute from the managed class directly (e.g. LineItem.weight) - instance is None in this case
        else:
            return getattr(instance, self.storage_name)
    
    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)     # don't handle validation here - so just set the value and let downstream classes worry about if the value is correct - as incorrect values will never make it up to here


class Validated(abc.ABC, AutoStorage):

    def __set__(self, instance, value):
        value = self.validate(instance, value)      # apply a generic validate function 
        super().__set__(instance, value)            # then apply AutoStorage's __set__ method; 
    # this pattern is generic to all types of validation we might want to perform, so it makes sense to implement it in the 
    # generic template class; else would meed to redundantly reimplement __set__ for 
    # all specific validation classes  
    
    @abc.abstractmethod
    def validate(self, instance, value):
        """return a validated value, or else raise a ValueError"""


# Now we create concrete validation subclasses
class PositiveNumber(Validated):
    """Ensures numbers are greater than zero"""
    def validate(self, instance, value):
        if value <= 0:
            raise ValueError('value must be > 0')
        return value


class NonBlank(Validated):
    """Ensures a given string is not empty"""
    def validate(self, instance, value):
        if value is None:
            raise ValueError('value must not be None')
        value = value.strip()
        if len(value) == 0:
            raise ValueError('value must have length > 0')
        return value


class LineItem_3:
    description = NonBlank()
    weight = PositiveNumber()
    price = PositiveNumber()

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price
    
    def subtotal(self):
        return self.weight * self.price


lineitem_3 = LineItem_3('melons', 10, 0.7)
print('\nlineitem_3:', lineitem_3.description, lineitem_3.weight, lineitem_3.price, lineitem_3.subtotal())  # lineitem_3: melons 10 0.7 7.0

try:
    l = LineItem_3('', 5, 2)
except Exception as e:
    print(repr(e))  # ValueError('value must have length > 0')

try:
    l = LineItem_3('bananas', -10, 0.5)
except Exception as e:
    print(repr(e))

try:
    l = LineItem_3('bananas', 10, -0.5)
except Exception as e:
    print(repr(e))


try:
    lineitem_3.description = None
except Exception as e:
    print(repr(e)) # ValueError('value must not be None')



# Descriptors as used above are called overriding descriptors, as their __set__
# method overrides the setting of an attribute of the same name in the managed instance.

# Note: reading an attribute from an instance usually returns the attribute defined
# in the instance. But if there is none, a class attribute will be retrieved.
# Assigning an attribute in an instance usually creates it in the instance, and doesn't
# affect the class at all. 

# Therefore there's an asymmetry in how Python handles getting
# vs setting attributes. This affects descriptors too - resulting in two categories,
# depending on if they have a __set__ method or not.


# To demonstrate, we first define some auxilliary display functions:
def cls_name(obj_or_cls):
    cls = type(obj_or_cls)
    if cls is type:         # type is the metaclass of all user-defined types - so this checks if cls is one of these
        cls = obj_or_cls
    return cls.__name__.split('.')[-1]

def display(obj):
    cls = type(obj)
    if cls is type:
        return f'<class {obj.__name__}>'
    elif cls in [type(None), int]:
        return repr(obj)
    else:
        return f'<{cls_name(obj)} object>'

def print_args(name, *args):
    psuedo_args = ', '.join(display(x) for x in args)
    print(f'-> {cls_name(args[0])}.__{name}__({psuedo_args})')


# Now create the classes to demonstrate the different descriptor types:
print('\nDescriptor Class Types Demo:')

class Overriding:
    """i.e. data descriptor or enforced descriptor"""

    def __get__(self, instance, owner):
        print_args('get', self, instance, owner)
    
    def __set__(self, instance, value):
        print_args('set', self, instance, value)


class OverridingNoGet:

    # No __get__()

    def __set__(self, instance, value):
        print_args('set', self, instance, value)


class NonOverriding:
    """i.e. non-data or shadowable descriptor"""

    def __get__(self, instance, owner):
        print_args('get', self, instance, owner)
    
    # No __set__()

class Managed:
    over = Overriding()
    over_no_get = OverridingNoGet()
    non_over = NonOverriding()

    def spam(self):
        print(f'-> Managed.spam({display(self)})')


# Now instantiate to see the difference between the different descriptors
obj = Managed()

print('\n\n Overriding Descriptor - implements __set__ and __get__:')
obj.over        # -> Overriding.__get__(<Overriding object>, <Managed object>, <class Managed>)
Managed.over    # -> Overriding.__get__(<Overriding object>, None, <class Managed>)
obj.over = 1    # -> Overriding.__set__(<Overriding object>, <Managed object>, 1)
print('---print(obj.over)---')
print(obj.over)  # None -  as the __set__ method in Overriding does nothing
print('---')
obj.__dict__['over'] = 1
print('---print(obj.over)---')
print(obj.over)  # still None, as this trigger Overriding's __get__ rather than accessing obj's __dict__
print('---')
print(vars(obj)) # {'over': 1} - vars returns objects in obj's __dict__ (and doesn't trigger Overriding's __get__)


print('\n\n Overriding Descriptor without get - implements __set__ but NOT __get__:')
print(obj.over_no_get)        # <__main__.OverridingNoGet object at 0x7ff7537f9130> - descriptor has no __get__, so this just returns the descriptor instance that was created when instantiating Managed()
print(Managed.over_no_get)    # <__main__.OverridingNoGet object at 0x7ff7537f9130> - again get the descriptor instance, since it was instantiated as a class attribute in Managed()
obj.over_no_get = 1    # -> OverridingNoGet.__set__(<OverridingNoGet object>, <Managed object>, 1)
print('---print(obj.over_no_get)---')
print(obj.over_no_get)  # <__main__.OverridingNoGet object at 0x7ff7537f9130> - setting the value above didn't actually make any changes, so return the descriptor instance again
print('---')
obj.__dict__['over_no_get'] = 1
print('---print(obj.over_no_get)---')
print(obj.over_no_get)  # 1  - obj's __get__ method now finds the over_no_get attribute and returns its value, rather than returning the descriptor instance
print('---')
print(vars(obj)) # {'over': 1, 'over_no_get': 1} - over_no_get added to obj's vars


print('\n\n Non-Overriding Descriptor - implements __get__ but NOT __set__:')
print(obj.non_over)        # -> NonOverriding.__get__(<NonOverriding object>, <Managed object>, <class Managed>); prints None, as no value is returned by __get__
print(Managed.non_over)    # -> NonOverriding.__get__(<NonOverriding object>, None, <class Managed>); instance arg of __get__ is None; also prints None as no value returned by __get__
obj.non_over = 1    # prints nothings, as uses obj's __set__ method, rather than a descriptor's that prints stuff (as above)
print('---print(obj.over_no_get)---')
print(obj.non_over)  # 1 - obj now has a non_over attribute that shadows its same-name descriptor in the Managed() instance
print(Managed.non_over)  # -> NonOverriding.__get__(<NonOverriding object>, None, <class Managed>); but the above is an instance attrtibute only - the Managed class itself still falls back to the descriptor
print('---')
obj.__dict__['non_over'] = 2
print('---print(obj.over_no_get)---')
print(obj.non_over)  # 2  - instance attribute overwritten in obj's __dict__ directly
print('---')
print(vars(obj)) # {'over': 1, 'over_no_get': 1, 'non_over': 2}


# However, we can overwrite any descriptor on the class itself:
obj_2 = Managed()
Managed.over = 10
Managed.over_no_get = 20
Managed.non_over = 30
print(obj_2.over, obj_2.over_no_get, obj_2.non_over) # 10 20 30
print(obj.over, obj.over_no_get, obj.non_over) # 1 1 2 - these find the attributes at the instance-level, not the class-level


# Methods are Descriptors

# Since all user-defined functions automatically have a __get__ method:
def foo():
    return 'bar'

print(foo.__get__)  # <method-wrapper '__get__' of function object at 0x7f83d8b5fd30>

#... functions defined within classes operate as descriptors - i.e. methods are descriptors.

# But they do not implement __set__, and so are non-overriding descriptors:

try:
    print(foo.__set__)
except Exception as e:
    print(repr(e))  #  AttributeError("'function' object has no attribute '__set__'")


# And they can be overwritten in instances, e.g. the spam() method of Managed:

obj.spam()  #  -> Managed.spam(<Managed object>)
print(obj.spam) #  <bound method Managed.spam of <__main__.Managed object at 0x7f4d8fa5a1c0>>
print(Managed.spam)  # <function Managed.spam at 0x7f4d8fa58040>
obj.spam = 7
print(obj.spam) # 7

# Managed.spam (i.e. in effect calling its __get__ method) above returns the spam function itself
# - which follows the pattern of __get__ returning self when accessed via the class (i.e. when its
# instance argument is None)

# obj.spam, prior to overwriting, returns a bound method, which wraps the class function.
# The bound method is a callable, which binds the managed instance (i.e. obj) to the function's
# first argument (i.e. self).

# We explore this further with the class below:

import collections

class Text(collections.UserString):

    def __repr__(self):
        return f'Text({self.data!r})'
    
    def reverse(self):
        return self[::-1]

txt = Text('forward')

print(txt) # forward
print(repr(txt))  # Text('forward')
print(txt.reverse()) # drawrof

print(type(txt.reverse)) # <class 'method'>
print(type(Text.reverse)) # <class 'function'>
  
# So Text.reverse is a function, and can be used in lieu of ordinary functions:
print(list(map(Text.reverse, ['abc', (1,2,3), Text('ty')])))  # ['cba', (3, 2, 1), Text('yt')]

# But txt.reverse is a bound method, with its first arg fixed to txt, so can't use it in lieu of functions:
try:
    print(list(map(txt.reverse, ['abc', (1,2,3), Text('ty')])))
except Exception as e:
    print(repr(e)) #  TypeError('reverse() takes 1 positional argument but 2 were given')

# i.e. the map above passes the map elements to txt.reverse as 2nd args - 
# e.g. txt.reverse(txt, 'abc') etc and it throws an error as only takes one arg


# But Text.reverse is a non-overriding descriptor, so calling its __get__ with 
# an instance retrieves a bound method attached to that instance:

print(Text.reverse.__get__(txt))  #  <bound method Text.reverse of Text('forward')>
print(Text.reverse.__get__(txt)()) # drawrof - the bound method /is/ callable

# In fact, txt.reverse just invokes Text.reverse.__get__(txt):
print(txt.reverse == Text.reverse.__get__(txt)) # True

# Indeed, both reference the same object in memory:
print(id(txt.reverse),id(Text.reverse.__get__(txt)),id(Text.reverse), txt.reverse is Text.reverse.__get__(txt)) # 139840747399616 139840747399616 139840745702304 False

# But note that txt.reverse and Text.reverse are different objects in memory

# The "is" comparison above fails because it creates both the txt.reverse and Text.reverse.__get__(txt)
# objects in the same lifetime, in separates parts of memory; whereas calling id() on each separately
# created-then-destroyed the objects in memory. And since they were created one-after-another, they had
# the same address.

# Note the addresses below are different than those above, as are created in a new lifetime:
print(id(txt.reverse),id(Text.reverse), id(Text.reverse.__get__(txt))) # 139840747645760 139840745702304 139840747645760

print(id(txt.reverse))  # 140620719188800
a = 12345
b = 67890
print(id(Text.reverse.__get__(txt)))  # 140620719188800


txt_2 = Text('new text')
print(Text.reverse.__get__(txt_2)) # <bound method Text.reverse of Text('new text')>
print(Text.reverse.__get__(txt_2)()) # txet wen

print(txt.reverse.__self__) # forward - self is txt itself
print(txt.reverse.__func__) # <function Text.reverse at 0x7f93ea1e23a0> - the function inside Text

# We can use the __func__ as a function directly:
print(list(map(txt.reverse.__func__, ['abc', (1,2,3), Text('ty')])))  # ['cba', (3, 2, 1), Text('yt')]

# They are the same object:
print(txt.reverse.__func__ is Text.reverse) # True


# Descriptor Usage Tips

# The @property desctiptor creates an overriding descriptor, implementing both
# __set__ and __get__, even if the setter method is not defined. Though by default
# __set__ raises an AttributeError. But this can be used to create a read-only attribute

class Foo:

    def __init__(self, prop_2):
        self.prop_2 = prop_2
    @property
    def prop(self):
        return 5
    

foo = Foo(6)
print(foo.prop) # 5
print(foo.prop_2) # 6

# Can't overwrite prop:
try:
    foo.prop = 10
except AttributeError as e:
    print(repr(e))  # AttributeError("can't set attribute")

# But can prop_2 (as it's just an attribute, not a descriptor)
foo.prop_2 = 10
print(foo.prop_2) # 10


# An incorrect alternative approach to create a read-only attribute would 
# be a descriptor without __set__. However doing this will mean that a namesake
# attribute created on an instance will shadow the descriptor.

# This can be used to cache the result of an expensive __get__ calculation - 
# as we can set the result as a namesake attribute to shadow the descriptor, so
# that subsequent lookups just lookup the value in the instance's __dict__

import time
class Desc_NoSet:

    def __get__(self, instance, owner):
        """Long-running __get__"""
        for i in range(3):
            print(i+1, sep=", ")
            time.sleep(1)
        return 5

class NewManaged:
    desc = Desc_NoSet()

nm = NewManaged()
val = nm.desc
nm.desc = val

print(nm.desc) # 5
print(nm.desc) # 5
print(nm.desc) # 5

# Note: this affects functions and (non-special) methods as well, which only 
# implement __get__. 
# 
# This doesn't affect special methods (e.g. __repr__), as the 
# interpreter looks for these inside the class - i.e. repr(x) is
# in fact shorthand for x.__class__.__repr__(x).

# Class methods also cannot be shadowed, so long as they are accesses through
# the class.

class Foo:

    def bar(self):
        return 'bar'
    
    def __repr__(self):
        return '<Foo>'

    @classmethod
    def bar_class(cls):
        return 'bar_class'
    

foo = Foo()
print(foo.bar()) # bar
print(repr(foo)) # <Foo>

print(Foo.bar_class()) # bar_class

foo.bar = 'new bar'
print(foo.bar) # new bar
try:
    print(foo.bar())
except Exception as e:
    print(repr(e))  # TypeError("'str' object is not callable")

def new_repr():
    return 'new repr'

print(foo.__repr__()) # <Foo>
foo.__repr__ = new_repr
print(foo.__repr__()) # new repr
print(repr(foo))  # <Foo>
print(vars(foo)) # {'bar': 'new bar', '__repr__': <function new_repr at 0x7fc43be8bd30>}

try:
    Foo.bar_class = new_repr
    print(Foo.bar_class())  # new repr
except Exception as e:
    print(repr(e))

foo.bar = new_repr
print(foo.bar()) # new repr


    





