# Registration module - see p185 of book
registry = []

def register(func):
    print("Running register({})".format(func))
    registry.append(func)
    return func

@register
def f1():
    print("Running f1()")
    
@register
def f2():
    print("Running f2()")
    
# Don't decorate
def f3():
    print("Running f3()")
    
def main():
    print("Running main()")
    print("Registry:", registry)
    f1()
    f2()
    f3()
    
if __name__ == "__main__":
    main()