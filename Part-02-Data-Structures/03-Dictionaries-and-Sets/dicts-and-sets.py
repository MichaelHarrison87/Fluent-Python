"""
Chapter 3 - Dictionaries and Sets
"""


# Dictionaries are implemented as hashtables under the hood; and as-such their keys must be a hashable data type
# The atomic immutable types are all hashable - i.e. str, byte, numeric types

# Tuples are hashable only if all their elements are hashable
t = (1,2,3)
s = (4,5,6)
d = {t: "tuple", s: "another tuple"}
print(d, d[(4,5,6)])

# Lists are not hashable (because they're mutable?)
try:
    l = [1,2,3]
    d = {l: "list"}
    print(d)
except Exception as ex:
    print(ex)
    
# So an unhashable element of a tuple makes the tuple unhashable
try:
    t = (1, 2, [3,4])
    d = {t: "unhashable tuple"}
    print(d)
except Exception as ex:
    print(ex)
    
# Sets are also mutable, hence unhashable:
s = set([1,2,3])
print("set:", s)
try:
    d = {s: "set"}
    print(d)
except Exception as ex:
    print(ex)
    
# frozensets are immutable sets, and hence hashable:
fs = frozenset([1,2,3])
print(fs)
d = {fs: "frozen set"}
print(d, d[frozenset([1,2,3])])
    
# Note: can build dicts using zip - first iterable are the keys, the second the values
d = dict(zip(["a", "b", "c"], [1, 2, 3]))
print(d, d["b"])

# And similarly can use dictcomps on paired items:
DIAL_CODES = [
(86, 'China'),
(91, 'India'),
(1, 'United States'),
(62, 'Indonesia'),
(55, 'Brazil'),
(92, 'Pakistan'),
(880, 'Bangladesh'),
(234, 'Nigeria'),
(7, 'Russia'),
(81, 'Japan'),
]

d = {country: code for code, country in DIAL_CODES}
print(d, d["Japan"])

# Can can apply filtering, transformations etc within the dictcomps:
d = {country.upper(): code for code, country in DIAL_CODES if country.startswith("I")}
print(d, d["INDIA"])

# Note: get(key, default) can be used on dicts to specify a value if the desired key is missing:
print(d.get("JAPAN", "xx"))

# The __missing__ dunder method controls what happens when for a non-existent key in a map
# It is called only by the __get_item__ method (which [] invokes - i.e. dict[key] is dict.__get_item__(key))
# In the dict() class, the __get_item__ method is aware of __missing__, but throws an error by default. 
# We could subtype dict and provide our own __missing__ method - e.g. convert nonstring keys to string on lookup
class StrKeyDict0(dict):
    
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]
    
    def get(self, key, default = None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def __contains__(self, key):
        """
        Lets us use the Python "in" keyword (e.g. if k in d: ... ). 
        The __contains__ method in the base dict class does not fall back to the __missing__ method
        Returns: boolean
        """
        return key in self.keys() or str(key) in self.keys()
    
print("Test StrKeyDict0:")
d = StrKeyDict0([("2", "two"), ("4", "four")])
print(d)  

# Test []
print(d["2"]) # expect "two"
print(d[4]) # expect "four"
try:
    print(d[1])
except KeyError:
    print("d[1] raises key error")

# Test get()
print(d.get("2")) # expect "two"
print(d.get(4)) # expect "four"
print(d.get(1, "N/A")) # expect "N/A"

# Test in
print(2 in d) # expect True
print("2" in d) # expect True
print(1 in d) # expect False


# Variations on dict:
## OrderedDict - maintains keys in insertion order, can iterate over keys in that order
## ChainMap - holds a list of mappings that can be searched as one
import collections

chain_map = collections.ChainMap({"A": 1, "B": 2}, {"C": 3, "D": 4}, {1: "a", 2: "b", 3: "c"}, {4: "d", 5: "e", 6: "f" })
print(chain_map)
print("{}: {}".format("A", chain_map["A"]))
print("{}: {}".format("C", chain_map["C"]))
print("{}: {}".format(1, chain_map[1]))
print("{}: {}".format(4, chain_map[4]))

## Counter - maintains a count of keys, which updated as each key is inserted multiple times. Has other useful functionality, e.g. mostcommon[n], +/- to add/subtract tallies
counter = collections.Counter("abbccc")
print(counter)
print(counter["b"])
print(counter.most_common(2))
counter.update("aaaa")
print(counter)
print(counter.most_common(2))
counter += collections.Counter("abcddd")
print(counter)
counter -= collections.Counter("a"*5)
print(counter)

## UserDict - a pure Python implementation of a standard dict. It's inteded use is to be subclassed.
## It's preferred to subclass UserDict instead of the base dict(), as the latter has implementation 
## shortcuts that force us to override certain methods that we could just inherit from UserDict.
## e.g. __cotains__ correctly calls __missing__ if needed - so don't need to override it as we did above.

class StrKeyDict(collections.UserDict):
    
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError
        return(self[str(key)])

    def __contains__(self, key):
        return str(key) in self.data # data is UserDict's internal dict()
 
    def __setitem__(self, key, item):
        self.data[str(key)] = item
        
print("Test StrKeyDict:")
d = StrKeyDict([("2", "two"), ("4", "four")])
print(d)  

# Test []
print(d["2"]) # expect "two"
print(d[4]) # expect "four"
try:
    print(d[1])
except KeyError:
    print("d[1] raises key error")

# Test get()
print(d.get("2")) # expect "two"
print(d.get(4)) # expect "four"
print(d.get(1, "N/A")) # expect "N/A"

# Test in
print(2 in d) # expect True
print("2" in d) # expect True
print(1 in d) # expect False

# Test setitem
d[1] = "one"
print(d)
print(d["1"])
    
# Immutable Mappings
# MappingProxyType is effectively a read-only dictionary, after being created from some mutable mapping type (typically a dict)
from types import MappingProxyType
d = {"a": 1, "b": 2}
d_proxy = MappingProxyType(d)
print(d_proxy)
print(d_proxy["a"])
print(d_proxy["b"])

# can't add new items
try:
    d_proxy["c"] = 3
except Exception as e:
    print(e)

# or modify existing ones
try:
    d_proxy["a"] = 3
except Exception as e:
    print(e)
    
# but changes in its reference dict are reflected:
d["c"] = 3
d["a"] = 4
print(d_proxy)

# Sets are collections of unqiue objects
l = ["a", "b", "b", "c", "c", "c"]
s = set(l)
print(s)
print(len(s), len(l))
s.add("d")
print(s)
s.add("d")
print(s)

# Sets support set operations
s2 = set(["a", "b", "e"])
print("SET OPERATIONS")
print(s, s2)
print("Union: ", s | s2) # union
print("Diff s1-s2: ",s - s2) # set difference
print("Diff: s2-s1",s2 - s) # set difference
print("Intersection: ",s & s2) # set intersection

# Gives a convenient way to find number of elements common to two (or more) sets:
print("Num common elements:", len(s & s2))

# The alternative approach is much more verbose:
num_common = 0
for item in s:
    if item in s2:
        num_common += 1
print("Num common elements:", num_common)

# Note: lists don't support the intersection operator - i.e. [1,2,3] & [1,2] doesn't work

# Note: sets use a hash table under the hood, so membership tests (e.g. intersection) are fast even against large sets 
# e.g. checking if 1000 "needles" are in a 10,000,000 item "haystack"

# Sets can also be constructed using "{}":
s = {"a", "a", "b"}
print(s, type(s))
s.pop()
print(s)
s.pop()
print(s) # this is the empty set - no literal "{}" representation, so prints "set()"

# Note: this literal syntax is faster than calling the constructor: set([1,2,3,...])
# This is because the constructor has to look up the set name to fetch the constuctor, build the list, then call the constructor

# We can see this by looking at the respective bytecode:
from dis import dis # "dissembler" function
print("Literal Bytecode:")
print(dis("{1}"))
print()
print("Constructor Bytecode:")
print(dis("set([1])"))

# frozensets are immutable sets
s = {1,2,3}
s.update([4])
print(s)

fs = frozenset({1,2,3})
try:
    fs.update([4])
except Exception as e:
    print(e)

# But can still perform set operations with frozensets:
fs2 = frozenset({1,2, 4})
print("Union: ", fs | fs2)
print("Diff: ", fs - fs2)
print("Intersection: ", fs & fs2)

# And can mix sets and frozensets in set operations - the first elements determines the type (set or frozenset):
print("Union: ", fs | s) # returns a frozenset
print("Union: ", s | fs) # returns a set
s1 = s | fs
s1.update([5])
print(s1)

# Can also create sets via set comprehensions:
s = {i for i in list("abbccc")}
print(s, type(s))


# Set Operations
# Can use the set operations /methods/ with a set, and any other iterable:
print(s.intersection(["a"]))
print(s.union(["d"]))

# But can't use the literals
try:
    print(s & ["a"])
except Exception as e:
    print(e)

try:
    print(s | ["d"])
except Exception as e:
    print(e)
    
# Note: in only works element-wise:
print(set(["a", "b"]) in set(["a", "b", "c"])) # False
print("a" in set(["a", "b", "c"])) # True

# sets implement the __iter__ method, so can iterate over them as for lists etc:
for item in set([1, 2, 2, 3, 3, 3]):
    print(item)
    
# Note: set elements (like dict keys) must be hashable. E.g. can't have set whose elements are lists
try:
    print(set([[1,2], [3,4]]))
except Exception as e:
    print(e)
    
# The Hash Table Algorithm
# To find the value of dict[search_key], Python calls hash(search_key) to get the hash value of the key. 
# Then it uses the least least significant bits of the has value to determine the offset to
# lookup the bucket in the hash table. The number of least significant bits depends on the 
# current size of the hash table.
# If the bucket is empty, a KeyError is raised. Else, Python then checks whether search_key == found_key.
# If they match, it returns the value in the bucket.
# If not (i.e. search_key != found_key), this is called a hash collision.
# In this case, the algorithm then takes different bits from the hash value to lookup the next bucket.
# See the CPython source code (in particular the Perturb function):
# https://hg.python.org/cpython/file/tip/Objects/dictobject.c
# The same process is used to insert or update items - with new items ideally being put into empty buckets.
# When inserting, if the hash table gets too dense, Python rebuilds it in a new location with more room.
# As the hash table grows, so does the number of offset bits used to lookup buckets - so as to keep the number of collisions low

# Note: this all means that only hashable objects can be used as dict keys. 
# An object is hashable if:
# 1. It supports hash() via a hash() method, and that method always returns the same value 
# over the lifetime of the object
# 2. It supports equality via an eq() method.
# 3. a==b being True implies hash(a) == hash(b) is True

# The first point means that mutable types are not hashable (and so can't be dict keys), whereas immutable types are
# e.g. 

# Can't use lists as dict keys
try:
    print({["a", "b"]: 1})
except Exception as e:
    print(e)
finally:
    print("finally test")

# But can use tuples
d = {("a", "b"): 1, ("c", "d"): 2}
print(d)
print(d[("c", "d")])

# Can't use sets
try:
    print({set(["a", "b", "a"]): 1})
except Exception as e:
    print(e)
finally:
    print("finally test")

# But can use frozensets
d = {frozenset(["a", "b", "a"]): 1, frozenset(["c", "d", "c", "d"]): 2}
print(d)
print(d[frozenset(["c", "d"])])

# Dicts have significant memory overhead: as hash tables must be sparse, they can't be space-efficient
# So, when dealing with large numbers of records, tuples or namedtuples are a better choice than dicts
# I.e. store records in a list of tuples, rather than a list of dicts (as in JSON) 
# Tuples won't create an entire hash table for each record, and also don't store the row headers 
# for each record (as dicts would)

# For user-defined types, the __slots__ class attribute can be used to change the storage 
# of class attributes from a dict to a tuple in each instance.

# Key search is very fast - what dicts lack in space inefficiency, then make up for in time efficiency.

# Note that key ordering depends on insertion order - as, if there's a collision, the second key 
# in that bucket is assigned into a location it wouldn't otherwise be.
# Hence dicts with keys in different order (but same contents - i.e. key/value pairs) compare as equal
# I.e. insertion order doesn't matter when comparing dicts.

DIAL_CODES = [
(86, 'China'),
(91, 'India'),
(1, 'United States'),
(62, 'Indonesia'),
(55, 'Brazil'),
(92, 'Pakistan'),
(880, 'Bangladesh'),
(234, 'Nigeria'),
(7, 'Russia'),
(81, 'Japan'),
]
d1 = dict(DIAL_CODES)
print(d1)
DIAL_CODES.sort() # sort by dial code digit
d2 = dict(DIAL_CODES) 
print(d2)
d3 = dict(sorted(DIAL_CODES, key = lambda x:x[1])) # sort by Country, alphabetically
print(d3)
print(d1 == d2, d1 == d3, d2 == d3)

# Adding items to the dict may change the original ordering of the key
# As if the hash table needs to grow, it is re-built. This may result in new hash collisions,
# and hence keys wind up in a different ordering in the hash table.

# Note this means that if iterating over a dict's key, and modifying them at the same time 
# may not iterate over all keys as expected.
# So avoid modifying a dict while iterating over it

# Sets and frozensets are both implemented via hash tables, although the buckets only contain a 
# reference to the element (effectively act as dict keys with no corresponding values)
# Hence all the same implications disucssed for dicts above apply to sets
# e.g. set elements must be hashable, sets have significant memory overhead
