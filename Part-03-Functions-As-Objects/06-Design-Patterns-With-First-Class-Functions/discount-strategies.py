"""
Implements a generic, abstract discount "strategy" class, then implements different specific discount
types by inheriting from the abstract parent.

The structure of classes follows the diagram on p168
"""
from abc import ABC, abstractmethod
from collections import namedtuple

Customer = namedtuple("Cusomter", "name Fidelity")

class LineItem:
    
    def __init__(self, product, quantity, price):
        self.product = product
        self.quantity = quantity
        self.price = price
    
    def total(self):
        return self.quantity * self.price
    

class Order: # the Context
    
    def __init__(self, customer, cart, promotion=None):
        self.customer = customer
        self.cart = list(cart)
        self.promotion = promotion
        
    def total(self):
        if not hasattr(self, "__total"):
            self.__total = sum(item.total() for item in self.cart)
            return self.__total
        return self.__total
    
    def due(self):
        if self.promotion is None:
            discount = 0
        else:
            discount = self.promotion.discount(self)
        return self.total() - discount
    
    def __repr__(self):
        fmt = "<Order total: {:.2f} due: {:.2f}>"
        return fmt.format(self.total(), self.due())
    

class Promotion(ABC): # the Strategy - an abstract base class
    
    @abstractmethod # decorator means child sub-classes must implement the method, othewise get an error
    def discount(self, order):
        """Return a discount as a positive amount"""
        

class FidelityPromo(Promotion): # the first Concrete strategy
    """5% discount for customers with 1000 or more Fidelity points"""
    
    def discount(self, order):
           return order.total() * 0.05 if order.customer.Fidelity >= 1000 else 0
       

class BulkItemPromo(Promotion): # the second Concrete strategy
    """10% discount for each LineItem with 20 or more units"""
    
    def discount(self, order):
        discount = 0
        for item in order.cart:
            if item.quantity >= 20:
                discount += item.total() * 0.1
        return discount
    

class LargeOrderPromo(Promotion): # the third Concrete strategy
    """7% discount for orders with 10 or more distinct items"""
    
    def discount(self, order):
        distinct_items = {item.product for item in order.cart}
        if len(distinct_items) >= 10:
            return order.total() * 0.07
        return 0


print("\nTest Order:")
# Test Fidelity Promo - 5% off for customers with Fidelity points >1000
joe = Customer("Joe Schmoe", 0)
ann = Customer("Ann Smith", 1100)

cart = [LineItem("banana", 4, 0.5),
        LineItem("apple", 10, 1.5),
        LineItem("watermelon", 5, 5.0)]  # Raw Total: 2 + 15 + 25 = 42

print(Order(joe, cart,  FidelityPromo())) # No Discount: 42
print(Order(ann, cart,  FidelityPromo())) # 5% Discount: 0.95 * 42 = 39.9


# Test Bulk Item Promo - 10% off items with quantity >= 20
banana_cart = [LineItem("banana", 30, 0.5),
               LineItem("apple", 10, 1.5)] # Raw Total: 15 + 15 = 30

print(Order(joe, banana_cart)) # No Discount: 30
print(Order(joe, banana_cart,  BulkItemPromo())) # Discount 10% on bulk items: 13.5 + 15 = 28.5


# Test Larger Order Promo - 7% off orders with 10 or more distinct items
long_order = [LineItem(str(i), 1, 1.0) for i in range(10)] # Raw Total: 10 * 1 * 1 = 10
print(Order(joe, long_order))
print(Order(joe, long_order, LargeOrderPromo())) # 7% discount: 9.30


# We could alternatively implement the promos as functions - rather than as inheritors from a base class, with only one method:
class OrderFnc: # the Context
    """
    Idential to Order, except in the due() method:
    discount = self.promotion.discount(self)
    changed to:
    discount = self.promotion(self) 
    """
    
    def __init__(self, customer, cart, promotion=None):
        self.customer = customer
        self.cart = list(cart)
        self.promotion = promotion
        
    def total(self):
        if not hasattr(self, "__total"):
            self.__total = sum(item.total() for item in self.cart)
            return self.__total
        return self.__total
    
    def due(self):
        if self.promotion is None:
            discount = 0
        else:
            discount = self.promotion(self)
        return self.total() - discount
    
    def __repr__(self):
        fmt = "<Order total: {:.2f} due: {:.2f}>"
        return fmt.format(self.total(), self.due())


def fidelity_promo(order): # the first Concrete strategy
    """5% discount for customers with 1000 or more Fidelity points"""
    
    return order.total() * 0.05 if order.customer.Fidelity >= 1000 else 0
       

def bulk_item_promo(order): # the second Concrete strategy
    """10% discount for each LineItem with 20 or more units"""

    discount = 0
    for item in order.cart:
        if item.quantity >= 20:
            discount += item.total() * 0.1
    return discount
    

def large_order_promo(order): # the third Concrete strategy
    """7% discount for orders with 10 or more distinct items"""
    
    distinct_items = {item.product for item in order.cart}
    if len(distinct_items) >= 10:
        return order.total() * 0.07
    return 0


print("\nTest OrderFnc:")
print(OrderFnc(joe, cart, fidelity_promo)) # No Discount: 42
print(OrderFnc(ann, cart, fidelity_promo)) # 5% Discount: 0.95 * 42 = 39.9

print(OrderFnc(joe, banana_cart)) # No Discount: 30
print(OrderFnc(joe, banana_cart, bulk_item_promo)) # Discount 10% on bulk items: 13.5 + 15 = 28.5

print(OrderFnc(joe, long_order))
print(OrderFnc(joe, long_order, large_order_promo)) # 7% discount: 9.30

# Don't need to instantiate a new Promo object for each order - simply provide the function. 
# And no abstract class is required
# Note: the discount functions have no internal state - their outcome depends only on the context in which they're applied

# The functional approach makes it straightforward to find the best promo, for a given order:
promos = [fidelity_promo, bulk_item_promo, large_order_promo]

def best_promo(order):
    return max(promo(order) for promo in promos)

# Since this reutrns a function, we can use this as the promo when creating the order:
print("\n Test Best Promo:")
print(OrderFnc(joe, long_order, best_promo)) # large_order_promo
print(OrderFnc(joe, banana_cart, best_promo)) # bulk_item_promo
print(OrderFnc(ann, cart, best_promo)) # fidelity_promo

# We can have the list of promos automatically include all functions whose names end in "_promo" - so don't have to 
# remember to add new promos to the list

def flat_promo(order):
    """ Flat 1% discount"""
    return order.total() * 0.01

promos = [globals()[name] for name in globals()
          if name.endswith("_promo") 
          and name != "best_promo"]

def best_promo(order):
    return max(promo(order) for promo in promos)

print("\n Test Best Promo and new promos list:")
print(OrderFnc(joe, long_order, best_promo)) # large_order_promo
print(OrderFnc(joe, banana_cart, best_promo)) # bulk_item_promo
print(OrderFnc(ann, cart, best_promo)) # fidelity_promo
print(OrderFnc(joe, cart)) # no promo
print(OrderFnc(joe, cart, best_promo)) # flat_promo


# An alternative to using globals would be to put all discount promo functions into a separate "promotions" module,
# then import them and get their names using the inspect package, e.g. with code like:

# promos = [func for name, func in inspect.getmembers(promotions, inspect.isfunction)]

# Although this assumes that the "promotions" module contains only these discount-calculating functions, and no other functions

