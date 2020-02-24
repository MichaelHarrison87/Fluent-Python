# Chapter 19 - Dynamic Attributes and Properties [p585]

# Data attributes and methods are collectively know as attributes in Python - a method
# is merely a callable attribute

import json
import os

with open('osconfeed.json') as fp:
    feed = json.load(fp)


print(feed.keys())
# By default, have to index into the JSON as vanilla dict key lookup and list indexing:
print(feed['Schedule']['events'][40]['name'])  # There *Will* Be Bugs


# But could create a data stucture that let us index into the JSON using Python's attribute syntax
# E.g. feed.Schedule.events[40].name
# The class below uses __getattr__ to do this - which is only invoked if the corresponding
# attribute can't be found as a member of the class/instance outright

from collections import abc

class FrozenJSON:

    def __init__(self, mapping):
        self.__data = dict(mapping)
    

    def __getattr__(self, name):

        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            return FrozenJSON.build(self.__data[name])
    
    @classmethod
    def build(cls, obj):

        if isinstance(obj, abc.Mapping):
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            return [cls.build(item) for item in obj]
        else:
            return obj


frozen_feed = FrozenJSON(feed)
print(frozen_feed)

# Can access keys as attributes:
print(frozen_feed.Schedule.events[40].name) # There *Will* Be Bugs

# Get KeyError if key not present:
try:
    frozen_feed.invalid
except Exception as e:
    print(repr(e))  # KeyError('invalid')


# And indexing for illegal names (e.g. keywords) doesn't work:
illegal_name = FrozenJSON({'name': 'Mike', 'class': 'Python'})

# Code below causes the interpreter to throw a SyntaxError (prior to running the script):
# my_class = illegal_name.class

# But, getattr works:
print(getattr(illegal_name, 'class'))   # Python


# The logic of the build class method can be replaced with the __new__ method. This
# method is in fact what creates new instances of classes, not __init__.

# __new__ is a class method (that doesn't require @classmethod decorator) that returns
# a new instance. This new instance will be passed as the first argument, 'self' of the
# __init__ method - __init__ being the "intialiser", that doesn't actually return anything.

# Note: this behaviour is typically inherited from object, and so rarely needs to be 
# used in practice

class FrozenJSON_new:

    def __new__(cls, arg):

        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)     # super() here will call object.__new__(cls)
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg


    def __init__(self, mapping):
        self.__data = dict(mapping)
    

    def __getattr__(self, name):

        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            return FrozenJSON_new(self.__data[name])  # can now just construct the sub-FrozenJSON directly, rather than via a .build() method


frozen_feed_new = FrozenJSON_new(feed)
print(frozen_feed_new.Schedule.events[40].name, frozen_feed_new.Schedule.events[40].serial)   # There *Will* Be Bugs


# Restructuring OSCON Feed with shelve  [p 594 (620 of 766)]
# Want to reformat the data to make it easier to find corresponding events/speakers/venues etc

# Pickle is Python's module for serialising/deserialising Python objects, into byte streams.
# The shelve module provides an interface for pickling and unpickling objects on DBM-style database files.
# A Shelf is a dictionary-style object, whose values (but not keys) can be arbitraty python objects
# i.e. anything that can be pickled

# Now create a dbm to store the OSCON JSON records

# First create a Record class:

class Record:
        def __init__(self, **kwargs):
            """
            This adds the keys & values in kwargs to the instance's __dict__ attribute; it's a
            way to create instances from keyword args - as __dict__ stores an instance's attributes
            """
            self.__dict__.update(**kwargs)   

        def __eq__(self, other):
            if isinstance(other, Record):
                return self.__dict__ == other.__dict__
            else:
                return NotImplemented

class MissingDatabaseError(RuntimeError):
    """Exception to raise when database is missing"""

class DbRecord(Record):
    __db = None   # This wil refer to a Shelf database

    @staticmethod
    def set_db(db):
        DbRecord.__db = db
    
    @staticmethod
    def get_db():
        return DbRecord.__db
    
    @classmethod
    def fetch(cls, ident):
        """Method to lookup an item in the database"""
        db = cls.get_db()
        try:
            return db[ident]
        except TypeError:
            if db is None:
                raise MissingDatabaseError
            else:
                raise
        
    def __repr__(self):
        if hasattr(self, 'serial'):
            cls_name = self.__class__.__name__
            return f'<{self.__class__.__name__} serial={self.serial}>'
        else:
            return super().__repr__()


class Event(DbRecord):

    @property
    def venue(self):
        key = f'venue.{self.venue_serial}'
        return self.__class__.fetch(key)    
    
    @property
    def speakers(self):
        if not hasattr(self, '_speaker_objs'):
            speaker_serials = self.__dict__['speakers']
            fetch = self.__class__.fetch    # use __class__ here in case there is an Event instance with attribute "fetch", which would be returned instead of the fetch method if this line was just self.fetch
            self._speaker_objs = [fetch(f'speaker.{serial}') for serial in speaker_serials]
        return self._speaker_objs

    def __repr__(self):
        if hasattr(self, 'name'):
            return f"<{self.__class__.__name__} {self.name} ({self.serial})>"


class Speaker(DbRecord):

    def __repr__(self):
        if hasattr(self, 'name'):
            return f"<{self.__class__.__name__} {self.name} ({self.serial})>"

# Create the function to add records to the database
import inspect
import warnings
from tqdm import tqdm

def load_db(db, json_feed):
    
    # json_feed['Schedule'] gives a dict with keys (conferences, events, speakers, venues)
    # The values are the lists of each type - i.e. list of events, list of speakers
    # Each item in these lists is a dict with attributes, e.g. the event's start time, the speaker's name
    DbRecord.set_db(db)
    
    for collection, records_list in json_feed['Schedule'].items():
        warnings.warn('Loading database file...')
        record_type = collection[:-1]
        cls_name = record_type.capitalize()     # used to turn "event" key into proper class name "Event"
        cls = globals().get(cls_name, DbRecord)  # if record_type is "event" use the Event class, else the DbRecord class; but this functionality would extent to other record types if we created, e.g., Speaker or Venue classes
        
        if inspect.isclass(cls) and issubclass(cls, DbRecord):
            factory = cls
        else:
            factory = DbRecord
        
        for record in tqdm(records_list, desc=record_type):
            key = f"{record_type}.{record['serial']}"   # e.g. speaker.123, event.40
            record['serial'] = key
            db[key] = factory(**record)


# With shelve, can use this function to add all records to a db file
import shelve

with shelve.open('OSCON_DB') as db:
    load_db(db, feed)

    # Get info on specific speaker:
    speaker = db['speaker.3471']
    print(speaker.serial, speaker.name, speaker.twitter)

    # Or event:
    event = db['event.33950']
    print(f'{event}: {event.name}')

    for speaker in event.speakers:
        print(f'{speaker}: {speaker.name}')


# The @property decorator effectively allows us to have getter/setter methods, 
# but use them via Python attribute access syntax. E.g:


class LineItem:

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price

    @property   # decorate getter method with @property
    def weight(self):
        return self.__weight
    
    @weight.setter
    def weight(self, value):
        """Prevent negative weights"""
        if value > 0:
            self.__weight = value
        else:
            raise ValueError('weight must be > 0')
            

li1 = LineItem('line item 1', 10, 0.5)
print(li1)

try:
    li2 = LineItem('line item 1', -10, 0.5)
except ValueError as e:
    print(repr(e))


# Now if we wanted to ensure prices couldn't be negative, we could repeat the code above, but for price
# But this could get out of hand if doing it for lots of attributes; so a better solution is
# a property factory.

# First, we consider the @property decorator. It's implemented as a class.
# Before decorators were introduced, properties were created as functions within
# classes:

class LineItem_Alt:

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price

    def get_weight(self):
        return self.__weight
    
    def set_weight(self, value):
        """Prevent negative weights"""
        if value > 0:
            self.__weight = value
        else:
            raise ValueError('weight must be > 0')
    
    weight = property(get_weight, set_weight)


li3 = LineItem_Alt('li3', 20, 1.5)
print(li3.weight)   # 20


# Note that properties are class attributes, but manage attribute access for 
# instances of the class. When an instance and a class both have an attribute of
# the same name, the instance version overrides the class version, when accessed via
# the instance:

class Class:
    data = 'class data'
    def __init__(self, dt):
        self.data = dt

cl = Class('instance data')
print(cl.data)  # instance data
print(Class.data) # class data


# In fact, changing an instance's version of a class attribute changes it only for
# that instance, but this does not happed for @properties

class Class2:
    data ='class2 data'

    @property
    def prop(self):
        return 'property data'

# data attribute:
cl2 = Class2()
print(cl2.data) # class2 data
cl2.data = 'new data'
print(cl2.data) # new data
print(Class2.data) # class2 data
cl3 = Class2()
print(cl3.data) # class2 data


# Now try the property - can access it:
print(cl2.prop) # property data
print(Class2.prop) # <property object at 0x7f8279d15e00>

# But can't modify it:
try:
    cl2.prop = 'new prop data'
except Exception as e:
    print(repr(e))  #  AttributeError("can't set attribute")


# We can even try adding it directly to the instance's __dict__:
cl3.__dict__['prop'] = 'foo'
print(vars(cl3)) # {'prop': 'foo'}

# But it stil doesn't override the conventional access pattern:
print(cl3.prop) # property data
print(cl2.prop) # property data

# However if we overwrite the propery at the class level, it will remove it
# for the instance as well, at which point it will look into __dict__ to find a value:

Class2.prop = 'xyz'

print(cl3.prop) # foo

# cl2 doesn't have prop in its __dict__, so it gets the class value:
print(cl2.prop) # xyz

# But adding a property back to the class will again override the instance attribute:
Class2.prop = property(lambda x: 'abcde')

print(cl3.prop) # abcde
print(cl2.prop) # abcde
 
# deleting it, we go back the instance attribute
del Class2.prop

print(cl3.prop) # foo
try:
    print(cl2.prop)
except Exception as e:
    print(repr(e)) # AttributeError("'Class2' object has no attribute 'prop'")


# So the expression obj.attr begins searching for the attr in obj.__class__ and
# only looks in the obj instance if it can't find it there. In fact this applies to
# a range of "overriding descriptors", of which proprties are one.

# Note that the docstring of the function decorated with @property becomes the
# docstring of the property, when called with help or ?


# Coding a Property factory  [p611 (637 of 766)]
# We now implement a LineItem class with a quantity factory method, that will
# let us create as many non-zero attributes as needed:

def quantity(storage_name):

    def qty_getter(instance):
        return instance.__dict__[storage_name]
    
    def qty_setter(instance, value):
        if value > 0:
            instance.__dict__[storage_name] = value
        else:
            raise ValueError('value must be > 0')
    
    # We return the property function, whose syntax is: property(fget, fset, fdel, doc)
    # i.e. we provde it the getter and setter functions
    return property(qty_getter, qty_setter)


class LineItem2:

    weight = quantity('weight')
    price = quantity('price')

    def __init__(self, weight, price, description):
        self.weight = weight
        self.price = price
        self.description = description

    def subtotal(self):
        return self.weight * self.price
    


    
lineitem = LineItem2(10, 1.5, 'melons')
print(lineitem.subtotal())
print(lineitem.weight, type(lineitem.weight))
print(lineitem.price, type(lineitem.price))


# Below we document certain aspects we've been using in this code:

# __class__: a reference to the object's class, obj.__class__ is the same as type(obj).
# Python looks for certain special methods, e.g. __getattr__ here, in the object's class
# rather than in the instances themselves

# __dict__: a dict that stores the writable attributes of an object or a class. Can 
# add items to an object's __dict__ at any time, to give it new attributes. 
# Note that for classes with a __slots__ attribute, their instances may not have a __dict__

# __slots__: a tuple of strings naming the permitted attributes an instance of this class
# can have; attributes not named in __slots__ are not allowed; although can name a __dict__
# attribute in __slots__, which can be written to with arbitrary objects  