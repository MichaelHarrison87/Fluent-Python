# Chapter 17: Concurrency with Futures

# This chapter uses the concurrent.futures package. "Futures" are objects representing the asynchronous
# execution of some operation.

# Heavy network I/O is a good use-case for concurrency - as want to waste CPU cycles while waiting for  
# a response from a network

# This chapter has two scripts - flags_sequential.py and flags_threadpool.py - which download images
# of 20 flags, sequentially and concurrently respectively.


# Futures encapsulate pending operations, so that they can be put into queues, their state of 
# completion can be queried, and their results (or exceptions) can be retrieved when available.

# They are inteded to be instantiated only by the concurrency framework, rather than directly by the 
# user. With concurrent.futures, instances of Future are created only as a result of scheduling 
# something for completion via an Executor.

# E.g. Executor.submit() takes a callable, schedules it to run, and returns a future.

# Client code should not change the state of a future - the concurrency framework does that  when
# the computation the future represents is complete.

# Futures from concurrent.futures (and asyncio) have a .done() method - that is non-blocking, and returns
# a Boolean that tells you whether the callable linked to the future has executed or not.

# However client code should instead wait to be told if a callable has executed, rather than ask. That is
# why Futures have an .add_done_callback() method - give it a callable, and the callable will be invoked 
# with the future as the single argument when the future is done.

# Futures also have a .result() method - when the future is done, it returns the result of the 
# callable (or re-raises any exceptions thrown when the callable ran). 
# 
# If the future is not done, in concurrent.futures f.result() will block the caller's thread 
# until the future is done. There's an optional timeout argument, which will raise a TimeoutError 
# exception if the future is not done in the specified time.  

# Executor.map() is an example of future's being used under the hood - it returns an iterator, whose
# __next__() method calls the .result() method of each future - so we get the results, not the futures 
# themselves.

# The as_completed() function takes an iterable of futures, and returns an iterator of that yields 
# results as they are completed.


# Blocking I/O and the GIL

# The CPython interpreter's Global Interpreter Lock (GIL) means that only one thread at a time can
# run Python bytecode. So a single (CPython) Python process can't use multiple CPU cores at the same
# time.

# However extensions (and built-ins) written in C can release the GIL while running time-consuming 
# tasks, launch their own OS threads, and utilise all CPU cores. In face, all standard library functions
# that perform blocking I/O do indeed release the GIL while waiting for a result from the OS.

# So I/O-bound Python programs can benefit from threads at the Python level.


# The concurrent.futures module allows us to work with multiple Python processes - which bypasses the GIL
# and allows for using all CPU cores, for CPU-bound processing. This is done via the ProcessPoolExecutor, 
# which implements the same generic Executor interface as ThreadPoolExecutor. The only difference being
# that ThreadPoolExecutor requires a max_workers argument upon initialisation, specifying the number of
# threads to use.

# Executor.map returns all results in the order that the calls are started. So if first call takes 10 secs
# to complete, while all others take 1 sec - the code will block for 10 secs before it is able to retrieve
# the first result. So we can't get and use results as they are completed (cd: as_completed)


# Downloads with progress display and error handling  [p522]

# Note: code uses the tqdm ('progress' in Arabic) module, which creates a progress bar. It works
# by consuming any iterable, and producing an iterator which, while it's consumed, updates the progress
# bar and estimates the time to completion. It requires an iterable with a __len__, or user can 
# provide an optional second argument with the expected number of iterations.


# Using futures.as_completed [p527]
