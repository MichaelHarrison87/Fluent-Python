# Chapter 05 - First Class Functions [p139]

# Functions in Python are first-class objects, meanining a program entity that can be:
# - Created at runtime
# - Assigned to a variable or element of a data structure
# - Passed as an argument to a function
# - Returned as a result of a function

# Other examples of first-class objects are integers, strings, dicts, lists etc.

# So functions are Python objects, with properties we can use:
def factorial(n):
    """Returns n! """
    return 1 if n < 2 else n * factorial(n-1)

print(factorial(5), 5*4*3*2*1)
print(factorial.__doc__) # print the docstring
print(type(factorial)) # <class 'function'> - as expected

# We can assign functions to variables:
fact = factorial
print(fact(5)) # 120 
print(type(fact)) # <class 'function'

# And can pass functions as variables in other functions:
l = map(factorial, [1,2,3,4,5])
print(l) # map object
print(list(l))

# First class functions allow for a functional programming style.

# Higher-Order Functions take functions as arguments, and return functions as results.

# E.g. sorted - can specify functions as the key keywork:
fruits = ["fig", "strawberry", "apple"]
print(fruits)
print(sorted(fruits)) # alphabetical
print(sorted(fruits, key=len)) # pass len() function to sort by length

# Python has equivalents of the common functonal functions map, filter & reduce
# However can often achieve the same result with better clarity using listcomps
# Consider - getting factorials of odd numbers between 1 and 5:
l1 = map(factorial, filter(lambda x: x % 2, range(1, 6)))
print(list(l1))

l2 = [factorial(x) for x in range(1,6) if x % 2]
print(l2)

# Note that map and filter return generators - the below prints nothing since list(l1) above exhausted the generator
print("Print Map - Pre-Refresh")
for i in l1:
    print(i)
    
l1 = map(factorial, filter(lambda x: x % 2, range(1, 6))) # refresh the generator
print("Print Map - Post-Refresh")
for i in l1:
    print(i)
    
# The reduce function is available in the functools package (it's not a built-in), and is used to aggregate over iterables:
from functools import reduce
from operator import add

print(reduce(add, range(101)))
print(sum(range(101)))

# all() and any() can be used for boolean comparison over iterables
print(all([i % 2 for i in range(6)])) # Checks if all are even - False
print(any([i % 2 for i in range(6)])) # Checks if any are even - True

# Anonymous functions are small one-off functions that don't need to be created as a fully-fledged object, e.g. a sorted() key or map() function
# They're created using the keyword "lambda"

# E.g. sort words by their alphabetical order when spelled backwards:
fruits = ['strawberry', 'fig', 'apple', 'cherry', 'raspberry', 'banana']
print(fruits)
print(sorted(fruits))
print(sorted(fruits, key = lambda x: x[::-1]))

# Anonymous functions are used pretty much exclusively as arguments to higher-order functions, in the manner above

# There are 7 types of callable object in Python:

# User-define function - created with def or lambda
# Built-in functions - implemented in C e.g. len, str
# Built-in methods - implemented in C e.g. dict.get()
# Methods - functions contained inside a class
# Classes - when call, classes run their __new__ method to create an instance, then __init__ to initialise it, 
# then return the instance to the caller. Although its possible to override __new__ method to get other behavious
# Class Instances - if the class has a __call__ method, can use its instances as functions
# Generator Functions - functions/methods that use the yield key word (vs return). Return a generator object

# The built-in function callable() lets us test if an object is callable:
for i in [abs, str, 13]:
    print(i, callable(i))

    
# User-Defined Callable Types - we can make arbitrary Python objects into functions, simply by implementing 
# a  __call__ instance method.
import random

class BingoCage:
    
    def __init__(self, items):
        self._items = list(items) # item can be any iterator; make an internal copy to avoid unintended side-effects on the inputted list
        random.shuffle(self._items)
    
    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError("Bingo Cage is empty!")
    
    def __call__(self):
        return self.pick()
    
bingo = BingoCage(range(3))
print(bingo.pick())
print(bingo())
print(bingo())

# This is a good way to create function-like objects that have some internal state that needs to persist across calls
# e.g. the remaining items inside the bingo cage. Or decorators that "remember" intermediate results for memoisation
# This approach serves as an alternative to Closures - which are also functions that remember internal state.

# We can compare the list of standard attributes functions have, that bare class instances don't:
class C: pass
obj = C()
def func(): pass
func_diffs = sorted(set(dir(func)) - set(dir(obj)))
print(func_diffs)
# Result: ['__annotations__', '__call__', '__closure__', '__code__', '__defaults__', 
#          '__get__', '__globals__', '__kwdefaults__', '__name__', '__qualname__']

# We can use * and ** to "explode" iterables out into function arguments
# * is used for positional arguments
# ** is used for keyword args

def tag(name, *content, cls=None, **attrs):
    """ Generate one or more HTML tags"""
    if cls is not None:
        attrs["class"] = cls
    
    if attrs:
        attr_str = "".join(" %s='%s'" % (attr, value) for attr, value in sorted(attrs.items()))
    else:
        attr_str = ""
        
    if content:
        return "\n".join("<%s%s>%s</%s>" % (name, attr_str, c, name) for c in content)
    else:
        return "<%s%s />" % (name, attr_str)
     
print(tag("br")) # <br /> - no content, cls, or keyword args
print(tag("p", "hello")) # <p>hello</p> - wrap the one-word content "hello" in p tags

print(tag("p", "hello", "there", "world")) # But content can be an arbitrary number of positional args
# Result:
# <p>hello</p>
# <p>there</p>
# <p>world</p>

print(tag("p", "hello", id=33)) # <p id='33'>hello</p> - arbitrary keyword args are captured in attrs
print(tag("p", "hello", "world", cls="sidebar")) # To use the cls keyword, have to explicitly use it in the function args
# Result:
# <p class='sidebar'>hello</p>
# <p class='sidebar'>world</p>

print(tag(content='testing', name="img")) # <img content='testing' /> - can use the first positional argument as a keyword

my_tags = {'name': 'img', 'title': 'Sunset Boulevard', 'src': 'sunset.jpg', 'cls': 'framed'}
print(tag(**my_tags)) # <img class='framed' src='sunset.jpg' title='Sunset Boulevard' /> - dict interpreted as keyword args - keys as keywords, values as param values

# Note that cls is a keyword-only argument: it'll never be specified by a positional-only argument, since it follows 
# the argument prefixed with * (i.e. *content)  

# Can use a free-standing * to specify keyword-only argument without having variable numbers of positional args:
def f(a, *, b):
    return a+b

print(f(1, b=2))

try:
    f(1,2)
except Exception as e:
    print(e)
    
# Retrieving Info about Parameters
# Within a function, the __defaults__ attribute holds info on the default values of positional and keyword args,
# while __kwdefaults__ is the same, but for keyword-only args
def f(a, b=1, c=2, *args, d=3, **kwargs): pass

print("defaults:", f.__defaults__)
print("kwdefaults:", f.__kwdefaults__)

# The __code__ attribute contains other information such as variable names, number of args etc
def clip(text, max_len=80):
    """Return text clipped at last space before or after max_len"""
    end = None
    if len(text) > max_len:
        space_before = text.find(" ", 0, max_len)
        if space_before >= 0:
            end = space_before
        else:
            space_after = text.find(" ", max_len)
            if space_after >= 0:
                end = space_after
    
    if end is None: # no spaces
        end = len(text)
    return text[:end].rstrip()

print(clip.__defaults__)
print(clip.__code__)
print(clip.__code__.co_varnames)
print(clip.__code__.co_argcount)
 
 # Can get the arg name of a function from the first N elements of __code__.co_varnames - where N = __code__.co_argcount
print("clip args:", clip.__code__.co_varnames[:clip.__code__.co_argcount])

# However, __code__.co_argcount doesn't count any args preceded by * or **
print("f args - full:   ", f.__code__.co_varnames)
print("f args - counted:", f.__code__.co_varnames[:f.__code__.co_argcount])

# Note that for clips above, we must /infer/ that max_len corresponds to the default 80 - as with 2 args and 1 default, 
# the default must correspond to the last arg.

# However the inspect package provides the same functionality, more conveniently
from inspect import signature
sig = signature(clip)  
print("clip signature:", sig)
print("clip signature:", str(sig))

print("Insepct clip:")
for name, param in sig.parameters.items():
    print(param.kind, ":", name, " = ", param.default)
    
print("Insepct f:")
sig = signature(f) 
for name, param in sig.parameters.items():
    print(param.kind, ":", name, " = ", param.default)
    
# inspect.Signature has a bind() method that allows us to bind any number of arguments (to bind()) to the function signature
sig = signature(tag)
bound_args = sig.bind(**my_tags)
print(bound_args.arguments)

# Now remove an item from my_tags:
del my_tags["name"]
try:
    bound_args = sig.bind(**my_tags) # missing a required argument: 'name'
except Exception as e:
    print(type(e), e)
    
# Function Annotation - lets us attach metadata to the params of a function declaration, and its return value
# e.g. an annotated version of the clip function is below:
def clip_annotate(text: str, max_len:"int > 0"=80) -> str: # -> annotates the return type
    """Return text clipped at last space before or after max_len"""
    end = None
    if len(text) > max_len:
        space_before = text.find(" ", 0, max_len)
        if space_before >= 0:
            end = space_before
        else:
            space_after = text.find(" ", max_len)
            if space_after >= 0:
                end = space_after
    
    if end is None: # no spaces
        end = len(text)
    return text[:end].rstrip()

# The annotations are stored in a function attribute:
print(clip_annotate.__annotations__)

# However, these annotations are not enfored, checked, validated etc - they don't mean anything to Python's interpreter:
print(clip_annotate("hi there", max_len=-1)) # no issue with max_len < 0  


# The Python standard library contains modules that support a functional style of programming

# For instance, the operator module lets us use arithmetical operators as functions (as above, with add).
# E.g. the below calcultes the factorial
from operator import mul
def fact(n):
    return reduce(mul, range(1, n+1))

print(fact(5))

# Could have also used a lambda:
def fact_alt(n):
    return reduce(lambda a, b: a*b, range(1, n+1))
print(fact_alt(5))

# Operator also has itemgetter and attrgetter to support picking items from sequences, or getting attributes from objects
from operator import itemgetter, attrgetter

# These can replace lambdas, similar to above. E.g. sorting a list of tuples, by the value of one field
# itemgetter(1) is equiv to lambda fields: fields[1
metro_data = [
 ('Tokyo', 'JP', 36.933, (35.689722, 139.691667)),
 ('Delhi NCR', 'IN', 21.935, (28.613889, 77.208889)),
 ('Mexico City', 'MX', 20.142, (19.433333, -99.133333)),
 ('New York-Newark', 'US', 20.104, (40.808611, -74.020386)),
 ('Sao Paulo', 'BR', 19.649, (-23.547778, -46.635833)),
 ]

# Print data in city alphabetical order
print("Metro Data by City:")
for city in sorted(metro_data, key = itemgetter(0)):
    print(city)

# cf the lambda equivalent:
print("Metro Data by City:")
for city in sorted(metro_data, key = lambda x: x[0]):
    print(city)

# Print data in country alphabetical order
print("Metro Data by Country:")
for city in sorted(metro_data, key = itemgetter(1)):
    print(city)
    
# Can pass multiple args to itemgetter to extract multiple items:
for city in metro_data:
    print(itemgetter(1,0,2)(city))
    
# attrgetter works similarly, but extracts attribtutes using its arg list as names. It can
# also navigate through nested objects to get the attribute
from collections import namedtuple
LatLong = namedtuple('LatLong', 'lat long')
Metropolis = namedtuple('Metropolis', 'name cc pop coord')
metro_areas = [Metropolis(name, cc, pop, LatLong(lat, long)) for name, cc, pop, (lat, long) in metro_data]
print("Metro Areas:")
for area in metro_areas:
    print(area, area.coord, area.coord.lat) # have to "delve" to get to the lat attribute
    
# Using attrgetter - can create a function to extract desired attributes:
name_lat = attrgetter("name", "coord.lat")
print("Get lats:")
for area in sorted(metro_areas, key=attrgetter("coord.lat")): # sort metro data by latitude
    print(name_lat(area)) # apply the name_lat function to extract name and coord.lat attributes
    
# methodcaller, also in the operator package, creates functions that call the given method:
from operator import methodcaller
s = "My String"
upper = methodcaller("upper")
print(s) 
print(upper(s)) 

# We can also supply method arguments to freeze them in each use - called "partial application":
rep = methodcaller("replace", " ", "-")
print(rep(s))

# Partial application can also be done with the functools.partial function:
from functools import partial

# E.g. use a two-argument function where a one-arg function is required:
triple = partial(mul, 3)
print(triple(4)) # 12
print(list(map(triple, range(1,11)))) # not mul wouldn't have worked with map here

# Another example: if we need to normalise unicde with "NFC" frequently, we can partially-apply the unicodedata.normalize function
from unicodedata import normalize
nfc = partial(normalize, "NFC")
s1 = 'café'
s2 = 'cafe\u0301'
print(s1, s2) # visually identical
print(s1 == s2) # False - different unicode code point
print(nfc(s1) == nfc(s2)) # True - code points normalised

# Can partially-apply multiple arguments (including keywords):
picture = partial(tag, "img", cls="pic-frame")
print(picture(src="wumpus.jpg")) # <img class='pic-frame' src='wumpus.jpg' />

# The partial object pictures contains various metadata:
print(picture)
print(picture.func)
print(picture.args)
print(picture.keywords)

# Note: .func provides access to original underlying function:
mul2 = triple.func
print(mul2(2,3), type(mul2)) # 6