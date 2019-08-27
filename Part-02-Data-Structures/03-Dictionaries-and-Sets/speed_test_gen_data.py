import random
import array

MAX_EXPONENT = 7
HAYSTACK_LEN = 10**MAX_EXPONENT
NEEDLES_LEN = 10**(MAX_EXPONENT-1)
SAMPLE_LEN = HAYSTACK_LEN + NEEDLES_LEN//2

needles = array.array("d")

sample = {1/random.random() for i in range(SAMPLE_LEN)}
print("Initial sample: {} elements".format(len(sample)))

# Duplicate sample values would be removed (as sample is a set), so keep adding to the set until it's at the required length
while len(sample) < SAMPLE_LEN:
    sample.add(1/random.random())
print("Sample complete: {} {}".format(len(sample), SAMPLE_LEN))

sample = array.array("d", sample)
random.shuffle(sample)

# Save not selected to file
not_selected = sample[:NEEDLES_LEN//2]
print("Not selected sample: {}".format(len(not_selected)))

print("Writing not_selected...")
with open("not_selected.arr", "wb") as fp:
    not_selected.tofile(fp)
print("not_selected written")



# Save selected to file
selected = sample[NEEDLES_LEN//2:]
print("Selected sample: {}".format(len(selected)))

print("Writing selected...")
with open("selected.arr", "wb") as fp:
    selected.tofile(fp)
print("selected written")