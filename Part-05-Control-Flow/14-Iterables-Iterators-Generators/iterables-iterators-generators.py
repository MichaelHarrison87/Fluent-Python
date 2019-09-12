# Chapter 14: Iterables, Iterators and Generators [p401]

# We start by seeing how the iter() built-in function makes sequences iterable.
# Below we implement a Sentence class that takes in strings, and allows iteration over the words:
import re
import reprlib

RE_WORD = re.compile('\w+')

class Sentence:
    
    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)
        
    def __getitem__(self, index):
        return self.words[index]
    
    def __len__(self):
        return len(self.words)
    
    def __repr__(self):
        return 'Sentence(%s)' % reprlib.repr(self.text)
    
    
s = Sentence('"The time has come," the Walrus said,')
print(s)  # Sentence('"The time ha... Walrus said,')  - reprlib.repr abbreviates long strings

for word in s:
    print(word)

# Prints:  
# The
# time
# has
# come
# the
# Walrus
# said

print(list(s)) # ['The', 'time', 'has', 'come', 'the', 'Walrus', 'said']
print(s[0]) # The
print(s[5]) # Walrus
print(s[-1]) # said


# Sequences are iterable because the Python interpreter calls the built-in iter() on the object, to obtain 
# the iterable.

# If __iter__ is not implemented, but __getitem__ is - Python creates an iterator that attempts to 
# return items in order, starting at index 0 and incrementing from there.

# Otherwise, get a TypeError saying the object isn't iterable.

# Note: merely implementing __getitem__ but not __iter__ doesn't make an object a (virtual) subclass of
# the Iterable ABC:
from collections import abc

print(isinstance(s, abc.Iterable)) # False
print(issubclass(Sentence, abc.Iterable)) # False

# However, having __iter__ does:
class Foo:
    
    def __iter__(self):
        pass

print(isinstance(Foo(), abc.Iterable)) # True
print(issubclass(Foo, abc.Iterable)) # True

# But: calling iter() on classes with only __getitem__ still does work (and is what supports the other
# iteration patterns, such as for loops):

s_iter = iter(s)
print(s_iter) # <iterator object at 0x7fb32d7de400>
for i in range(3):
    print(next(s_iter))
# Prints:
# The
# time
# has

# So trying to call iter() on an object may be a more /practical/ test of it being iterable than the
# isinstance/subclass test above.


# Iterables vs Iterators:

# An iterable is an object from which the iter() built-in function can obtain an iterator. The iterator is 
# then the object that can be iterated over.

# For instance, a string is an iterable - with an iterator behind the scenes:
s = 'ABC'
it = iter(s)
print(it) # <str_iterator object at 0x7f23f589d518>

while True:
    try:
        print(next(it))
    except StopIteration:
        del it
        break

# So 'it' is the iterator object. Iterators raise StopIteration when the iterator is exhausted.

# The standard interface for iterators has two method: __next__ to get the next item, until iterator is 
# exhausted (when it raises StopIteration) and __iter__ which returns self - so that iterators can be 
# used where iterables are expected (e.g. in a for loop).

# Note the ABC Iterator inherits from the ABC Iterable - and Iterable has an abstract method __iter__ - 
# which Iterators implements by simply returning self

# Iterator also has a __subclasshook__ meaning any class implementing __next__ and __iter__ is a virtual 
# subclass of Iterator:

class C:
    def __iter__(self):
        pass
    
    def __next__(self):
        pass
 
    
from collections import abc

print(isinstance(C(), abc.Iterator)) # True
print(issubclass(C, abc.Iterator)) # True


# Note: there is no way to check if an Iterator is exhausted, other than to call next() on it and check
# for StopIteration exception. Nor can Iterators be refreshed - they have to be re-created from scratch
# on the original Iterable.

# So our Sentence class is an iterable - as we can create an iterator of it:
s = Sentence('Hi There World')
it = iter(s)
print(next(it)) # Hi
print(next(it)) # There
print(next(it)) # World

try:
    next(it)
except Exception as e:
    print(repr(e)) # StopIteration()
    
# We now implement a SentenceIterator class - for the iterator associated with Sentence.
# This needs to implement both __iter__ and __next__
class SentenceIterator:
    
    def __init__(self, words):
        self.words = words
        self.index = 0
    
    def __next__(self):
        try:
            word = self.words[self.index]
        except IndexError:
            raise StopIteration()
        
        self.index += 1
        return word

    def __iter__(self):
        return self
    

# Now we re-implement Sentence to use this iterator in its __iter__ method:

class Sentence_v2:
        
    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)
    
    def __repr__(self):
        return 'Sentence(%s)' % reprlib.repr(self.text)
    
    def __iter__(self):
        return SentenceIterator(self.words)

print('\nTest Sentence_v2:')
s = Sentence_v2('Hi There World')
it = iter(s)
print(next(it)) # Hi
print(next(it)) # There
print(next(it)) # World

try:
    next(it)
except Exception as e:
    print(repr(e)) # StopIteration()
    
# And SentenceIterator is indeed a subclass of the Iterator ABC:
print(type(it)) # <class '__main__.SentenceIterator'>
print(isinstance(it, abc.Iterator)) # True
print(issubclass(SentenceIterator, abc.Iterator)) # True

# Note: an alternative would have been for SentenceIterator to explicitly subclass abc.Iterator - 
# and inherit the concrete __iter__ method (which also just returns self) rather than implement it itself.


# To reiterate the distinction between Iterables and Iterators: Iterables have an __iter__ method, that 
# returns a (fresh) iterator each time it is called. Iterators implement a __next__ method that is used to
# return individual items, and an __iter__ method that returns self.
# So Iterators are iterable, but Iterables are not Iterators.

# A temptation above might have been to implement a __next__ method in Sentence itself - so that it is both
# an Iterable, and an Iterator over itself. However this is bad practice, and considered an anti-pattern.

# To see why, consider the purposes of Iterators (as opposed to Iterables):
# To access an aggregate object's contents without exposing the internal representation
# To support multiple traversals of aggregate objects
# To support a uniform interface for traversing different aggregate strucure (i.e. polymorphic iteration)

# So to support mutliple traversals, need to be able to obtain multiple Iterators from a single Iterable - 
# i.e. each __iter__ call on the Iterable needs to return a fresh instance of the Iterator, with its own 
# internal state.


# However, having two connected classes such as Sentence and SentenceIteror above is cumbersome.
# A more Pythonic approach is instead to have the Iterable yield a generator to act as the Iterator:

class Sentence_v3:
        
    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)
    
    def __repr__(self):
        return 'Sentence(%s)' % reprlib.repr(self.text)
    
    def __iter__(self):
        for word in self.words:
            yield word
        return

print('\nTest Sentence_v3')
s = Sentence_v3('Hi There World')
it = iter(s)
print(it) # <generator object Sentence_v3.__iter__ at 0x7fa96adf38b8>
print(next(it)) # Hi
print(next(it)) # There
print(next(it)) # World

try:
    next(it)
except Exception as e:
    print(repr(e)) # StopIteration()
    
print(type(it)) # <class 'generator'>
print(isinstance(it, abc.Iterator)) # True
print(issubclass(SentenceIterator, abc.Iterator)) # True


# Note that the yield keyword creates a Generator object - a function with yield in its body is therefore
# a Generator factory. Consider:

def gen_123():
    yield 1
    yield 2
    yield 3
    
print(gen_123) # <function gen_123 at 0x7f8f2af890d0>
g = gen_123() # <generator object gen_123 at 0x7f1a9cc83de0> - function returns a generator
print(g)
print(next(g)) # 1
print(next(g)) # 2
print(next(g)) # 3 - as expected


try:
    next(g)
except Exception as e:
    print(repr(e)) # StopIteration()

# Generators can continue indefinitely:
def gen_count():
    start = 1
    while True:
        yield start 
        start += 1

g = gen_count()
for i in range(19):
    print(next(g), end=',')
print(next(g)) # 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20


# When running generators, calling next() on them will execute code up to the yield statement. Then 
# subsequent next() calls execute the code from that point on, up to the next yield statement. And so 
# on until the end of the code block is reached (either it ends, or hits a return statement):

def genAB():
    print('Start')
    yield 'A'
    print('Continue')
    yield 'B'
    print('End')
    
for c in genAB():
    print('-->', c)

# Start
# --> A
# Continue
# --> B
# End

# Note that the for loop above handles and squashes the raising on StopIteration() on the third (undelying)
# call to next() - as that call print 'End' but then raises StopIteration() as it has no more objects to
# return

# We see StopIteration if we try to manually call next:
print('\nManual next:')
g = genAB()
print(next(g), end=';\n')
# Start
# A;
print(next(g), end=';\n')
# Continue
# B;
try:
    print(next(g)) # End
except Exception as e:
    print(repr(e)) # StopIteration()
    
    
# Sentence v4 Lazy Implementation: note our implementation of Sentence above is not lazily-evaluated,
# since its __init__ eagerly builds a list of all words in the text, and binds that list to self.words.

# This was driven by our use of re.findall. A lazy alternative is re.finditer - which returns a generator
# producing re.MatchObject instances on-demand. We use it below to make a lazy version of Sentence:

class Sentence_v4:
    
    def __init__(self, text):
        self.text = text
    
    def __repr__(self):
        return 'Sentence(%s)' % reprlib.repr(self.text)
    
    def __iter__(self):
        return (match.group() for match in RE_WORD.finditer(self.text))
    

# Note: we used a generator comprehension in the definition of iter
s = Sentence('Hi There World')
# But note that the __iter__ method /returns/ a generator (rather than using /yield/)
it = iter(s)
print(it) # <iterator object at 0x7ff2a2b9ffd0> 
print(next(it)) # Hi
print(next(it)) # There
print(next(it)) # World

# Note: generator comprehensions are lazily evaluated, unlike list comprehensions.
# For instance, creating a listcomp from the generator above executes the code inside it:
print('\nListcomp:') 
l = [x for x in genAB()]
# Prints:
# Start
# Continue
# End
# without even doing anything with the list l

# cf:
print('\nGencomp:') 
g = (x for x in genAB())
# Nothing is printed, only when we use the new generator g is the code in genAB() executed:

print(g) # <generator object <genexpr> at 0x7f7802bf3ed0>
for item in g:
    print('-->', item)
# Prints:
# Start
# --> A
# Continue
# --> B
# End


# An alternative use for generators than traversal is to /generate/ values on-the-fly, potentially indefinitely.
# For instance, consider the class below, which generates numbers between some begin and 
# end values, with a given step size.

class ArithmeticProgression:
    
    def __init__(self, begin, step, end = None):
        self.begin = begin
        self.step = step
        self.end = end # None implies indefinite series
        
    def __iter__(self):
        result = type(self.begin + self.step)(self.begin) # e.g. type(2+0.5) evaluates to float - so this becomes float(2)
        forever = self.end is None
        index = 0
        while forever or result < self.end:
            yield result
            index += 1
            result = self.begin + index * self.step

print('\nArithmetic Progression')
ap = ArithmeticProgression(1, 0.25, 2)
print(list(ap)) # [1.0, 1.25, 1.5, 1.75]

ap = ArithmeticProgression(0, 0.5)
g = iter(ap)
# g can be called indefinitely
for i in range(10):
    print(next(g), end=', ')
print(next(g)) # 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0

for i in range(89):
    next(g)
print(next(g)) # 50.0

# Arithmetic Progression with itertools
# The itertools package has count, which does indefinite arithmetic progression:
import itertools

c = itertools.count(1, 0.5)
print(next(c)) # 1
print(next(c)) # 1.5
print(next(c)) # 2
print(next(c)) # 2.5

# This count can be used indefinitely - so trying to put it into a list: list(c) would fail.

# itertool's takewhile function consumes another generator, until some condition is met - and returns
# a generator
gen = itertools.takewhile(lambda x: x < 4, c)
print(next(gen)) # 3.0
print(next(gen)) # 3.5
try:
    print(next(gen))
except Exception as e:
    print(repr(e)) # StopIteration()
    
# So we could use count and takewhile to implement our arithmetic progression

def arith_prog_gen(begin, step, end = None):
    first = type(begin + step)(begin)
    ap_gen = itertools.count(first, step)
    
    if end is not None:
        ap_gen = itertools.takewhile(lambda x: x <= end, ap_gen)
    
    return ap_gen 
    
ap = arith_prog_gen(0, 0.5, 10)
print(list(ap)) # [0, 2, 4, 6, 8, 10]

# Note: the function above doesn't use 'yield' - so it is not itself a generator. Instead it /returns/
# generator objects - so it acts as a generator factory.

# Other standard library iterators:

## Selection Generators

# compress: consumes two iterables in parallel, returning items from the first whenever the second is truth:
a = "abcdef"
b = [True, False, 1, 0, "a", [1,2,3]]
c = itertools.compress(a, b)
print(list(c)) # ['a', 'c', 'e', 'f']

# dropwhile: consumers an iterable, but skipping items while some predicate remains truthy, but once
# it becomes falsey, yields all further items (regardless of predicate's status)

# filterfalse: yields items whenever predicate is falsey

def vowel(letter):
    return letter in 'aeiou'


c = itertools.dropwhile(vowel, 'aaabcdef') 
print(list(c)) # ['b', 'c', 'd', 'e', 'f'] - drops first 3 a's, but not the remaining vowels after hitting the consonant b

c = itertools.filterfalse(vowel, 'aaabcdef')
print(list(c)) # ['b', 'c', 'd', 'f'] - drops all vowels (i.e. where vowel is Truw)

# cf the built-in filter - of which filterfalse is the inverse:
c = filter(vowel, 'aaabcdef')
print(list(c)) # ['a', 'a', 'a', 'e'] - drops all consonants (i.e. where vowel is False)

# takewhile - inverse of dropwhile, yields item while the predicate is truthy, then stops yielding, 
# with no further checks made after predicate stops being truthy
c = itertools.takewhile(vowel, 'aaabcdef')
print(list(c)) # ['a', 'a', 'a'] - stops yielding after first consonant

# islice - take slices from an iterable, but returns then as a generator, executed lazily

c = itertools.islice('abcdefghi', 0, 6, 2)
print(c) # <itertools.islice object at 0x7f6c8edac408>
print(type(c)) # <class 'itertools.islice'>
print(next(c)) # a
print(next(c)) # c
print(next(c)) # e
try:
    next(c)
except Exception as e:
    print(repr(e)) # StopIteration()
    
## Mapping Generators
    
# accumulate: cumulative sum over the items in the provided iterable. Can provide an option function

print(list(itertools.accumulate([1,2,3,4,5]))) # [1, 3, 6, 10, 15] - cumulative sums
print(list(itertools.accumulate([1,2,3,4,5], lambda x, y: x*y))) # [1, 2, 6, 24, 120] - cumulative products
print(list(itertools.accumulate([1,3,4,2,5], max))) # [1, 3, 4, 4, 5] - rolling max values

# enumerate: yields tuples of (index, item) over an iterable.
e = enumerate(['a', 'b', 'c'])
print(e) # <enumerate object at 0x7f0116d6d510>
print(next(e)) # (0, 'a')
print(list(e)) # [(1, 'b'), (2, 'c')]

# note: can specify a starting value for enumerate:
e = enumerate(['a', 'b', 'c'], start = 100)
print(list(e)) # [(100, 'a'), (101, 'b'), (102, 'c')]

# But not apparently a step, as enumerate takes a max of 2 args:
try:
    e = enumerate(['a', 'b', 'c'], start = 100, step= 50)
except Exception as ex:
    print(repr(ex)) # TypeError('enumerate() takes at most 2 arguments (3 given)')


# map: passes iterable items to a function as arguments; can have arbitrarily many iterables so long as
# the function has as many corresponding arguments. In this case, all the iterables are iterated over
# in parallel
m = map(lambda x: x**2, [1,2,3,4])
print(m) # <map object at 0x7f91410a64a8>
print(next(m)) # 1
print(list(m)) # [4, 9, 16]

def f(x, y, string):
    return string + str(x+y)

m  = map(f, [1,2,3], [4,5,6], ['a', 'b', 'c'])
print(next(m)) # a5
print(list(m)) # ['b7', 'c9']


# starmap: apply a map function over an input iterable, where the input iterable is itself comprised of 
# iterables, with the function taking the inner iterables' items as arguments (func(*args) - hence "star" map)

l = [['a'], ['a', 'b'], ['a', 'b', 'c']] 

def conc(*args):
    res = ''
    for i in args:
        res += i
    return res

sm = itertools.starmap(conc, l)
print(sm) # <itertools.starmap object at 0x7f2ba3fa3a20>
print(next(sm)) # a
print(list(sm)) # ['ab', 'abc']


## Merging Generators

# chain: yields all items from a sequence of iterables, in sequence:

c = itertools.chain([1,2,3], (4,5,6), {'a', 'b', 'c'})
print(next(c)) # 1
print(list(c)) # [2, 3, 4, 5, 6, 'a', 'c', 'b']


# chain.from_iterable: chains items from iterables that are themselves generated by the input iterable

a = arith_prog_gen(0, 0.5, 2)
b = itertools.chain(['a', 'b'], ['c', 'd'])
l = [a, b, ['s', 3]] # l is an iterable of iterables
c = itertools.chain.from_iterable(l)
print(next(c)) # 0.0
print(list(c)) # [0.5, 1.0, 1.5, 2.0, 'a', 'b', 'c', 'd', 's', 3]


# product: creates the Cartesian (or cross) prodcut of a set of N iterables, returning each combo of items
# as tuples
c = itertools.product([1, 2], ('a', 'b', 'c'), 'z') # note, the singleton 'z' counts as an iterable too
print(next(c)) # (1, 'a', 'z')
print(list(c)) # [(1, 'b', 'z'), (1, 'c', 'z'), (2, 'a', 'z'), (2, 'b', 'z'), (2, 'c', 'z')]

# e.g. could generate all squares of a chess board:
c = itertools.product("ABCDEFGH", range(1,9))
print(list(c))
# [('A', 1), ('A', 2), ('A', 3), ('A', 4), ('A', 5), ('A', 6), ('A', 7), ('A', 8), 
#  ('B', 1), ('B', 2), ('B', 3), ('B', 4), ('B', 5), ('B', 6), ('B', 7), ('B', 8), 
#  ('C', 1), ('C', 2), ('C', 3), ('C', 4), ('C', 5), ('C', 6), ('C', 7), ('C', 8), 
#  ('D', 1), ('D', 2), ('D', 3), ('D', 4), ('D', 5), ('D', 6), ('D', 7), ('D', 8), 
#  ('E', 1), ('E', 2), ('E', 3), ('E', 4), ('E', 5), ('E', 6), ('E', 7), ('E', 8), 
#  ('F', 1), ('F', 2), ('F', 3), ('F', 4), ('F', 5), ('F', 6), ('F', 7), ('F', 8), 
#  ('G', 1), ('G', 2), ('G', 3), ('G', 4), ('G', 5), ('G', 6), ('G', 7), ('G', 8), 
#  ('H', 1), ('H', 2), ('H', 3), ('H', 4), ('H', 5), ('H', 6), ('H', 7), ('H', 8)]


# zip: returns items in tuples from N iterables in parallel; stops when the shortest iterable is exhausted
z = zip(['a', 'b', 'c'], {1, 2, 3}, 'de')
print(list(z)) # [('a', 1, 'd'), ('b', 2, 'e')]

# zip_longest: as above, but keeps yielding until the longest iterable is exhausted, returning None for the 
# exhausted ones:
z = itertools.zip_longest(['a', 'b', 'c'], {1, 2, 3}, 'de', [1])
print(list(z)) # [('a', 1, 'd', 1), ('b', 2, 'e', None), ('c', 3, None, None)]

# Can specify a fill value for the exhausted items
z = itertools.zip_longest(['a', 'b', 'c'], {1, 2, 3}, 'de', [1], fillvalue = 'nan')
print(list(z)) # [('a', 1, 'd', 1), ('b', 2, 'e', 'nan'), ('c', 3, 'nan', 'nan')]


## Expansion generators - these yield more than one value per input item

# combinations: yields combinations (as tuples) of a given length of items in the input iterable
c = itertools.combinations(['a', 'b', 'c'], 1)
print(list(c)) # [('a',), ('b',), ('c',)]

c = itertools.combinations(['a', 'b', 'c'], 2)
print(list(c)) # [('a', 'b'), ('a', 'c'), ('b', 'c')] - all ways of picking 2 distinct items

c = itertools.combinations(['a', 'b', 'c'], 3)
print(list(c)) # [('a', 'b', 'c')] - only 1 way of picking 3 distinct items

c = itertools.combinations(['a', 'b', 'c'], 4)
print(list(c)) # [] - no way to 4 distinct items

# So the number of items return by combinations, with an iterable of length n and r=k is (n choose k):
c = itertools.combinations(range(5), r=2)
print(len(list(c))) # 10 - i.e. 5 choose 2: 5!/(3!2!) = 120/(6*2) = 10


# combinations_with_replacement: as the name suggests
c = itertools.combinations_with_replacement(['a', 'b', 'c'], r=1)
print(list(c)) # [('a',), ('b',), ('c',)]

c = itertools.combinations_with_replacement(['a', 'b', 'c'], r=2)
print(list(c)) # [('a', 'a'), ('a', 'b'), ('a', 'c'), ('b', 'b'), ('b', 'c'), ('c', 'c')]

c = itertools.combinations_with_replacement(['a', 'b', 'c'], r=3)
print(list(c)) 
c = itertools.combinations_with_replacement(['a', 'b', 'c'], r=3)
print(len(list(c))) # 10
# [('a', 'a', 'a'), ('a', 'a', 'b'), ('a', 'a', 'c'), 
#  ('a', 'b', 'b'), ('a', 'b', 'c'), ('a', 'c', 'c'), 
#  ('b', 'b', 'b'), ('b', 'b', 'c'), ('b', 'c', 'c'), 
#  ('c', 'c', 'c')]

c = itertools.combinations_with_replacement(['a', 'b', 'c'], r=4)
print(list(c))
# [('a', 'a', 'a', 'a'), ('a', 'a', 'a', 'b'), ('a', 'a', 'a', 'c'), 
#  ('a', 'a', 'b', 'b'), ('a', 'a', 'b', 'c'), ('a', 'a', 'c', 'c'), 
#  ('a', 'b', 'b', 'b'), ('a', 'b', 'b', 'c'), ('a', 'b', 'c', 'c'), 
#  ('a', 'c', 'c', 'c'), ('b', 'b', 'b', 'b'), ('b', 'b', 'b', 'c'), 
#  ('b', 'b', 'c', 'c'), ('b', 'c', 'c', 'c'), ('c', 'c', 'c', 'c')]
c = itertools.combinations_with_replacement(['a', 'b', 'c'], r=4)
print(len(list(c))) # 15

# Formaula for choosing k object from a list of n with replacement is (n+k-1) choose k
# e.g. n=3, k=4: 6 choose 4 = 6!/4!2! = (6*120)/48 = 120/8 = 15 - as in the last example above


# count: yields increments from the given start number, with the given step-size (default: 1)


# cycle: yields items from the iterator in sequence, repeatedly, indefinitely:
c = itertools.cycle(['a', 'b', 'c'])
for i in range(9):
    print(next(c)) 
# a
# b
# c
# a
# b
# c
# a
# b
# c


# permutations: yield permutations of a given length of items from the given iterable. 
# The length of the permutations is by default the length of the iterable.
p = itertools.permutations(['a', 'b', 'c'])
print(list(p))
# [('a', 'b', 'c'), ('a', 'c', 'b'), 
#  ('b', 'a', 'c'), ('b', 'c', 'a'), 
#  ('c', 'a', 'b'), ('c', 'b', 'a')]

# If don't specify a length, for an iterable of length n - returns n! items (3! = 6 above)

p = itertools.permutations(['a', 'b', 'c'], r=1)
print(list(p)) # [('a',), ('b',), ('c',)]

p = itertools.permutations(['a', 'b', 'c'], r=2)
print(list(p)) # [('a', 'b'), ('a', 'c'), ('b', 'a'), ('b', 'c'), ('c', 'a'), ('c', 'b')]

# cf: number of combinations:
c = itertools.combinations(['a', 'b', 'c'], r=2)
print(list(c)) # [('a', 'b'), ('a', 'c'), ('b', 'c')]

# Permutations effectively gives the permuations of combination of the same length 
c = itertools.combinations(['a', 'b', 'c'], r=2)
l = [next(c) for i in range(3)]
p = [tuple(itertools.permutations(it)) for it in l]
print('\nPermuations - permute each combo')
print(p) # [(('a', 'b'), ('b', 'a')), (('a', 'c'), ('c', 'a')), (('b', 'c'), ('c', 'b'))]


p = itertools.permutations(['a', 'b', 'c'], r=4)
print(list(p)) # [] - no combinations of length 4, so only "1" permuatation


# Number of permuations of sub-lists of length k drawn from list of n items is:
# (n choose k) items, each with k! perumations - so (n choose k) * k! = (n!/k!(n-k)! * k!) = n!/(n-k)!
# i.e. (n-k+1)*(n-k+2)*...*(n-1)*n

# e.g. n=5, k=3 below: # perms is 3*4*5=60
p = itertools.permutations(range(5), r=3)
print(len(list(p))) # 60

# Or above, had n=3, k=2: 2*3 = 6 (or: 3!/1! = 3! = 6)


# repeat: yield the given item repeated, or a specified number of times
c = itertools.repeat('a', times=3)
print(list(c)) # ['a', 'a', 'a']

c = itertools.repeat(['a', 'b'])
l = [next(c) for i in range(5)]
print(l) # [['a', 'b'], ['a', 'b'], ['a', 'b'], ['a', 'b'], ['a', 'b']]

# repeat is useful if need to provide a fixed argument for map:
c = map(lambda x, y: x*y, range(1, 11), itertools.repeat(5))
print(list(c)) # [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]


## Rearranging generators

# groupby: yields tuples of the form (key, value) where the value comes from the provided iterator, and
# key is generated based on the value (default is None)
c = itertools.groupby([1,2,3,4,5], key=lambda x: 'Odd' if x%2 else 'Even')

for key, value in c:
    print(key, list(value))

# Odd [1]
# Even [2]
# Odd [3]
# Even [4]
# Odd [5]

for key, value in itertools.groupby('ABBCCC'):
    print(key, list(value))
# A ['A']
# B ['B', 'B']
# C ['C', 'C', 'C']

for key, value in itertools.groupby(['a', 'b', 'c', 'aa', 'ab', 'acb'], len):
    print(key, list(value))
# 1 ['a', 'b', 'c']
# 2 ['aa', 'ab']
# 3 ['acb']

# Note: for groupby to "aggregate" as above, need items to be in the order of the keys:
for key, value in itertools.groupby(['a', 'b', 'c', 'aa', 'abc', 'ab'], len):
    print(key, list(value))
# 1 ['a', 'b', 'c']
# 2 ['aa']
# 3 ['abc']
# 2 ['ab'] - doesn't get bundled into the 2 category above

# This is why the odd/even example above doesn't work, but the below does:
for key, value in itertools.groupby([1, 3, 5, 2, 4], key=lambda x: 'Odd' if x%2 else 'Even'):
    print(key, list(value))
# Odd [1, 3, 5]
# Even [2, 4]


# tee: yields a tuple of a given number of generators, each yielding the items of the input iterable independantly
c = itertools.tee(['a', 'b', 'c'], 4)
print(c) # (<itertools._tee object at 0x7f96c7b786c8>, <itertools._tee object at 0x7f96c7b78688>, <itertools._tee object at 0x7f96c7b78708>, <itertools._tee object at 0x7f96c7b78748>)
print(c[0]) # <itertools._tee object at 0x7fef0df787c8>
print(list(c[0])) # ['a', 'b', 'c']
print(list(c[1])) # ['a', 'b', 'c']
print(list(c[2])) # ['a', 'b', 'c']
print(list(c[3])) # ['a', 'b', 'c']

# c still exists - but it's now a tuple of exhausted generators:
try:
    next(c[2])
except Exception as e:
    print(repr(e)) # StopIteration()
    
# So tee essentially creates a bunch of copies of the input generator (by default creates 2)
print(len(itertools.tee(['a', 'b', 'c']))) # 2


# The 'yield from' syntax yields elements from the provided iterable - so we can iterate over
# several iterables and 'yield from' each one, rather than needing a second iteration over the
# provided outer iterable

# e.g. consider:

def f(*iterables):
    
    for iterable in iterables:
        for it in iterable:
            yield it


c = f(range(3), ['a', 'b'])
print(list(c)) # [0, 1, 2, 'a', 'b']

# We can replace that with:

def f(*iterables):
    for iterable in iterables:
        yield from iterable
        
c = f(range(3), ['a', 'b'])
print(list(c)) # [0, 1, 2, 'a', 'b']

# Or consider the difference:

def f():
    for item in [['a', 'b'], ['c','d']]:
        yield item

def g():
    for item in [['a', 'b'], ['c','d']]:
        yield from item
    
print(list(f())) # [['a', 'b'], ['c', 'd']]
print(list(g())) # ['a', 'b', 'c', 'd']

# 'yield from' creates a channel connecting the consumer of the outer generator with the inner generator,
# as is more than mere syntactic sugar


# Now more generators from the Standard Library
## Reducing Generators

# These accept iterables and apply aggregation of reduction to them

# all, any: returns true if all, any items in the iterable are truthy
print(all([1,True, "s", [1,2]])) # True
print(any([0, False, []])) # False
print(any([0, False, [], [[]]])) # True - empty list is Falsey, but list containing an empty list is Truthy
print(all([1, True, []])) # False

g = (n for n in [0,1,2])
print(any(g)) # True
print(list(g)) # [2] - any seems to have exhausted all but the last elemnent of g


# max: returns max elemnt in the iterable, based on an optional key; 
# empty iterables return an optional default value
print(max([], default = 'hi')) # hi
print(max([2,1,3])) # 3
print(max([2,1,3], key = lambda x: -x)) # 1

# min: as above, but for min value
print(min([], default = 'hi')) # hi
print(min([2,1,3])) # 1
print(min([2,1,3], key = lambda x: -x)) # 3

# sum: adds all elements of the iterable, to an optional start value
print(sum({1,2,3}, 10)) # 16
g = arith_prog_gen(1, 1, 5)
print(sum(g)) # 15: 1+2+3+4+5 = 15
try:
    next(g)
except Exception as e:
    print(repr(e)) # StopIteration() - sum consumers the generator
    
    
# reduce: applyies a given function successively over the items of the iterable (strarting with the first
# pair of item, but can specify an initial value) 
import functools

c = functools.reduce(lambda x,y: x+y, ['a', 'b', 'c'], 'z')
print(c) # zabc


# We can use the iter function on a callable function (with no args), to produce an iterator 
# that repeated calls the callable, until some given "sentinel" value is returned - 
# at which point the iterator terminates
import random

def dice_roll():
    return random.randint(1,6)

d = iter(dice_roll ,1) 
print(d) # <callable_iterator object at 0x7f73d72ac2e8>
for i in range(5):
    try:
        print(next(d))
    except StopIteration:
        break

# But note: the sentinel value is required
try:
    d = iter(dice_roll)
except Exception as e:
    print(repr(e)) # TypeError("'function' object is not iterable")
    
# But it is valid to provide a sentinel value that the function will never return - in which case 
# it can be "iterated" over indefinitely (although can't see a use-case here where this is better
# than simply repeated calling the function directly)
def f():
    return 2

g = iter(f, 1)
for i in range(5):
    print(next(g))
    
# An example using the sentinel value might be to iterate over the lines of a file, until you hit, say,
# an empty line ''