import random

random.seed(11)

rnd_1 = [random.random() for i in range(100)]
rnd_2 = [random.random() for i in range(100)]

random.seed(11)
rnd_3 = [random.random() for i in range(100)]

print(any([i == j for i,j in zip(rnd_1, rnd_2)])) # Expect False
print(all([i == j for i,j in zip(rnd_1, rnd_3)])) # Expect True
