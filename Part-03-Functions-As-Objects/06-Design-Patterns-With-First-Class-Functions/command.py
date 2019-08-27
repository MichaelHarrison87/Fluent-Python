"""
See UML diagram on p178
The Command design pattern has an intermediate Command class between the Invoker (e.g. a menu in an application) 
and the specific commands on that menu (Open, Paste, Macro)

The book reccomends instead simply sending functions to the Invoker, rather than going via a Command class. The 
Macro class is made up of several commands - but can implement this by making it callable. I.e. implementing 
__call__. Then its instances are callable, and can be used as-if they were functions. Each instance will
be made up of a specific sequence of other commands.
"""

class MacroCommand:
    """Callable class that executes a list of commands"""
    
    def __init__(self, commands):
        self.commands = list(commands)
    
    def __call__(self):
        for command in self.commands:
            command()
            
"""
This is supposed to be equivalent to a callback. Callbacks can be used to ensure operations are done in the correct order,
e.g. add user "Mike" to database, then get list of users. If adding the user takes longer than getting the list
of users, running these in sequence may give unexpected result - with "Mike" missing from the list of users.
A callback could solve this by:

def add_user(name, callback):
    users.append(name)
    callback()

def get_users():
    print(users)

We could then apply the callback by:
add_user("Mike", get_users)

Then the two operations will certainly in executed in the correct order.

Callbacks in general are executable code passed as arguments to other functions, where the function is expected to
"call back" (i.e. execute) that provided code at some point
"""