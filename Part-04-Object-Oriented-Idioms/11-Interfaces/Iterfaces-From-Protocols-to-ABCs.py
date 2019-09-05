# Chapter 11 - Interfaces: From Protocols to ABCs

# An example of an interface in Python is Sequence, an Abstract Base Class.

# We can get sequence-like behaviour even if we only implement some sequence methos, e.g:

class Foo:
    def __getitem__(self, pos):
        return range(0, 30, 10)[pos]
    
# Note Foo doesn't inherit from Sequence - but we can still use it as an iterator:
f = Foo()
print(f[1]) # 10

for i in range(3):
    print(f[i])

for i in f:
    print(i)
        
# The in operator also works:
print(10 in f) # True
print(15 in f) # False

# Iteration and in all work here, since they fall back on using __getitem__ with integer indices.
# The point being - we can get Sequence-like behaviour even by only partially implementing its protocol

# Monkey-Patching to Implement a Protocol at Runtime

# The French Deck class from chapter 1 did not subclass Sequence either, but it did implement both methods
# of the sequence protocol - __getitem__ and __len__. Recall:
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck:
    
    ranks = [str(n) for n in range(1, 11)] + list('JQKA')
    suits = ['spades', 'diamonds', 'clubs', 'hearts']
    
    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits 
                                        for rank in self.ranks
                      ]
    
    def __len__(self):
        return len(self._cards)
    
    def __getitem__(self, position):
        return(self._cards[position])
    

deck = FrenchDeck()
print(deck._cards)
print(deck[0]) # Card(rank='1', suit='spades')
print(deck[-1]) # Card(rank='A', suit='hearts')

# These methods are enough to support other operations, such as iteration:
for card in deck:
    print(card)
    
# Note currently shuffle doesn't work:
import random

try:
    random.shuffle(deck)
except Exception as e:
    print(repr(e)) # TypeError("'FrenchDeck' object does not support item assignment")


# We need to support item assignment, via a __setitem__ method - right now, FrenchDeck only implements the 
# /immutable/ sequence protocol - this extra method is required for a mutable sequence.

# We can monkey-patch support for this method:

def set_card(deck, position, card):
    deck._cards[position] = card

FrenchDeck.__setitem__ = set_card

print(deck[0]) # Card(rank='1', suit='spades')
random.shuffle(deck)
print(deck[0]) # Card(rank='10', suit='clubs') - deck has been shuffled

# Note: monkey-patching means to change a class or module at runtime, without chaning the underlying source 
# code - as done when we set FrenchDeck.__setitem__ above.

# Abstract Base Classes served as interface templates, even for classes which do not inherit from them - 
# they again just need to satisfy the required to "look like" one of the ABC's. AKA "Duck Typing"

# For instance, simply implementing a __len__ method with the correct syntax (callable with no
# argument) and semantics (returns a non-negative integer) is enough to be recognised as a "subclass"
# of the ABC "Sized":

from collections import abc

class Struggle:
    
    def __len__(self):
        return 5

print(isinstance(Struggle(), abc.Sized)) # True


# The more usual ways of identify a class as a subtype of an ABC are to either inherit from it, or to 
# register the class "virtual" subclass of the ABC.

# We'll demonstrate subclassing an ABC by creating an alternative version of FrenchDeck:

class FrenchDeck_v2(abc.MutableSequence):
    
    ranks = [str(n) for n in range(1, 11)] + list('JQKA')
    suits = ['spades', 'diamonds', 'clubs', 'hearts']
    
    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits 
                                        for rank in self.rank]
    
    # len and getitem required to be an (immutable) Sequence. So also required by the MutableSequence ABC
    def __len__(self):
        return len(self._cards)
    
    def __getitem__(self, position):
        return self._cards[position]
    
    # setitem required for shuffle to work
    def __setitem__(self, index, value):
        self._cards[index] = value
    
    # delitem and insert methods are required by the MutableSequence ABC
    def __delitem__(self, position):
        del self._cards[position]
    
    def insert(self, position, value):
        self._cards.insert(position, value)
        
        
# Now we demonstrate creating an ABC and some concrete imeplementations of it. It'll be "Tombola" - a
# collections of objects which can be drawn from at random, without replacement:

import abc

class Tombola(abc.ABC):
    
    @abc.abstractmethod
    def load(self, iterable):
        """Adds items from an iterable"""
        
    @abc.abstractmethod
    def pick(self):
        """Remove item at random, returning it.
        
           Should raise LookupError if instance is empty.
        """
    
    def loaded(self):
        """Return True if have at least one item"""
        return bool(self.inspect())
    
    def inspect(self):
        """Return sorted tuple with items inside"""
        items = []
        while True:
            try:
                items.append(self.pick()) # don't know how items will be stored, so retrive them with pick abstract method
            except LookupError:
                break
        self.load(items) # then after exhausting all items, load them back in
        return tuple(sorted(items))
    
# As seen above, ABC's can have concrete methods - loaded and inspect - however they must rely only on the 
# interface (methods (concrete or abstract), attributes etc) provided by that ABC/

# Of course, subclasses of Tombola can override these methods - e.g. with better inspect method, more 
# appropriate to its specific data types.

# Note our inspect method relies on pick throwing a LookupError - which we have said in pick's docstring. 
# However there is no way to enfore that any pick implementation must raise a LookupError. LookupError is 
# the base class for more specific types of lookup error such as IndexError or KeyError. So an implementation
# of this ABC could raise these latter Errors instead.

# The @abc.abtstractmethod required any subclasses to implement that method:
class Fake(Tombola):
    
    def pick(self):
        return 23

try:    
    f = Fake()
except Exception as e:
    print(repr(e)) # TypeError("Can't instantiate abstract class Fake with abstract methods load")
    
# Fake needs a load method

# We can stack decorators on top of @abstractmethod, e.g. to create abstract static or class methods, 
# or abstract properties. E.g. for an abstract class method:

class MyClass(abc.ABC):
    
    @classmethod
    @abc.abstractmethod
    def abstract_class_method(cls, *args):
        pass

# Note that @abstractmethod should always be the inner-most decorator in the stack.

# We'll now create some concrete subclasses of the Tombola ABC
import random

class BingoCage(Tombola):
    
    def __init__(self, items):
        self._randomizer = random.SystemRandom()
        self._items = []
        self.load(items)
        
    def load(self, items):
        self._items.extend(items)
        self._randomizer.shuffle(self._items)
        
    def pick(self):
        
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError('can\'t pick from empty {}'.format(__class__.__name__))   
    
    def __call__(self):
        self.pick()

cage = BingoCage(range(10))
print(cage.pick()) # 5
print(cage.pick()) # 4
        
cage.load([10, 11, 12])

# inspect and loaded are inherited from the Tombola ABC - but use its (inefficient) implementation
print(cage.inspect()) # (0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12) - inspect returns sorted tuple; 4 & 5 missing as were picked; 10,11,12 loaded in successfully
print(cage.loaded()) # True

print(cage.pick()) # 7
print(cage.pick()) # 11
print(cage.inspect()) # (0, 1, 2, 3, 6, 8, 9, 10, 12) - 4,5,7 & 11 now missing, as were picked
        
# pick remaining elements:
for i in range(9):
    cage.pick()

# Now try to pick again:
try:
    cage.pick()
except Exception as e:
    print(repr(e)) # LookupError("can't pick from empty BingoCage")
    

# An alternative concrete subclass of Tombola is below - which picks elements from random positions, rather than
# popping a shuffled list as above. Also overrides the inspect and loaded methods from the ABC with faster 
# alternative implementations

class LotteryBlower(Tombola):
    
    def __init__(self, iterable):
        self._balls = list(iterable) # think of the contents as lottery "balls"
    
    def load(self, iterable):
        self._balls.extend(iterable)

    def pick(self):
        try:
            position = random.randrange(len(self._balls))
        except ValueError:
            raise LookupError('can\'t pick from empty {}'.format(__class__.__name__))        
        return self._balls.pop(position)
    
    def loaded(self):
        return bool(self._balls)
    
    def inspect(self):
        return tuple(sorted(self._balls))
    
# Note: taking list(iterable) in the constructor above allows it to take in any iterable type but can
# still use lists' pop method (which is useful as we want to remove items - whereas the provided 
# iterable may be immutable; or if mutable, not desired to change in-place as would if we just
# set self._balls = iterable).


# We can also register a class as a "virtual" subclass of the ABC - which are distinct as they do not /inherit/ 
# from the ABC. So they wouldn't inherit (say) loaded or inspect above. But they do pass isinstance() 
# and issubclass() checks. However Python does not check whether the required interface (e.g. @abstractmethod's)
# is implemented at all.
# We can register a class as a virtual subclass using the ABC's register method.ArithmeticError

class FakeTombola:
    pass

Tombola.register(FakeTombola)
print(isinstance(FakeTombola(), Tombola)) # True
print(issubclass(FakeTombola, Tombola)) # True

# However inspecting the registered class' method resolution order shows it doesn't inherit from the ABC:
print(FakeTombola.__mro__) # (<class '__main__.FakeTombola'>, <class 'object'>)

# We can also register a class by decorating it. 
# Also the below subtypes list, so we inherit its constructor and other useful methods. Allowing for simpler 
# implementations of the Tombola methods

@Tombola.register
class TombolaList(list):
    
    def pick(self):
        if self:
            position = random.randrange(len(self))
        else:
            raise LookupError('can\'t pick from empty {}'.format(__class__.__name__))
    
    load = list.extend
    
    def loaded(self):
        return bool(self)
    
    def inspect(self):
        return tuple(sorted(self)) 

print(isinstance(TombolaList(), Tombola)) # True
print(issubclass(TombolaList, Tombola)) # True

# Note we can get Tombola's subclasses (i.e. its children, but not register virtual subclasses) as
# well as the virtual subclasses registered with it:

print(Tombola.__subclasses__()) # [<class '__main__.Fake'>, <class '__main__.BingoCage'>, <class '__main__.LotteryBlower'>]

_abc_registry, _abc_cache, _abc_negative_cache, _abc_negative_cache_version = abc._get_dump(Tombola)
print(_abc_registry) # {<weakref at 0x7fb2d653ee08; to 'type' at 0x7fffc2e5de18 (FakeTombola)>, <weakref at 0x7fb2d653eea8; to 'type' at 0x7fffc2e5e1c8 (TombolaList)>}
print(_abc_cache) # set()
print(_abc_negative_cache) # set()
print(_abc_negative_cache_version) # 38


# Recall the example of Struggle above, which was recognised as a subclass of Sized (from collections.abc),
# simply because it implmeneted __len__:
print(isinstance(Struggle(), collections.abc.Sized)) # True
print(issubclass(Struggle, collections.abc.Sized)) # True

# This was because Sized has a special method (or inherits one from abc) "__subclasscheck__", which contains
# logic specifying when comparisons as above should return True. In this case, it's that the class (or its
# parents have a __len__).ArithmeticError

# So a raw empty class doesn't pass
class Dummy:
    pass

print(isinstance(Dummy(), collections.abc.Sized)) # False
print(issubclass(Dummy, collections.abc.Sized)) # False

# But a class inheriting a __len__ method does:
class DummyList(list):
    pass

print(isinstance(DummyList(), collections.abc.Sized)) # True
print(issubclass(DummyList, collections.abc.Sized)) # True

# Try monkey-patching our dummy class above:
def len():
    return 1

Dummy.__len__ = len
print(isinstance(Dummy(), collections.abc.Sized)) # False
print(issubclass(Dummy, collections.abc.Sized)) # False

# Still returns False above - so not regarded as subclass
