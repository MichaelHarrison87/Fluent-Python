# spinner_asyncio.py [p567]

# Code is the book is valid for Python <= 3.5; asyncio syntax changed to new 'async def' & 'await'
# for later versions of Python. Updated code examples taken from:
# https://github.com/fluentpython/example-code/tree/master/18-asyncio-py3.7

import asyncio
import itertools
import sys
import threading


async def spin(msg):
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))  # This moves the cursor back - \x08 is the backspace char; this allows for text-based animation
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            break
    write(' ' * len(status) + '\x08' * len(status))
    

async def slow_function():
    """Mimics some slow-running function"""
    await asyncio.sleep(5)
    return 42


async def supervisor():
    spinner = asyncio.create_task(spin('thinking...'))
    print('spinner object:', spinner)
    result = await slow_function()
    spinner.cancel()
    return result


def main():
    result = asyncio.run(supervisor())
    print('Answer:', result)

if __name__ == '__main__':
    main()