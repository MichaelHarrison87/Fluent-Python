# Chapter 16 - Coroutines [p463]

# In PEP 342, the .send(value) method was added to the generator API, allowing the caller of the 
# generator to post data that then becomes the value of the yield expression inside the generator
# function.

# This allowed generators to be used a coroutines: a procedure that collaborates with the caller, both yielding
# and receiving values from them

# There's also the .throw() method to throw an exception to be handedled in the generator, and .close() to
# terminate the procedure.

# We demonstrate a simple coroutine below:
def simple_coroutine():
    print('--> coroutine started')
    x = yield # note: yield on the right-hand-side
    print(f'--> coroutine received: {x}')
    
my_coro = simple_coroutine()
print(my_coro) # <generator object simple_coroutine at 0x7f5bd9fb0840>
print(next(my_coro)) # Takes the executing up to the yield statement:
# --> coroutine started
# None
try:
    my_coro.send(5) # --> coroutine received: 5
except Exception as e:
    print(repr(e)) # StopIteration()
    
# Our coroutine implicitly returns None - as it's only job is to receive data.
# Note the first next() call is required to bring the execution up to the yield, otherwise
# we can't use the send method:
my_coro = simple_coroutine()
try:
    my_coro.send(10)
except Exception as e:
    print(repr(e)) # TypeError("can't send non-None value to a just-started generator")


# To see the use of coroutines as a way to send-and-receive, see below:
def averager():
    total = 0.0
    count = 0
    average = None
    while True:
        term = yield average
        total += term
        count +=1
        average = total/count

av = averager()
next(av)
print(av.send(1)) # 1.0
print(av.send(2)) # 1.5
print(av.send(3)) # 2.0

       
# Or this running-sum:
def running_sum():
    total = 0
    while True:
        x = yield total
        total += x

s = running_sum()
print(next(s)) # 0
print(s.send(1)) # 1
print(s.send(2)) # 3
print(s.send(3)) # 6

# So we can keep track of local variables (total, count) over successive runs, without having to use 
# a closure as in previous chapters.

# Note calling next() on a coroutine after priming it is equivalent to .send(None):
def none_test():
    total = 0
    while True:
        x = yield total
        if x is not None:
            total += x

print('\nNone Test:')
s = none_test()
print(next(s)) # 0
print(s.send(1)) # 1
print(s.send(2)) # 3
print(s.send(3)) # 6
print(next(s)) # 6
print(next(s)) # 6 - keeps yielding the total variable
print(s.send(4)) # 10
print(next(s)) # 10


# Decorators for Coroutine priming: the need to "prime" coroutines intially calling next() on them is
# annoying (and gives errors if forgotten)

# Below is a decorator that primes coroutines automatically:
from functools import wraps

def coroutine(func):
    """Decorator to prime func"""
    @wraps(func)
    def primer(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return primer

# Now we put it into action:
@coroutine
def averager():
    total = 0.0
    count = 0
    average = None
    while True:
        term = yield average
        total += term
        count +=1
        average = total/count

a = averager()

# No need to prime it:
print(a.send(1)) # 1.0
print(a.send(2)) # 1.5
print(a.send(3)) # 2.0

# Note that using the yield from syntax automatically primes the coroutine.


# If coroutines encounter an unhandled exception, they expire:
try:
    a.send('hi')
except Exception as e:
    print(repr(e)) # TypeError("unsupported operand type(s) for +=: 'float' and 'str'")
    

try:
    print(a.send(4))
except Exception as e:
    print(repr(e)) # StopIteration()
    
# This can actually serve as a way to deliberately close coroutines - try to send it some sentinel
# value which causes an exception, e.g. None, Ellipsis, or (the class) 
# StopIteration (e.g. coro.send(StopIteration))
    
# There are 2 methods that can be used to send exceptions to generators:

# .throw(exc_type[, exc_value[, traceback]]): causes yield (at which the generator was paused) to raise the
# given exception. If the exception is handled, flow continues to the next yield, and the value yielded is
# the value returned by the gen.throw() call.

# .close(): cases the yield at which the generator was paused to throw a Generator Exit exception. No error
# is reported to the caller if the generator does not handled that exception, or if it raises StopIteration 
# (usually by running to completion). When receiving a Generator Exit, the generator must not yield a 
# value, otherwise a RuntimeError is raised. Any other exception raised by the generator propagates to 
# the caller.

# We can use these to control a coroutine, e.g.:

class DemoException(Exception):
    """Exception for demo purposes"""

def demo_exc_handling():
    print('-->coroutine started')
    while True:
        try:
            x = yield
        except DemoException:
            print('***DemoException Handled. Continuing...')
        else:
            print(f'-> coroutine received value {x}')
    raise RuntimeError('This line should never run.')

# Use and close normally
print('\nGenerator Close:')
d = demo_exc_handling()
next(d)
d.send(1) # -> coroutine received value 1
d.send('a') # -> coroutine received value a
d.close()
try:
    d.send(2)
except Exception as e:
    print(repr(e)) # StopIteration()
    
# Now try throwing it DemoException
print('\nGenerator Throw:')
d = demo_exc_handling()
next(d)
d.send(1) # -> coroutine received value 1
d.send('a') # -> coroutine received value a
d.throw(DemoException) # ***DemoException Handled. Continuing...
d.send(2) # -> coroutine received value 2

# But if we throw it an unhandled excpetion, it still expires:
try:
    d.throw(ZeroDivisionError)
except Exception as e:
    print(repr(e)) # ZeroDivisionError()

# It's now expired...
try:
    d.send(2)
except Exception as e:
    print(repr(e)) # StopIteration()
    

# If some tear-down logic /must/ run as the coroutine expires, we need to wrap the coroutine logic in a 
# try/finally block:
def demo_finally():
    print('-->coroutine started')
    try:
        while True:
            try:
                x = yield
            except DemoException:
                print('***DemoException Handled. Continuing...')
            else:
                print(f'-> coroutine received value {x}')
    finally:
        print('--->coroutine closing')

print('\nFinally...:')
d = demo_finally()
next(d)
d.send(1) # -> coroutine received value 1
d.send('a') # -> coroutine received value a
d.throw(DemoException) # ***DemoException Handled. Continuing...
d.send(2) # -> coroutine received value 2

# But if we throw it an unhandled excpetion, it still expires:
try:
    d.throw(ZeroDivisionError) # --->coroutine closing
except Exception as e:
    print(repr(e)) # ZeroDivisionError()

# It's now expired...
try:
    d.send(2)
except Exception as e:
    print(repr(e)) # StopIteration()
    
    
# It is possible to /return/ values from coroutines, after they have been used, e.g. at the end of
# some accumulation. E.g. averager below returns a tuple of (count, average) with the count and average
# of the items sent to it
from collections import namedtuple

Result = namedtuple('Result', 'count average')

def averager():
    total = 0.0
    count = 0
    while True:
        term = yield
        if term is None:
            break
        total += term
        count += 1
        average = total/count
    return(Result(count, average))

# Note: we used break above, as to return a value the coroutine must return normally (rather than expire, e.g.
# due to an unhandled excpetion)

a = averager()
next(a)
a.send(1)
a.send(2)
a.send(3)

# Now terminate the loop
try:
    a.send(None)
except Exception as e:
    print(repr(e)) # StopIteration(Result(count=3, average=2.0))
    
# The return value is smuggled out as the value of the StopIteration exception. But we can
# still extract it out.
a = averager()
next(a)
a.send(1)
a.send(2)
a.send(3)

try:
    a.send(None)
except StopIteration as e:
    avg = e.value
print(avg) # Result(count=3, average=2.0)


# The 'yield from' syntax makes this more user-friendly, by consuming the StopIteration exception, and by
# making its value (the coroutine's return value) the value of the 'yield from' expression itself.

# 'yield from' is perhaps poorly named, as it is very different than 'yield'. In other languages, 
# equivalents are called 'await'.
# When a generator gen calls 'yield from subgen()', the subgen() takes over, and will yield values 
# to the caller of gen. Meanwhile, gen is blocked, waiting until subgen is terminated.

# Consider below, where yield is inside the for loop:
def gen():
    for c in 'AB':
        yield c
    for c in range(1,3):
        yield c

print(list(gen())) # ['A', 'B', 1, 2]

# Can replace with yield from, applied directly to the iterable
def gen_from():
    yield from 'AB'
    yield from range(1,3)

print(list(gen_from())) # ['A', 'B', 1, 2]

# We could extend that simple use-case to produce a chain function, which yields values from all 
# given iterables in sequence:
def chain(*iterables):
    for it in iterables:
        yield from it
        
c = chain('abc', range(3), ('A', 'B', 'C'))
print(list(c)) # ['a', 'b', 'c', 0, 1, 2, 'A', 'B', 'C']

# Can use very similar logic to flatten out nested data structures:
from collections import Iterable
def flatten(nest):
    for item in nest:
        if isinstance(item, Iterable):
            yield from flatten(item)    # apply flatten recursively
        else:
            yield item

l = [1, [2, 3, [4, [5, [6]]]]]
print(list(flatten(l))) # [1, 2, 3, 4, 5, 6]


# However the real purpose of yield from is to allow nested generators - to hand control over to subgenerators.
# As such, it opens up a bi-directional channel from the outermost caller to the innermost subgenerator, 
# without involving all the intermediate generators. This channel can pass values, and excpetions.

# The PEP that introduced yield from uses specific terminology:

# delegating generator: the generator function containing the 'yield from <iterable>' expression

# subgenerator: the generator obtained from the <iterable> in the delegating generator's yield from 
# expression

# caller: the client code that calls the delegating generator

# E.g. consider the code below, in which the caller main sends data to grouper, which is the delegating 
# generator which calls averager - with end result, being calcuating averages by the groups in the data

# averager was define above - its a simple generator, using 'yield'

# grouper below is the delegating generator, using 'yield from':
def grouper(results, key):
    while True:
        results[key] = yield from averager()    # averager() is a generator-iterator
        
# recall: 'yield from' consumes the StopIteration raised from averager() generator when it runs to completion
# That happens when it is sent value 'None'

# client code - note the coroutine is created fresh, primed, and values piped in for 
# each (group-by) key in the data
def main(data):
    results = {}
    for key, values in data.items():
        group = grouper(results, key)   # group is our coroutine
        next(group)     # prime it
        for value in values:
            group.send(value)   # value gets sent through to averager
        group.send(None) # terminate the averager generator
        
    # print the results
    report(results)        


def report(results):
    for key, result in sorted(results.items()):
        print(f'Group {key} average: {result}')
        

data = {'A': range(1,4), 'B': [10, 20], 'C': (1,1,1)}

main(data)
# Group A average: Result(count=3, average=2.0)
# Group B average: Result(count=2, average=15.0)
# Group C average: Result(count=3, average=1.0)

# Note that if we ommited the line 'group.send(None)', averager would never return - and so 
# the return value would never be passed to results[key] - and so key wouldn't be inserted into
# the results dict. Hence results would have remained empty, and the report would print no output.


# The Meaning of yield from:

# Any values yielded by the subgenerator are passed directly to the caller of the delegating
# generator (i.e. client code)

# Any values passed to the delegating generator via .send() are passed directly to the subgenerator. If 
# 'None' is sent, the subgenerators's __next__ method is called. Otherwsie the subgenerator's send() 
# method is called. If that call raises StopIteration, the delegating generator is resumed. Any 
# other exception is propagated to the delegating generator.

# 'return expr' in a (sub)generator causes StopIteration(expr) to be raised upon exit from the (sub)generator.

# The value of the 'yield from' expression is the first argument of the StopIteration exception raised 
# by the subgenerator when it terminates.

# Excpetions other than GeneratorExit throw to the delegating generator are passed to the throw() method 
# of the subgenerator. If this call raises StopIteration, the delegating generator is resumed. Any other
# exception is thrown to the delegating generator.

# If a GeneratorExit is thrown to the delegating generator, or its close() method is called, then 
# the close method of the subgenerator is called (if it has one). If this call raises an excpetion, 
# that exception is propagated to the delegating generator. Otherwise, GeneratorExit is raised in 
# the delegating generator.

# Note that yield from automatically primes the subgenerator, by calling next on it - so 
# don't need to do it manually; but this is incompatible with decorators that prime coroutines.
 
 
 
# One use-case for coroutines is simulation - where they let us implement concurrent activities 
# without using threads. The focus here is 'Discrete Event Simulation', where the simulation runs
# over a (discrete) sequence of events (e.g. taxi: pick up -> drop off -> look for next customer), 
# rather than time-based or chronological simulation. Another example is turn-based games.
# See taxi_sim.py for an example.

# [p492]