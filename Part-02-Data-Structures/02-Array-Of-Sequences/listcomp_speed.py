import timeit

SETUP = """
symbols = '$¢£¥€¤'
def non_ascii(c):
    return c > 127
"""

# Times how long the given command takes to run for a total of 10,000 times; repeats this 10 times and prints the 10 results    
def clock(label, cmd):
    results = timeit.repeat(cmd, repeat = 10, setup=SETUP, number = 10_000)
    print(label, *('{:.3f}'.format(x) for x in results)) 

clock("listcomp       :", '[ord(s) for s in symbols if ord(s) > 127]')
clock("listcomp + func:", '[ord(s) for s in symbols if non_ascii(ord(s))]')
clock("filter + lambda:", 'list(filter(lambda c: c > 127, map(ord, symbols)))')
clock("filter + func  :", 'list(filter(non_ascii, map(ord, symbols)))')