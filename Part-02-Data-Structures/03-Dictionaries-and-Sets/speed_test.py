# Speed Test lookup "needles" in "haystack" - using lists vs dicts.
# See example A-1 in Appendix A in the book
# Run the test by specifying a container type on the command line, e.g.:
# python speed_test.py dict
# python speed_test.py list
# python speed_test.py set

import sys
import timeit

SETUP = """
import array
selected = array.array("d")

with open("selected.arr", "rb") as fp:
    selected.fromfile(fp, {size})

if {container_type} is dict:
    haystack = dict.fromkeys(selected, 1)
else: 
    haystack = {container_type}(selected)

print(type(haystack), end=" ")
print("haystack %10d" % len(haystack), end=" ")

needles = array.array("d")
with open("not_selected.arr", "rb") as fp:
    needles.fromfile(fp, 500)
needles.extend(selected[::{size}//500])

print(" needles %10d" % len(needles), end=" ")
"""

TEST = """
found = 0
for n  in needles:
    if n in haystack:
        found += 1
"""

def test(container_type):
    MAX_EXPONENT = 6
    
    for n in range(3, MAX_EXPONENT + 1):
        size = 10**n
        setup = SETUP.format(size=size, container_type=container_type, )
        test = TEST.format()
        
        tt = timeit.repeat(stmt=test, setup=setup, repeat=5, number=1)
        print("|{:{}d}|{:f}".format(size, MAX_EXPONENT+1, min(tt)))
        
if __name__ == "__main__":
    test(sys.argv[1])