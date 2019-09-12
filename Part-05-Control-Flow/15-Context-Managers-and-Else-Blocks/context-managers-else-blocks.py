# Chapter 15: Context Managers and Else Blocks [p447]


# We can actually use else block with try, while and for block - not just if's@

# for: else will run only if the for loop runs to completion (so not if it's exited early via break)
for i in range(5):
    print(i)
else:
    print('for loop finished!')
# 0
# 1
# 2
# 3
# 4
# for loop finished!

# The else block below won't trigger, as it exits via break
for i in range(5):
    if i > 3:
        break
    print(i)
else:
    print('for loop finished!')
# 0
# 1
# 2
# 3


# while: else block triggers if the while loop exits because its condition becomes falsey
# (but again, not via break)
i = 0
while i < 5:
    print(i)
    i += 1
else:
    print('while loop finished!') 
# 0
# 1
# 2
# 3
# 4
# while loop finished!

# The else block below doesn't execute, because while exits via break
i = 0
while True:
    if i >= 5:
        break
    print(i)
    i += 1
else:
    print('while loop finished!') 
# 0
# 1
# 2
# 3
# 4


# try: else block executes if we get through the try block with no exceptions raised; but execptions within
# the /else/ block are not caught by the preceding except blocks
try:
    print('try')
except Exception:
    pass
else:
    print('No Exceptions')
    
    
try:
    l = [1,2]
    print(l[2])
except IndexError as e:
    print(repr(e))
else:
    print('No Exceptions')
# IndexError('list index out of range')

try:
    l = [1,2]
    print(l[1])
except IndexError as e:
    print(repr(e))
else:
    try:
        print(l[2])
    except Exception as e:
        print('Inner except block!')
# 2
# Inner except block!
    
    
# else blocks are useful to avoid extra if statements. e.g: see below, else triggers if 'd' isn't
# in the list

l = ['a', 'b', 'c']
for item in l:
    if item == 'd':
        break
else:
    print('d not in list')
# d not in list

# The general use of else with try is to avoiding try'ing stuff which is not anticipated 
# to raise exceptions, e.g:

# try:
#     dangerous_call()
# except OSError:
#     log('OSError')
# else:
#     next_safe_call()
#     ...

# This just makes it clearer what aspect of the code we are checking for exceptions 


# Context manager objects exist to manager with blocks. with blocks are intended to simplify 
# the try/finally syntax - to guaranteed that some operation is performed after a block of code.
# Even if that block are aborted due to an exception, a return, or sys.exit().
# finally is usually used to release some resource, or restore some state that 
# had been temporarily changed.

# The context manager protocol used the __enter__ and __exit__ methods - __enter__ being invoked
# at the start of the with block, and __exit__ at the end (playing the role of finally).


# Example: file context manager below, ensures the file is closed after leaving the with block:
with open('my_text.txt', 'r') as f:
    print(f) # <_io.TextIOWrapper name='my_text.txt' mode='r' encoding='UTF-8'>
    src = f.read()
    # print(next(f))
    # print(next(f))
    # print(next(f))

print(f) # <_io.TextIOWrapper name='my_text.txt' mode='r' encoding='UTF-8'>
print(len(src)) # <_io.TextIOWrapper name='my_text.txt' mode='r' encoding='UTF-8'>

# After closing the file object upon exiting the with, we can't use it:
with open('my_text.txt', 'r') as f:
    print(f) # <_io.TextIOWrapper name='my_text.txt' mode='r' encoding='UTF-8'>
    print(f.closed, f.encoding) # False UTF-8
    print(next(f)) # first line\n
    print('---')
    print(next(f)) # second line\n

try:
    print(next(f))
except Exception as e:
    print(repr(e)) # ValueError('I/O operation on closed file.')
    
# However its attributes are still accessible:
print(f.closed, f.encoding) # True UTF-8

# Re the context manager: the result of it's __enter__ clause is bound to the variable in the 'as' clause
# In this case, open() returns a _io.TextIOWrapper object; and this object's __enter__ method just 
# returns self - which is then bound to the 'as' variable.

# We could work with this TextIOWrapper directly, but we'd need to remember to close it
print('\nNo Context Block:')
o = open('my_text.txt', 'r')
print(o) # <_io.TextIOWrapper name='my_text.txt' mode='r' encoding='UTF-8'>
o2 = o.__enter__() # 
print(o2) # <_io.TextIOWrapper name='my_text.txt' mode='r' encoding='UTF-8'> - as enter just returns self
print(o is o2) # True
print(next(o)) # first line\n
print(next(o2)) # second line\n
print(next(o)) # third line\n
print(o.closed) # False - TextIOWrapper is still open

try:
    next(o)
except Exception as e:
    print(repr(e)) # StopIteration() - the iterator is exhausted

print(o.closed) # False - but TextIOWrapper remains open
o.close() # until closed (alt: o.__exit__())
print(o.closed) # True - now the TextIOWrapper is closed

try:
    next(o)
except Exception as e:
    print(repr(e)) # ValueError('I/O operation on closed file.') - different error this time
    
    
# The context manager is not always the same object as returned by the __enter__ method
# E.g. below, where enter causes text to be reversed, but exit swaps it back:

class ReverseText:
    def __enter__(self):
        import sys
        self.original_write = sys.stdout.write
        sys.stdout.write = self.reverse_write
        return 'ABCD'
        
    def reverse_write(self, text):
        self.original_write(text[::-1])
    
    def __exit__(self, exc_type, exc_value, traceback):
        import sys
        sys.stdout.write = self.original_write
        if exc_type is ZeroDivisionError:
            print('Don\'t divide by zero!')
            return True
    
print('\nTest ReverseText:')
with ReverseText() as some_text:
    print(some_text) # DCBA
    print('Hello') # olleH
    
    # Note: only the display of text is reversed:
    a = 'ABCD'
    print(a == some_text) # eurT
    print(a is some_text) # eurT

    b = 'DCBA'
    print(b == some_text) # eslaF
    print(b is some_text) # eslaF

# Text is back to normal after 
print(some_text) # ABCD
print('Hello') # Hello

# This shows that some_text - the return value of the context manager's __enter__ method is distinct
# from the context manager itself (which is ReverseText). In fact we can use the context manager
# as an object in its own right, separate from the with block:

print('\nUse Context Manager standalone:')
rt = ReverseText()
print(rt) # <__main__.ReverseText object at 0x7f4333684400>
print('ABCD') # ABCD - text not reversed yet, as haven't invoked __enter__ (its a side-effect of __enter__)
m = rt.__enter__()
print(m) # DCBA - return value of __enter__, with text now reversed
print(m == 'ABCD') # eurT - But again, only the display is reversed as this is still True
print('ABCD') # DCBA
rt.__exit__(None, None, None)
print('ABCD') # ABCD - back to normal after exiting
print(m) # ABCD 


# The standard library has contextlib, which contains a bunch of utility context managers, e.g:

# closing: function to build a context manager out of objects that have a close() method,
# but not __enter__/__exit__
from contextlib import closing

class dummy:
    def close():
        print('close!')
        
try:
    with dummy as d:
        print('Inside context mgr')
        print('Inside context mgr')
except Exception as e:
    print(repr(e)) # AttributeError('__enter__')
    
dummy_cm  = closing(dummy)
with dummy_cm as d:
    print(d)
    print('Inside context mgr')
print('Outside context mgr')
# Inside context mgr
# close! - print statement in close() executed upon leaving the with block
# Outside context mgr

# Example use: urllib.urlopen - has a close() method, which we can use in with block with closing:

# import urllib

# with contextlib.closing(urllib.urlopen('http://www.python.org')) as page:
#     for line in page:
#         print line


# suppress: context manager to temporarily suppress specified exceptions, 
# then resume from after the with block
from contextlib import suppress

with suppress(IndexError, KeyError):
    print('In suppress block')
    d = {'a': 1}
    print(d['a']) # 1
    print(d['b']) # IndexError
    print('Still in suppress block - after exception') # This isn't executed

print('Left suppress block')
print(d.items()) # dict_items([('a', 1)]) - objects defined in with block accessible outisde it

with suppress(IndexError, KeyError):
    print('In suppress block')
    l = ['a']
    print(l[0]) # 1
    print(l[1]) # 1
    print('Still in suppress block - after exception') # This isn't executed

print('Left suppress block')

# @contextmanager: decorator that can build a context manager from a generator function, rather
# than building a class to implement the enter/exit protocol. The decorator creates a factory function
# that is then used by the with block. 
# The decorated function must be a generator-iterator, and yield only one value (which is bound to the
# with block's 'as' variable). The generator is paused at this yield, and the code in the with block
# is run - with the generator resuming after exiting the with block.
from contextlib import contextmanager

print('\nTest @contextmanager')

@contextmanager
def gen():
    yield 1
    print('Exit gen')

with gen() as p:
    print(p) # 1
print('Left with block')
# Exit gen
# Left with block - executed after the generator finishes


# If an exception is raised in the with block (hence, exiting it), it is re-raised in 
# the generator at the point where the yield occurred.
print('\nTest @contextmanager with exception')

@contextmanager
def gen():
    try:
        yield 1
    except IndexError as e:
        print(repr(e))
    finally:
        print('finally')
    print('Exit gen')

with gen() as p:
    l = ['a']
    l[1]
    print('Still in with block') # this doesn't get executed, as the exception above causes us to exit the with block
print('Left with block')
# IndexError('list index out of range')
# finally
# Exit gen
# Left with block


# ExitStack - lets us enter a variable number of context managers, using one with block.
# When that with block exits, __exit__ is called on the individual context managers in a 
# last in, first out (LIFO) fashion 

# For instance, can use this to open several files inside one with block:
from contextlib import ExitStack

print('\nPrint files contents')
filenames = ['my_text.txt', 'my_text_2.txt']
with ExitStack() as stack:
    files = [stack.enter_context(open(fname)) for fname in filenames]
    for index, file in enumerate(files, 1):
        print(f'File {index}:')
        while True:
            try:
                print(next(file))
            except StopIteration:
                break
        print(f'------END FILE----')
for file in files:
    print(file.closed, end=',') # True,True, - files closed after exiting the with block


# Back to @contextmanager - effectively uses a generator (with a single yield) as syntactic sugar
# for creating context managers. With the yield splitting the enter logic from the exit logic,
# and the yield value being the context manager's name per the 'as' clause
# So we could have implemented the reverse text manager as:

@contextmanager
def reverse_text():
    print('Enter...')
    import sys
    original_write = sys.stdout.write
    
    def reverse_write(text):
        original_write(text[::-1])        
        
    sys.stdout.write = reverse_write
    try:
        yield 'ABCD'
    except ZeroDivisionError:
        print('Don\'t divide by zero')
    finally:
        sys.stdout.write = original_write
    print('Exit...')
    
print('\nTest reverse_text:')
with reverse_text() as cm:
    print(cm)
    print('Hello')
    print(cm == 'ABCD')
    print(1/0)
print(cm)
# Enter...
# DCBA
# olleH
# eurT
# orez yb edivid t'noD
# Exit...
# ABCD