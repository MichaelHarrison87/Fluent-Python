"""
Script to get the positions (line no, column no) of each word in a given (command line arg) text file
To run this on the-zen-of-python.txt enter on the command line:
python get_word_indices.py the-zen-of-python.txt
"""
import sys
import re # regular expressions

WORD_RE = re.compile("\w+") # \w is the "word characeter" regex

# Scrap the file, recording the position of each word
index = {}
with open(sys.argv[1], encoding="utf-8") as fp:
    for line_no, line in enumerate(fp, 1):
        for match in WORD_RE.finditer(line):
            word = match.group()
            column_no = match.start() + 1
            location = (line_no, column_no)
            
            # The below can be replaced using the setdefault() dict method - see get_word_indices_set_default.py
            occurences = index.get(word, []) # use empty list (mutable) as default value - subsequent matches then modify this list
            occurences.append(location)
            index[word] = occurences
            
# Print the words (and all locations) in alphabetical order:
for word in sorted(index, key = str.upper):
    print(word, index[word]) 
 