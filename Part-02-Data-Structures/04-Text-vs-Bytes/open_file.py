with open("word.txt", "r") as fp:
    lines = fp.readlines()

for item in lines:
    print(item)
    print("--")