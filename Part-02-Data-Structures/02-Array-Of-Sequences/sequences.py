"""
Python standard library includes a variety of sequence types:

Containers:
- list
- tuple (immutable)
- deque

Flat:
- str (immutable): converts input into a string, e.g. str(123) = '123'
- bytes (immutable): 
- bytearray
- memoryview
- array.array

"""
import array
from collections import namedtuple, deque
import bisect
import random

###  List Comprehensions

symbols = "$¢£¥€¤"
codes = [ord(symbol) for symbol in symbols] # ord() returns the numeric ASCII code for its input
print(codes)

# Note from Python > 2.7, listcomps do not "leak":
x = "xyz"
dummy = [x for x in "ABC"]
print(x) # expect 'xyz' but in Python 2.7 get 'C'; fixed in Python 3

# But listcomps can use variables from the surrounding scope:
dummy_2 = [elem for elem in x] # expect ['x', 'y', 'z']


# Can replicate listcomp behavious with map/filter - but at the expense of readability
codes_filter = [ord(symbol) for symbol in symbols if ord(symbol) > 127]
print(codes_filter)

# With map/filter:
codes_filter_alt = list(filter(lambda c: c > 127, map(ord, symbols)))
print(codes_filter_alt)

# However, listcomps are faster - see the listcomp_speed.py tests

# Can use listcomps to produce the Cartesian product of two set of values:
print()
colors = ["black", "white"]
sizes = ["small", "medium", "large"]
tshirts = [(color, size) for color in colors for size in sizes]

# Note the 2nd for iterates first, then the 1st, i.e. (black, small), (black, medium); not (black, small), (white, small)
for shirt in tshirts:
    print(shirt)
print()


### Generator Expressions

# These are used to initialise other sequences types than lists - e.g. tuples, arrays
codes_tuple = tuple(ord(s) for s in symbols)
print(codes_tuple)

codes_array = array.array("I", (ord(s) for s in symbols)) # Note: first argument denotes type, here integer
print(codes_array, codes_array[0])

# They also save memory by yielding items one-by-one
# For instance below, the full list of 6 color/size combos is never instantiated in memory (useful if, say, each list had 1000 items for 1,000,000 combos) 
for tshirt in ((c, s) for c in colors for s in sizes):
    print("{!s}, {!s}".format(*tshirt)) # Need to explode the tshirt tuple
    
### Tuples

# Tuples can be used simply as immutable lists, but also as records with no field names

# Example uses of tuples:

# Immutable data:
lax_coords = (33.9425, -118.408056) 

# As a collection of data
city, year, pop, change, area = ('Tokyo', 2003, 32450, 0.66, 8014) 

# Several data items in same format - list of tuples
traveler_ids = [('USA', '31195855'), ('BRA', 'CE342567'), ('ESP', 'XDA205856'), ('ALB', "98437222")]
print()
print(traveler_ids)

# Can sort these items on their first element:
print()    
for passport in sorted(traveler_ids):
    print("{!s}\{!s}".format(*passport))

#  Can also "unpack" tuples within for loops (and other iterators):
print() 
for country, _ in traveler_ids:
    print(country) # Note the dummy "_" above, which denotes the 2nd field is not to be used

# Note: can use unpacking to elegently swap values, without using a temp variable:
print()
a = 1
b = 2
print(a,b) # expect 1 2
b, a = a, b
print(a, b) # expect 2 1

# Can use * to explode tuples, so they can be passed as args to functions
t = ("A", "B", "C")
print()
print(t)
print(*t)

t = (20, 8)
result = divmod(*t) # explode t to pass its elements in as arguments
print("{!r} is divisible by {!r}, {!r} times, with remainder {!r}".format(*t, *result))
print()

# The * can also be used to grab ranges of elements from tuples:
a, b, *rest = range(5)
print(rest) # expect [2, 3, 4]

a, *rest, b = range(5)
print(rest) # expect [1, 2, 3]
print()

# Unpacking can also be used to get elements from inside nested tuples:
metro_areas = [
('Tokyo', 'JP', 36.933, (35.689722, 139.691667)), #
('Delhi NCR', 'IN', 21.935, (28.613889, 77.208889)),
('Mexico City', 'MX', 20.142, (19.433333, -99.133333)),
('New York-Newark', 'US', 20.104, (40.808611, -74.020386)),
('Sao Paulo', 'BR', 19.649, (-23.547778, -46.635833)),
]

for city, code, pop, (long, lat) in metro_areas:
    print("{!s} Latitude: {:9.4f}".format(city, lat))
    
# Named Tuples - can use these to assign names to attributes in the data being packaged
City = namedtuple('City', 'name country population coordinates') # City is the class name
tokyo = City('Tokyo', 'JP', 36.933, (35.689722, 139.691667))

print("Tokyo:", tokyo)
print("Tokyo coords:", tokyo.coordinates)

# Can get the class fields:
print(City._fields)

# Can use named tuples in lieu of tuples:
Coords = namedtuple("coords", "lat long")
delhi_data = ('Delhi NCR', 'IN', 21.935, Coords(28.613889, 77.208889))
delhi = City._make(delhi_data)
print("Delhi:", delhi)

# Can convert namedtuples to dictionary:
print(delhi._asdict()) # an OrderedDict with only one item: a list containing the named tuple

for key, value in delhi._asdict().items():
    print(key, value)
    
    
### Slicing

# Python ranges exclude the last item as its more convenient with 0-indexing convention in the rest of the language (and in other, e.g. C)
# Its intended by analogy of specifying ranges in maths as: 2 <= i < 13 (for 2,...,12)

# Easier to tell how many items will be returned:
print(list(range(3))) # prints first 3 integers
l = [10, 20, 30, 40, 50, 60]

# Allows for partitioning with the same position value - helps avoid overlap with out-by-one errors
print(l[:3]) # first 3 items of l
print(l[3:]) # the remainder of l

# The a:b:c slice syntax produces a slice(a,b,c) object under the hood, which can be named - useful for clarity; e.g:
invoice = """
0.....6.................................40........52...55........
1909  Pimoroni PiBrella                       $17.50    3    $52.50
1489  6mm Tactile Switch x20                   $4.95    2     $9.90
1510  Panavise Jr. - PV-201                   $28.00    1    $28.00
1601  PiTFT Mini Kit 320x240                  $34.95    1    $34.95
"""
SKU = slice(0, 6)
DESCRIPTION = slice(6, 40)
UNIT_PRICE = slice(40, 52)
QUANTITY = slice(52, 55)
ITEM_TOTAL = slice(55, None)
line_items = invoice.split('\n')[2:]

print("\nINVOICE:")
for item in line_items:
    print(item[UNIT_PRICE], item[DESCRIPTION])
print()


# Multidimensional Slicing

# [] takes multiple slices, separate by columns: [x:y, m:n]
# a[x, y] is interpreted by Python as a.__getitem__((x,y))

# Slicing can be used to modify mutable sequences in-place:
l = list(range(11)) # [0, 1, 2, 3, 4, 5 ,6, 7, 8, 9, 10]
l[2:4] = [20, 30]  # [0, 1, 20, 30, 4 ,6, 7, 8, 9, 10]
del l[5:7] # remove positions 5, 6: [0, 1, 20, 30, 4, 7, 8, 9, 10]
l[7] = 90 # [0, 1, 20, 30, 4, 7, 8, 90, 10]

# Can overwrite a (sub-)slice with a single element, but need to put that element in an iterable object (e.g. one-element list below):
l[4:7] = [60] # overwrite positions 4-6: [0, 1, 20, 30, 60, 90, 10]

# Note: l[4:7] = 60 will throw an error
print(l)

# Lists of lists
# Can use lists of lists to represent multi-dimensional objects.
# e.g. a 3x3 naughts-and-crosses board:
board = [["_"] * 3 for i in range(3)]
print(board)
board[1][1] = "X" 
board[0][2] = "O" 
print(board) # result: [['_', '_', 'O'], ['_', 'X', '_'], ['_', '_', '_']]

# But be careful initialising with * - the below initialises 3 references to the same inner list:
board_wrong = [["_"] * 3] * 3
print(board_wrong)
board_wrong[1][1] = "X"
board_wrong[0][2] = "O" 
print(board_wrong) # result: [['_', 'X', 'O'], ['_', 'X', 'O'], ['_', 'X', 'O']]

# The above [["_"] * 3] * 3 is equiv to:
row = ["_"] * 3
wrong_board_alt = []
for i in range(3):
    wrong_board_alt.append(row) # append same object multiple times

print(wrong_board_alt)
wrong_board_alt[1][1] = "X"
wrong_board_alt[0][2] = "O"
print(wrong_board_alt) # result: [['_', 'X', 'O'], ['_', 'X', 'O'], ['_', 'X', 'O']]

# Whereas [["_"] * 3 for i in range(3)] is equiv to:
board_alt = []
for i in range(3):
    row = ["_"] * 3 # object create fresh at each iteration
    board_alt.append(row)

print(board_alt)
board_alt[1][1] = "X"
board_alt[0][2] = "O"
print(board_alt) # result: [['_', '_', 'O'], ['_', 'X', '_'], ['_', '_', '_']]

# The in-place operators += and *= modify mutable objects in-place - also changing anything that references them:
l = [1,2,3]
id_l = id(l)
m = l
id_m =id(m)
l += [4,5,6]
id_l_2 = id(l)
print("List:")
print(l, m, id_l == id_l_2, id_l == id_m) # l,m are both [1,2,3,4,5,6] and their id's equal, unchanged after the += operation

# compare for immutable tuple:
t = (1,2,3)
id_t = id(t)
s = t
id_s =id(s)
t += (4,5,6)
id_t_2 = id(t)
print("Tuple:")
print(t, s, id_t == id_t_2, id_t == id_s) # t is (1,2,3,4,5,6) whereas s remains (1,2,3) and t's id is changed after the += - as it's a new object

# For immutables,  a += b is equiv to a = a + b, which creates a new object in place of a, even for mutables:
# Whereas for mutables, a += b is implemented using in-place operations
print("List - l = l + m")
l_2 = [1,2,3]
id_l_2 = id(l_2)
m_2 = l_2
id_m_2 = id(m_2)
l_2 = l_2 + [4, 5, 6]
id_l_2_new = id(l_2)
print(l_2, m_2, id_l_2 == id_l_2_new, id_l_2 == id_m_2) # m_2 remains [1,2,3] and l_2's id is changed

# These in-place operations can introduces some strangeness, e.g:
t = (1, 2, [3, 4])
print(t)

try:
    t[2] += [5,6] # throws an error as can't modify a tuple: TypeError: 'tuple' object does not support item assignment
except Exception as ex:
    print(ex)

print(t) # but the change actually went through! - get: (1, 2, [3, 4, 5, 6])

# But doesn't work when altering the integers:
try:
    t[0] += 1
except Exception as ex:
    print(ex)

print(t) # still get: (1, 2, [3, 4, 5, 6])

# The former works because the object [3, 4] is mutable; whereas the latter doesn't because int's are immutable:
a = 1
id_a = id(a)
a += 1
print(id_a == id(a)) # False - int's are immutable

# The lesson is: avoid putting mutable objects inside immutable ones


# Note the .sort() method sorts in-place, whereas the sorted() function creates a new object:
l = [2, 1, 3]
id_l = id(l)
l.sort()
id_l_2 = id(l)
print(l, id_l == id_l_2) # id's are equal

m = [2, 1, 3]
id_m = id(m)
m = sorted(m) # simply doing sorted(m) leaves m unchanged, so need to assign it to m
id_m_2 = id(m)
print(m, id_m == id_m_2) # id's now different


# Python by default uses bisect search - which can be applied to sorted lists to efficiently lookup values
# e.g. - lookup grades based on threshold values:
breakpoints = [60, 70, 80, 90] # these define the open upper bounds of each threshold, e.g. 0<=x<60 = F; 60<=x<70 = D 
grades = list("FDCBA")

def grade(score, thresholds, grade_letters):
    i = bisect.bisect(thresholds, score) # bisect.bisect is an alias for bisect.bisect_right (cf _left, which differs in how ties are broken)
    return grade_letters[i] 

my_scores = [33, 99, 77, 70, 89, 90, 95, 100]
my_grades = [grade(score, breakpoints, grades) for score in my_scores]
print(my_scores)
print(my_grades)

# cf bisect_left:
def grade_left(score, thresholds, grade_letters):
    i = bisect.bisect_left(thresholds, score)
    return grade_letters[i] 

my_grades_left = [grade_left(score, breakpoints, grades) for score in my_scores]
print(my_grades_left) # scores on the boundary now placed on the left-hand side; so get one grade lower

# bisect.insort() lets us insert items into sorted lists at the correct position, so as to keep the list properly sorted:
l = [1,2,5]
bisect.insort(l, 3)
print(l) # [1,2,3,5]



# Arrays
# Arrays are efficient containers for large numbers of items of the same type, particularly numbers (ints, floats etc)

# e.g. code below creates an array of 10 million floats:
floats = array.array("d", (random.random() for i in range(10**7))) # typecode "d" indicates doubles
print(floats[-1])

# Now save them as a binary file:
with open("floats.bin", "wb") as fp:
    floats.tofile(fp)

# Now read them back in as a new array:
floats_new = array.array("d")
with open("floats.bin", "rb") as fp:
    floats_new.fromfile(fp, 10**7)
print(floats_new[-1])
print(floats == floats_new) # expect True

# These operations are much quicker using arrays than, say, reading the floats from a text file.

# And note that arrays are mutable:
a = array.array("i", (1,2,3))
id_a = id(a)
a.append(4) # append() only appends one value
a.extend((5,6)) # extend() appends many values; can supply any iterable, e.g. here a tuple
a.extend([7,8]) # and here a list
id_a_2 = id(a)
print(a, id_a == id_a_2) # expect 1,2,3,4,5,6 and True

# Can also extend using arrays
b = array.array("i", (1,2))
id_b = id(b)
c = array.array("i", (3,4))
b.extend(c)
id_b_2 = id(b)
print(b, id_b == id_b_2) # expect 1,2,3,4 and True


# Note: we can access an arrays typecode as an attribute, as well as the size (in bytes) of each item:
print(a.typecode, a.itemsize) # ints are 4 bytes
print(floats_new.typecode, floats_new.itemsize) # floats are 8 bytes


# MemoryViews [p51] - these allow us to work with subsets (slices) of our data, without copying those subsets into new memory objects
# Lets us share memory between data structures (e.g. PIL images, numpy arrays)
# Useful when working with very large datasets and need to conserve memory usage 

# MemoryViews have a cast method, that changes the type, without changing the bytes themselves - it returns another memoryview object on the same underlying memory 

numbers = array.array("h", [-2, -1, 0, 1, 2]) # "h" is signed short int
id_numbers = id(numbers)
memv = memoryview(numbers)
id_memv = id(memv)
print(memv, hex(id(memv))) # printing the memv just gives it location in memory (in hex) 
print(memv[0]) # returns "-2", as expected
print(id_numbers, id_memv, id_numbers == id_memv) # Comparison here is False - memv is separate in memory from the numbers array

# But modifying the numbers array /does/ modify (in-place) the memoryview, and doesn't change their location in memory
numbers[0] = -3
id_numbers_2 = id(numbers)
id_memv_2 = id(memv)
print(numbers[0]) # -3
print(memv[0]) # -3
print(id_numbers == id_numbers_2) # True
print(id_memv == id_memv_2) # True

# Similarly, modifying the memoryview modifies the numbers array
memv[0] = -2
id_memv_3 = id(memv)
print(numbers[0]) # -2
print(memv[0]) # -2
id_numbers_3 = id(numbers)
print(id_numbers == id_numbers_3) # True
print(id_memv == id_memv_3) # True

# Can also convert memv to other types:
memv_oct = memv.cast("B") # "B" is an unsigned char
print(memv.tolist())
print(memv_oct.tolist())


### Deques [p55] - double-ended queues; allow threadsafe insertion and removal of items from both ends of the queue
dq = deque(range(10), maxlen=12) # optional maxlen arg specifies the max number of items allowed in the queue
print(dq)
id_dq = id(dq)
dq.rotate(3) # move last 3 items to the start of the queue
id_dq_2 = id(dq)
print(dq)
print(id_dq == id_dq_2) # True

dq.rotate(-3) # rotates first 3 items to the end
print(dq)

dq.appendleft(-1) # pre-pends -1
dq.append(11) # appends 11
print(dq)

dq.append(12) # appending to full deque removes items from the begining
print(dq, len(dq), dq[0], -1 in dq) # -1 not in dq, len is 12, first item is 0

dq.appendleft(-1) # pre-prending to full queue removes items from end
print(dq, len(dq), dq[-1], 12 in dq) # 12 not in dq, len is 12, last item now 11

dq.extendleft([-2, -3, -4]) # prepends successively in the order of the items in the tuple
print(dq, dq[0], dq[-1]) # so first item is now -4; last item is 7 as 8,9,11 are removed

# Note: deques are not as fast when removing items from the middle of the list, vs the end or start
