"""
Script to get the positions (line no, column no) of each word in a given (command line arg) text file.
This is a copy of get_word_indices.py, but instead using the setdefault() dict method for cleaner code
To run this on the-zen-of-python.txt enter on the command line:
python get_word_indices_set_default.py the-zen-of-python.txt

Note: my_dict.setdefault(key, []).append(new_value) is equiv to:

if key not in my_dict:
my_dict[key] = []
my_dict[key].append(new_value)

However the setdefault() approach performs only a single key lookup, vs 2 or 3 (depending on if key is present) for the other approach
"""
import sys
import re # regular expressions
import collections

WORD_RE = re.compile("\w+") # \w is the "word characeter" regex

# Scrap the file, recording the position of each word
index = collections.defaultdict(list) # list is the default_factory - produces an empty list if key is missing
with open(sys.argv[1], encoding="utf-8") as fp:
    for line_no, line in enumerate(fp, 1):
        for match in WORD_RE.finditer(line):
            word = match.group()
            column_no = match.start() + 1
            location = (line_no, column_no)
            
            index[word].append(location) 
            
# Print the words (and all locations) in alphabetical order:
for word in sorted(index, key = str.upper):
    print(word, index[word]) 
 