"""Chatper 7 - Function Decorators and Closures [p183]"""

# A decorator is a callable that takes another function (the decorated function) as its argument.

# Create a decorator
def deco(func):
    def inner():
        print("Running inner()")
    return inner

# Apply to other functions with the @ syntax:
@deco
def target():
    print("Running target")
    
print(target()) # "Running inner()"

def target_2():
    print("Running target")
 
print(target_2()) # "Running target"   

# The decorated function is equivalent to:
target_2 = deco(target_2)
print(target_2()) # "Running inner()"

# That is, the result is new function:
tar_dec = target
print(tar_dec) # <function deco.<locals>.inner at 0x7f7baf8dbe18>
tar_dec() # Also prints "Running inner()"

# Note the decorated function is actually a refernce to the inner() function inside deco().

# Also: decorators are run as soon as the decorated function is defined - usually at import time, when loading modules
print("\n Import Registration:")
import registration

# The above prints the output of decorating f1 and f2 in the registration.py module:
# Running register(<function f1 at 0x7f1af79b7a60>)
# Running register(<function f2 at 0x7f1af79b7b70>)

print(registration.registry)
registration.main()

# Note: decorators are more usually created in one module, then used in another. And they typically define some inner 
# function, then return that (as in deco() above, vs register() in registrations.py)

# Note: the register() decorator in registration could be used to populate a list of promotion functions, 
# from the previous chapter (where we had to inspect globals()) - we would simply decorate all the individual
# promotion functions. The promotions module could then have several other functions (e.g. best_promo()), and
# if we don't want to add them to the promotions list, we simply don't decorate them. The promotions functions
# don't require any special names etc (e.g. _promo as in Chapter 6) - they just need to be decorated.

# Recall function scoping - can't used previously-undefined variables in a function:

def f1(a):
    print(a)
    print(b)

try:
    f1(2)
except Exception as e:
    print(type(e), e) # <class 'NameError'> name 'b' is not defined

# But if we now define b, can call f1 with no problem:
b =3
f1(2)

# However, if we try to assign b within a function after using it within that same function, Python complains
# that we used it without assigning it:

def f2(a):
    print(a)
    print(b)
    b=5

try:
    f2(2)
except Exception as e:
    print(type(e), e) # <class 'UnboundLocalError'> local variable 'b' referenced before assignment
    
# This happens because Python compiles the body of the function, it decides b is a local variable.
# If it didn't do this, the below would inadervantly change the value of the global x:
x=5
def f3(x):
    x=1
    print(x)
f3(2) # prints 1
print(x) # still 5 - as expected

# We can declare b to be global within the function - and it will use the global object, but can also change that object:

print("\nTest global:")
b=3
def f4(a):
    global b
    print(a)
    print(b)
    b=5
f4(1) # prints 1 then 3, as expected
print(b) # b is now 5, rather than 3 since the function body was working on the global object b 

# Can compare the bytecode of f2 and f4:
from dis import dis
print("\nf2 bytecode:")
print(dis(f2))

print("\nf4 bytecode:")
print(dis(f4))


# A closure is an extended function, that encompasses nonglobal functions referenced within the body of the function, but 
# not defined there.
# E.g. consider an avg(x) function that keeps a running average of all values x it has received over all the times
# it was called, i.e.:
# avg(1) = 1
# avg(2) = 1.5
# avg(3) = 2

# We could implement this using a class that keeps a record of all values it has been called with:
class Averager():
    
    def __init__(self):
        self.series = []
    
    def __call__(self, value):
        self.series.append(value)
        return sum(self.series)/len(self.series)
    
print("\nTest Averager class:")
avgr = Averager()
print(avgr(1)) # 1.0
print(avgr(2)) # 1.5
print(avgr(3)) # 2.0
print(avgr.series) # [1, 2, 3]

# Alternatively we can use functions, with a make_averager closure function:
def make_average():
    series = []
    def averager(value):
        series.append(value)
        return sum(series)/len(series)
    return averager

print("\n Test make_averager():")
avgr_fn = make_average()
print(avgr_fn) # <function make_average.<locals>.averager at 0x7f41b324b9d8>
print(avgr_fn(1)) # 1.0
print(avgr_fn(2)) # 1.5
print(avgr_fn(3)) # 2.0
print(avgr_fn) # <function make_average.<locals>.averager at 0x7f41b324b9d8> - note same as when originally created

# The make_average() function returns its inner function, the averager() - which is mapped only at invokation (i.e. avgr_fn = make_average())
# Subsequent /calls/ to this function are in fact calls to the inner function - hence it doesn't get re-created with each call (and so
# remains at the same location in memory)
    
# However: where does it get the series variable from?
# This was a local variable in the scope of make_averager(), but was then used as a "free variable" in the average() 
# inner function - i.e. a variable not bound to local scope. 
# Of course, it's not a global variable:
try: 
    print(series)
except Exception as e:
    print(type(e), e) # <class 'NameError'> name 'series' is not defined
    
# However, Python specifically keeps track of such free variables within the function object:
print(avgr_fn.__code__.co_varnames) # ('value',)
print(avgr_fn.__code__.co_freevars) # ('series',)

# The binding for series is kept inside the __closure__ attribute of the function:
print(avgr_fn.__closure__[0].cell_contents) # [1, 2, 3]

print(avgr_fn(4)) # 2.5
print(avgr_fn.__closure__[0].cell_contents) # [1, 2, 3, 4]


# An alternative approach would simply keep track of a running sum and count, rather than storing they entire history
# of args (i.e. series above). However we can fall into a trap:

def make_averager_alt():
    count = 0
    total = 0
    def averager(x):
        count += 1
        total += x
        return total/count
    return averager

avgr_alt = make_averager_alt()
try:
    print(avgr_alt(1))
except Exception as e:
    print(type(e), e) # <class 'UnboundLocalError'> local variable 'count' referenced before assignment
    
# Within averager, "count" is treated as a local variable - since "count += 1" translates to "count = count + 1" 
# (since integers as immutable). Hence it is instantiated within averager, and is thus a local variable.

# For the above to work, we need to declare count (and total) as explicitly "nonlocal" (analogous to the global 
# declaration above):
def make_averager_alt():
    count = 0
    total = 0
    def averager(x):
        nonlocal count
        nonlocal total
        count += 1
        total += x
        return total/count
    return averager

avgr_alt = make_averager_alt()
print(avgr_alt(1)) # 1.0
print(avgr_alt(2)) # 1.5
print(avgr_alt(3)) # 2.0

# Note: the version using series above didn't face this problem, since series was a (mutable) list.

# Nonlocal flags the variable as a free variable, rather than a local one:
print(avgr_alt.__code__.co_varnames) # ('x',)
print(avgr_alt.__code__.co_freevars) # ('count', 'total')

# The values are stored within the __closure__ object:
print(avgr_alt.__closure__[0].cell_contents) # 3 - the count
print(avgr_alt.__closure__[1].cell_contents) # 6 - the total

print(avgr_alt(4)) # 2.5
print(avgr_alt.__closure__[0].cell_contents) # 4
print(avgr_alt.__closure__[1].cell_contents) # 10

# Implementing a Simple Decorator: below is a decorator that times the functions it decorates, 
# and records info on them (e.g. their args)
import time

def clock(func):
    def clocked(*args):
        """Calc how long the decorated function takes to run"""
        t0 = time.perf_counter()
        result = func(*args)
        elapsed = time.perf_counter() - t0
        name = func.__name__
        arg_str = "".join(repr(arg) for arg in args)
        print('[%0.8fs] %s(%s) -> %r' % (elapsed, name, arg_str, result))
        return result
    return clocked

# Note: the closure for clocked (i.e. clock) contains func as a free variable - hence we can call func within clocked

# So decorating a function with clock() will return the inner clocked function - which itself returns the result of running
# the decorated function, but also prints the data about the function too.
# This is a quintessential use case for decorators - amend the decorated function with additional functionality

@clock
def sum_to_n(n):
    """Sum the numbers from 1 to n"""
    total = 0
    for i in range(1,n+1):
        total += i
    return total

print("\nTest clock decorator")
print(sum_to_n) # <function clock.<locals>.clocked at 0x7f08fe3fec80>
sum_to_n(10**3) # [0.00000460s] sum_to_n(10) -> 55

# However, the clock decorator above masks the __name__ and __doc__ information:
print(sum_to_n.__name__) # clocked
print(sum_to_n.__doc__) # "Calc how long the decorated function takes to run" - i.e. the docstring of clocked (clock's inner function) 

# Also, it doesn't handle keyword args.

# Can fix the name & doc problems by using the @wraps decorator on the innter function:
from functools import wraps

def clock_alt(func):
    @wraps(func)
    def clocked_alt(*args, **kwargs):
        """Calc how long the decorated function takes to run"""
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        name = func.__name__
        arg_lst = []
        
        if args:
            arg_str = arg_lst.append(", ".join(repr(arg) for arg in args))
        
        if kwargs:
            pairs = ['%s=%r' % (k, w) for k, w in sorted(kwargs.items())]
            arg_lst.append(", ".join(pairs))
        
        arg_str = ", ".join(arg_lst)
        
        print('[%0.8fs] %s(%s) -> %r' % (elapsed, name, arg_str, result))
        return result
    return clocked_alt

@clock_alt
def sum_n_m(n, m):
    """Sum numbers from n to m"""
    total = 0
    for i in range(n, m+1):
        total += i
    return total

print("\n Test clock_alt decorator")
print(sum_n_m) # <function sum_n_m at 0x7f48b67fde18> - note: no longer has no of inner function, but of the decorated function
sum_n_m(1, 10) # [0.00000370s] sum_n_m(1, 10) -> 55
sum_n_m(1, m = 10) # [0.00000290s] sum_n_m(1, m=10) -> 55

print(sum_n_m.__name__) # "sum_n_m"
print(sum_n_m.__doc__) # "Sum numbers from n to m"

# Other decorators in the standard library, for use with Classes, are: @property, @classmethod and @staticmethod

# Another decorator in functools is lru_cache - which implements memoisation, i.e. storing previous results of
# expensive functions, to avoid re-calculating them. 
# lru stands for "least recently used" - the cache is pruned over time by removing the values used least frequently over
# recent iterations.

# Consider the naive implementation of a Fibonacci sequence generator below:
@clock_alt
def fibonacci(n):
    """Generates nth Fibonacci number"""
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("\nNaive Fibonacci:")
fibonacci(6)

# This approach calls itself multiple times e.g. fibonacci(3) is called 3 times.

# But decorating with lru_cache can solve this:
from functools import lru_cache

@lru_cache()
@clock_alt
def fibonacci(n):
    """Generates nth Fibonacci number"""
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("\nFibonacci with lru_cache:")
fibonacci(6)

# Note stacking decorators as in:
# @dec1
# @dec2
# def f():
# is equivalent to applying them from bottom to top:
# f = dec1(dec2(f))

# So @lru_cache() above applies to the function returned by @clock.
# @lru_cache() is called as a function, as it can take configuration params: maxsize and typed
# maxsize determines the max size of the cache - default is 128
# If typed=True (default: False), stores the result of different types separately (e.g. int vs float) 

# Note that the args taken by the decorated function must be hashable, since the cache is stored as a dict,
# with the decorated function's args as keys.


# Another standard library decorator is @singledispatch. Decorating a plain function with @singledispatch
# will turn it into a generic function - which allows a group of functions to perform the same task in different
# ways, depending on the type of the first arg. I.e. a form of overloading.
# Note: "single" dispatch refers to the fact that only the first arg determines which function is used.

# E.g. consider htmlize below which adds html tags to different types in different way:

from functools import singledispatch
from collections import abc
import numbers
import html

# Base function, to handle the object type:
@singledispatch
def htmlize(obj):
    content = html.escape(repr(obj))
    return "<pre>{}</pre>".format(content)

# htmlize for strings - the name below is irrelevant, so "_" chosen to emphasise that
@htmlize.register(str)
def _(text):
    content = html.escape(text).replace('\n', '<br>\n')
    return '<p>{0}</p>'.format(content)

# And for integers:
@htmlize.register(numbers.Integral)
def _(n):
    return '<pre>{0} (0x{0:x})</pre>'.format(n)

# Can apply same function to multiple types by stacking their decorator - i.e. tuples and mutable sequences below:
@htmlize.register(tuple)
@htmlize.register(abc.MutableSequence)
def _(seq):
    inner = '</li>\n<li>'.join(htmlize(item) for item in seq)
    return '<ul>\n<li>' + inner + '</li>\n</ul>'

print("\nTest htmlize:")
print(htmlize(abs)) # <pre>&lt;built-in function abs&gt;</pre> - base: object
print(htmlize("abs")) # <p>abs</p> - string
print(htmlize(10)) # <pre>10 (0xa)</pre> - integer

print(htmlize(["a", "b", "c"]))
# List above gives:
# <ul>
# <li><p>a</p></li>
# <li><p>b</p></li>
# <li><p>c</p></li>
# </ul>

print(htmlize((1,2,3)))
# Tuple above gives:
# <ul>
# <li><pre>1 (0x1)</pre></li>
# <li><pre>2 (0x2)</pre></li>
# <li><pre>3 (0x3)</pre></li>
# </ul>

# Note: the alternative the @singledispatch would be to create htmlize as a dispatch function that calls
# the desired specific verison, depending on type - htmlize_str, htmlize_int etc...
# However if users can't modify this code, then they can't extend with their own types if needed - they'd 
# need to create their own wrapper on top of the base htmlize. Awkward and inconvenient.
# Whereas they can extend the base htmlize by using the @htmlize.register on their own type implementation

# Note that we used the abstract classes for types above - numbers.Integral, abc.MutableSequence vs (say) int & list
# - so as to cover the widest possible range of types. E.g. if the user subtypes numbers.Integral with their own
# smaller-bit versions of int.


# Note: decorators typically take the decorated function as its argument - via def dec(func).
# But we can create parameterised decorators that take params as arguments of their own (as in @lru_cache). 
# This is done by creating a decorator factory, which takes these params as its argument, and returns a decorator
# But we must call this decorator factory as a function, for it to then return the actual decorator function itself.
# See example below, for decorator that registers which function's it decorates

registry = set()

def register(active=True):
    """The decorator factory"""
    def decorate(func):
        """The decorator itself"""
        print('running register(active=%s)->decorate(%s)' % (active, func))
        
        if active:
            registry.add(func)
        else:
            registry.discard(func)
        
        return func
    return decorate

@register(active=False)
def f1():
    print('running f1()')

@register()
def f2():
    print('running f2()')

def f3():
    print('running f3()')
    
f1()
f2()
f3()
print(registry) # {<function f2 at 0x7fabd82b21e0>}

# We can remove f2 from the registry by calling the register function on it, with active False:
register(active=False)(f2)

# Or we can add f3 to it, in the same way with active True:
register(active=True)(f3)
print(registry) # {<function f3 at 0x7f4fcaf47d90>}


# Parameterised clock decorator [p209] - we can modify the @clock decorator to accept a user-specified format string

DEFAULT_FMT = '[{elapsed:0.8f}s] {name}({args}) -> {result}'

def clock_alt_2(fmt=DEFAULT_FMT):   # clock() is a parameterised decorator factory
    def decorate(func):
        def clocked(*_args):
            t0 = time.time()
            _result = func(*_args)
            elapsed = time.time() - t0
            name = func.__name__
            args = ", ".join(repr(arg) for arg in _args)
            result = repr(_result)
            print(fmt.format(**locals())) # locals() allows any local variable of clocked to be used in the format string
            return _result
        return clocked
    return decorate
      
# Test it:
print("\nTest clock_alt_2")

@clock_alt_2() # Note: need to use as a callable
def snooze(seconds):
    time.sleep(seconds)

for i in range(3):
    snooze(0.0123)
    
# Try alternative format string:
@clock_alt_2("{name}:{elapsed}s") # Note: need to use as a callable
def snooze(seconds):
    time.sleep(seconds)

for i in range(3):
    snooze(0.0123)
    
# Can reference any local variable in clocked(), in the format string:
@clock_alt_2("The result is: {result}") # Note: need to use as a callable
def times_2(n):
    return 2 * n

for i in range(1, 11):
    times_2(i)
    
    
# Extra material from: 
# https://github.com/GrahamDumpleton/wrapt/blob/develop/blog/01-how-you-implemented-your-python-decorator-is-wrong.md

# Note: decorators can also be implemented as classes, instead of as function closures.
class function_wrapper(object):
    
    def __init__(self, wrapped):
        self.wrapped = wrapped
    
    def __call__(self, *args, **kwargs):
        print("This function is decorated!")
        return self.wrapped(*args, **kwargs)

print("\nTest Class version of decorator")
@function_wrapper
def f(x):
    """Doubles input"""
    return 2*x

f(1)
f(2)

print(type(f)) # <class '__main__.function_wrapper'>
print(f.wrapped) # <function f at 0x7f9c90c080d0> - gets the wrapped function
print(f.wrapped.__name__) # f
print(f.wrapped.__doc__) # "Doubles input"

# So f is actually an instance of the class function_wrapper, and calling it is actually invoking that 
# class' __call__() method.

# Note that functools' @wraps or @update_wrapper fail if applied to a class method that is also decorated 
# with @classmethod or @staticmethod - as wrappers created by these latter decorators don't have some of the attribs 
# being decorated.

class Class(object):
    
    @function_wrapper
    @classmethod
    def cmethod(cls):
        pass

c = Class()
try:
    c.cmethod()
except Exception as e:
    print(type(e), e) # <class 'TypeError'> 'classmethod' object is not callable
