# Chapter 18 - Concurrency with asyncio [p537]

# We make a distinction between concurrency and parallelism - even a single-core CPU can run
# 100s or 1000s of processes concurrently (swapping between them), but fundamentally at
# any given moment in time it can only run one process. So it lacks parallelism, but 
# not concurrency. Meanwhile, a quad-core CPU can also run processes concurrently, 
# but can run up to 4 processes at a single moment in time - in parallel. The latter
# being genuinely in parallel.  

# asyncio is a package that implements concurrency using coroutines, driven by an event loop.

# Code is the book is valid for Python <= 3.5; asyncio syntax changed to new 'async def' & 'await'
# for later versions of Python. Updated code examples taken from:
# https://github.com/fluentpython/example-code/tree/master/18-asyncio-py3.7


# Note: 'async def' defines a coroutine, and 'await' is equivalent to 'yield from' in ordinary coroutines.
# We create and cancel Tasks (analagous to threading Threads), which drive the coroutines.

# Tasks' .cancel() method sends a CancelledError to the coroutine it is driving, and the coroutine will
# usually have code to catch this exception (see the spin() function in the spinner_asyncio.py example)

# Note that, unlike with threads, coroutines are protected from interruption by default - they must explicitly
# yield/await to let the rest of the program run - only one coroutine runs at any one time, but 'yield from'
# hands control back to the scheduler. As such, coroutines can only be cancelled when paused at a yield 
# statement - and hence the CancelledError lets us perform cleanup.

# asyncio.Task is a subclass of asyncio.Future, intended to wrap a coroutine: create_task() takes a coroutine,
# schedules it to run, and returns a Task instance.

# Usually get results from asyncio.Futures via 'yield from' ('await' now?) - which waits for the Future to 
# finish without blocking the event loop.

# E.g. in spinner_asyncio.py's supervisor() function - we 'await' (i.e. yield from) the slow_function()
# coroutine after creating the spinner task. Which allows slow_function() to run, while spin() is also
# running

# Hence any processing to be done after the Future can simply be put in the lines after 'await'.


# Downloading with ayncio and aiohttp  [p548 (574 of 766)]