import itertools
import sys
import threading
import time

class Signal:
    go = True
    
def spin(msg, signal):
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))  # This moves the cursor back - \x08 is the backspace char; this allows for text-based animation
        time.sleep(0.5)
        if not signal.go:
            break
    write(' ' * len(status) + '\x08' * len(status))
    

def slow_function():
    """Mimics some slow-running function"""
    time.sleep(5)
    return 42


def supervisor():
    signal = Signal()
    spinner = threading.Thread(target = spin, args = ('thinking...', signal))
    print('spinner object:', spinner)
    spinner.start()
    result = slow_function()
    signal.go = False
    spinner.join()
    return result


def main():
    result = supervisor()
    print('Answer:', result)

if __name__ == '__main__':
    main()