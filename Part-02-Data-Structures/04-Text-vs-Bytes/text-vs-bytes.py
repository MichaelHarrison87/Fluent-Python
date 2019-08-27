# Chapter 04 - Text vs Bytes [p97]

# A string is a sequence of characters
# The items you get out of Python's str are Unicode characters, not the raw bytes (as in Python 2)
# The Unicode standard separates characters from specific byte representations

# The identity of a character (called its "code point") is a number between 0 and 1,114,111.
# That number is usually represented as a 4 to 6 hexadecimal digits, preceded by a "U+"
# e.g. U+0041 is A
# U+20AC is the euro sign
# Around 10% of the possible code points are assigned in Unicode 6.3, which is the standard used by Python 3.4

# The actual byte representation of each character depends on the encoding being used.
# An encoding is an algorithm for converting code points into bytes, and vice versa.
# E.g. "A" with code point U+0041 with the UTF-8 encoding is represented as single byte: \x41
# but as bytes \x41\x00 in UTF-16LE

# Note: \x refers to hexadecimal representation of a byte (i.e. 2 hexa digits = 1 byte):
# A byte is 8 bits: 2^8 categories
# One hexadecimal digit is 16 categories: or 2^4
# So type hexadecimal digits is: (2^4)*(2^4) = 2^8 categories, as required  

s = 'café' # note the e has an accent
print(s, len(s))
b = s.encode("utf-8")
print("UTF-8 encoded bytes:", b, len(b)) 

# len is 5 bytes, since "é" is encoded as 2 bytes, which "c" "a" & "f" are 1:
print(b.decode("utf-8"))

# Python has two binary sequence types - bytes (immutable) and bytearray (mutable)

# Each item in byte or bytearray is a number between 0 and 255  - i.e. 2^8 categories, a byte
cafe = bytes('café', encoding="utf-8")
print("\nbytes")
print(cafe)
for byte in list(cafe):
    print(byte)

print("\nbytearray")
cafe_arr = bytearray('café', encoding="utf-8")
for byte in cafe_arr:
    print(byte)

# Bytes is immutable:
try:
    cafe[2] = 255
except Exception as e:
    print(e)

# Bytearrays are mutabe - change é to e changing its two bytes to (decimal) 100:
cafe_arr.pop() # remove last byte
cafe_arr[-1] = 101 # decimal 101 is "e"
print(cafe_arr)

# We can build up byte sequences from buffer-like objects (e.g. arrays):
import array
numbers = array.array("h", [-2, -1, 0, 1, 2])
numbers_hexa = bytes(numbers)

print(numbers_hexa) # prints entire hexa number, which is outside the printable range: b'\xfe\xff\xff\xff\x00\x00\x01\x00\x02\x00'

# Note: creating bytes or bytearray in this way always copies the bytes

# Conversely, memoryview lets us share memory between binary data structures

# The struct module assists with this - it lets us parse packed bytes into a tuple of fields 
# of different lengths. As well as the reverse - from a tuple into packed bytes.

# e.g. can use memoryview to get the the height/width of a gif
import struct
fmt = '<3s3sHH' # struct format: "<": little-endian, "3s3s": two sequences of 3 bytes, "HH": two 16-bit integers
with open("giphy.gif", "rb") as fp:
    img = memoryview(fp.read()) # memoryview of the gif's content
header = img[:10] # slicing a memoryview creates another memoryview - no bytes are copied
print("Header bytes: ", bytes(header))
print("Struct:", struct.unpack(fmt, header)) # unpacks into tuple of: (type, version, width, height)
del header
del img

# Basic Encoders/Decoders - Python has various codecs built-in. E.g:
for codec in ['latin_1', 'utf_8', 'utf_16']:
    print(codec, "El Niño".encode(codec), sep="\t")

# Note: these codecs all define mappings between Unicode code points and the raw byte 
# representation (with bytes expressed as 2-digit hexadecimal numbers).
# So the "ñ" char has code point:
print("ñ code point:", ord("ñ")) # ord returns Unicode code points for given character
print("Code point 241: ", chr(241)) # chr returns the character corresponding to a given code point

# The codecs then map between Unicode and bytes:
print("ñ in latin1 (hexa f1):", b"\xf1".decode("latin1")) # hexa f1 in latin1
print("ñ in utf-8 (hexa c3 b1):", b"\xc3\xb1".decode("utf-8")) # hexa c3 b1 in utf-8
print("ñ in latin1 (hexa ff fe f1 00):", b"\xff\xfe\xf1\x00".decode("utf-16")) # hexa ff fe f1 00 in utf-16

# Can use encode to get the byte representation:
print("ñ in latin1:", "ñ".encode("latin1"))
print("ñ in utf-8:", "ñ".encode("utf-8"))
print("ñ in utf-16:", "ñ".encode("utf-16"))

# Can use decode and ord to get the code point from the byte representation:
print("ñ code point:", ord(b"\xc3\xb1".decode("utf-8")))
 
 # Unicode code points cover a range of characters, e.g. chinese, musical notes etc:
print("Unicode code point U+6C23:", chr(int("6C23",16))) # U+6C23 (i.e. hexa 6c 23) - gives 㰣
print("Unicode code point U+1D11E:", chr(int("1D11E",16))) # U+1D11E (i.e. hexa 1 D1 1E) - gives 𝄞

print("㰣 in utf-8", "㰣".encode("utf-8")) # result is hexa: E3 B0 A3
print("𝄞 in utf-8", "𝄞".encode("utf-8"))# result is hexa: F0 9D 84 9E

# There's two types of UnicodeError in Python:
# UnicodeEncodeError - can't convert a given string to a binary sequence.
# UnicodeDecodeError - can't convert a given binary sequence to a string

# Encode Error happens when the Unicode code point is not mapped in the encoding, e.g.:
try:
    print("㰣".encode("latin1"))
except UnicodeEncodeError as e:
    print(e)

# In the encode function, can specify "replace" to replace unknow chars with "?"
print("Chinese Char: 㰣".encode("latin1", errors="replace"))

# Can also ignore, but this is unadvisable:
print("Chinese Char: 㰣".encode("latin1", errors="ignore"))


# Decode Error happens if trying to map a binary sequence that's not part of the codec into a character (Unicode code-point)

# E.g. hexa E9 is not part of utf-8:
try:
    print(b"\xE9".decode("utf-8"))
except UnicodeDecodeError as e:
    print(e)

# Although can again replace - this time with the Unicdoe REPALCEMENT CHAR �
print("Replace:", b"\xE9".decode("utf-8", errors="replace"))

# And can ignore:
print("Ignore:", b"\xE9".decode("utf-8", errors="ignore"))

# Note: UTF-8 is the default source encoding for Python. So if you load a .py module containing non-UTF-8 data 
# (with no encoding declaration) you get a SyntaxError

# Also note: given a byte sequence, we can't tell what encoding it represents. We have to be told that. Although some encodings can be
# ruled out, if the sequence containing illegitimate byte sequences in that encoding (e.g. if we see hexa E9, we know the encoding's not UTF-8)

# However some encodings put a "byte-order mark" at the start of the byte sequence, which denotes the endianess of the byte ordering 
# (i.e. litte-endian vs big-endian). 

# In UTF-16 the BOM is hexa FF FE. Recall decoding "ñ":
print("ñ in latin1 (hexa ff fe f1 00):", b"\xff\xfe\xf1\x00".decode("utf-16")) # hexa ff fe f1 00 in utf-16

# Can in fact drop the BOM:
print("ñ in latin1 (hexa f1 00):", b"\xf1\x00".decode("utf-16")) # hexa ff fe f1 00 in utf-16

# The BOM is put at the start of the sequence (regardless of length), not for each character:
print([hex(i) for i in list("Hello World".encode("UTF-16"))])
print([hex(i) for i in list("Another string".encode("UTF-16"))])

# Note that the Unicode code point U+FEFF is "ZERO WIDTH NO-BREAK SPACE", although the codec filters it out when displaying the text
# Although a little-endian machine puts the least significant byte first - hence the utf-16 encoding is "\xFF\xFE"

# Note: endianess only affects encodings which use words of more than one byte. UTF-8 only uses one byte, hence is not affected - one reason for its ubiquity
# So UTF-8 doesn't need a BOM (although some apps like Notepad/Excel add it anyway)

# Handling Text File
# The best way to handle text files is the "Unicode sandwich":

# Input: decode bytes -> str
# Process text only
# Output: encode str -> bytes

# That is, don't convert between string and bytes in the middle of text processing, only at the input/output bookends of the processing.

# The built-in open() supports this model, when opening and writing files in text mode. my_file.open() 
# and my_file.write(text) return only str objects

# Assuming an encoding can be dangerous - e.g. the utf-8 encoding for "é" is hexa C3 A9. 
# However, in the default windows encoding, CP1252, these bytes are mapped to C3 -> "Ã"  and A9 -> "©"
# Hence, if we write the text string "café" with the utf-8 encoding, then open it in Windows Python, without 
# specifying an encoding, it will dispaly as "cafÃ©".

# Note: distinct Unicode code points can appear identical, e.g. code point U+0301 combines the previous char 
# with an acute accent:
print("a\u0301")  
print("b\u0301")  
print("c\u0301")  
print("hello\u0301")  

# So the two items below look identical:
s1 = "cafe\u0301"
s2 = "café"
print(s1, s2)

# But recall the code point for the "é" is different - 233 (decimal), or E9 (hexa):
print("Code point for 'é':", ord("é"), hex(ord("é")))

# Hence, they compare differently - both are False below:
print(s1 == s2)
print(s1 is s2)

# Note, the first version is counted as 5 characters (counting the accent as the 5th), whereas the second version is 4:
print(len(s1), len(s2))

# However, part of the Unicode standard is that certain combinations of code points are considered "canonical equivalents"
# and applications should treat them as the same. The "e\u0301" and "é" case being one of them.

# We can use the unicodedata.normalize function to interpret this equlivalence. In this case we use "Normalisation Form C"
# (NFC) to compose the code points to produce the shortest equivalent string.
from unicodedata import normalize

print("\nNFC:")
s1_norm_c = normalize('NFC', s1)
s2_norm_c = normalize('NFC', s2)

print(s1_norm_c, s2_norm_c)
print(ord(s1_norm_c[0]), ord(s2_norm_c[0])) # Code Points are equal
print(len(s1_norm_c), len(s2_norm_c))
print(s1_norm_c == s2_norm_c) # True - as compares elements
print(s1_norm_c is s2_norm_c) # False - not the same blocks of memory

# Whereas "NFD" decomposes combined characters into the underlying base char and combining chars:
print("\nNFD:")
s1_norm_d = normalize('NFD', s1)
s2_norm_d = normalize('NFD', s2)

print(s1_norm_d, s2_norm_d)
print(ord(s1_norm_d[0]), ord(s2_norm_d[0])) # Code Points are equal
print(len(s1_norm_d), len(s2_norm_d))
print(s1_norm_d == s2_norm_d) # True - as compares elements
print(s1_norm_d is s2_norm_d) # False - not the same blocks of memory

# Another example is the Ohm sign and Greek capital Omega - both appear identically as: Ω
from unicodedata import name
ohm = "\u2126"
print(ohm, name(ohm), ord(ohm), hex(ord(ohm)))
ohm_c = normalize("NFC", ohm)
print(ohm_c, name(ohm_c), ord(ohm_c))
print(ohm == ohm_c) # False
print(normalize("NFC", ohm) == normalize("NFC", ohm_c)) # True


# Case Folding means essentially converting all letters to lowercase, along with some other transformations.
# Use the str.casefold() method - for latin1 chars, the returns the same result as str.lower(),
# with the exceptions of "μ" and "ß":
micro = "μ"
print(micro, name(micro), micro.casefold())

ss = "ß"
print(ss, name(ss), ss.casefold())

A = "AbCd"
print(A, A.casefold())

# We can take normalisation futher - e.g. by removing diacritics - which can be useful in some contexts
# e.g. Google search for cafe vs café should probably give the same result, as should São Paulo vs Sao Paulo etc...
# This is also useful for URLs.
# The function below will do this form of "stripping down":
from unicodedata import combining 
import string

def shave_marks(txt):
    norm_txt = normalize("NFD", txt) # decompose accented Unicode code points into separate base + accent code points
    shaved = "".join(c for c in norm_txt if not combining(c))
    return normalize("NFC", shaved) # NFC to recombine the decomposed code points

print("café")
print(shave_marks("café"))
print("Herr Voß: • ½ cup of OEtker™ caffè latte • bowl of açaí")
print(shave_marks("Herr Voß: • ½ cup of OEtker™ caffè latte • bowl of açaí"))

# Note: combining() seems to return 0 for standalone letters, and non-zero (the "combining class") for free-floating accent marks (that can be combine with previous chars)
e_nfc = normalize("NFC", "é")
e_nfd = normalize("NFD", "é")
print("é NFC", list(e_nfc), [combining(c) for c in list(e_nfc)])
print("é NFD", list(e_nfd), [combining(c) for c in list(e_nfd)])
print(combining("a"))

# We can go even further and convert common symbols into only ASCII chars:

# Specify the mappings into ASCII - make trans converts the provided chars into their Unicode code points
single_map = str.maketrans("""‚ƒ„†ˆ‹‘’“”•–—˜›""", """'f"*^<''""---~>""")

multi_dict = {
'€': '<euro>',
'…': '...',
'Œ': 'OE',
'™': '(TM)',
'œ': 'oe',
'‰': '<per mille>',
'‡': '**'
}
multi_map = str.maketrans(multi_dict)
multi_map.update(single_map)

print("Multi Map:\n", multi_map)

def dewinize(txt):
    """Replace Win1252 symbols with ASCII chars or sequences"""
    return txt.translate(multi_map)


def shave_marks_latin(txt):
    """Remove all diacritic marks from Latin base characters"""
    norm_txt = normalize('NFD', txt)
    latin_base = False
    keepers = []
    for c in norm_txt:
        if combining(c) and latin_base:
            continue # ignore diacritics on latin base chars
        keepers.append(c)
        
        # If c isn't a combining char, it's a base char:
        if not combining(c):
            latin_base = c in string.ascii_letters
    shaved = "".join(keepers)
    return normalize("NFC", shaved)
            
    

def asciise(txt):
    no_marks = shave_marks_latin(dewinize(txt))
    no_marks = no_marks.replace("ß", "ss")
    return normalize("NFKC", no_marks)

print('“Herr Voß: • ½ cup of OEtker™ caffè latte • bowl of açaí.”')
print(asciise('“Herr Voß: • ½ cup of OEtker™ caffè latte • bowl of açaí.”'))


# Python sorts lists of strings by comparing code points - however this is not suitable for non-ASCII characters
fruits = ['caju', 'atemoia', 'cajá', 'açaí', 'acerola']
print(sorted(fruits)) # ['acerola', 'atemoia', 'açaí', 'caju', 'cajá']

# By default, caju comes before cajá since "u" has a lower code point than "á". However, in Portuguese, cajá should come first
# Similarly, 'açaí' should come before 'acerola' and 'atemoia'

# The standard Python approach to solve this is to use the locale module 
import locale
try:
    locale.setlocale(locale.LC_COLLATE, 'pt_BR.UTF-8') # Not supported on my machine
except Exception as e:
    print(e)

# An alternative is the pyUCA package, which implements the Unicode Collation Algorithm and allows for internationalised sorting.
# pyUCA: https://pypi.org/project/pyuca/
# Unicode Collation Algorithm: https://en.wikipedia.org/wiki/Unicode_collation_algorithm


# The Unicode Standard also provides the Unicode Database, which specifies various apsects of Unicode.
# First and foremost, it contains a table mapping code points to character names.
# It also contains metadata about individual characters, and info on how chars are related
# E.g. whether a char is printable, if it's a letter, if it's a decimal/digit or other numerical symbol
# The str methods isidentifier, isprintable, isdecimal, and isnumeric work based on this data. The 
# casefold() method also uses data from this database.

# The Python Standard Library contains several modules that use a "dual-mode" API - with functions 
# accepting arguments as either strings or bytes, and operating differently depending on the type

# E.g. all functions is the os module accept filenames as either str or byte - since filenames across different
# systems may not be in compatible encodings (and so we can't convert them to strings - have to deal with the raw bytes)
# String filenames are assumed by the module to be encodedin the filesystem encoding. Can see what Python thinks that is below:
import sys
print(sys.getfilesystemencoding())  # utf-8