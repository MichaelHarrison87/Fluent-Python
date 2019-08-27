import collections
from random import choice


Card = collections.namedtuple("Card", ["rank", "suit"])
AceOfSpades = Card("A", "spades")

class FrenchDeck:
    """
    Implements a standard deck of 52 playing cards: ranks 2-9 + JKQA; suits spades, diamonds, clubs, hearts
    """


    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = ["spades", "diamonds", "clubs", "hearts"]
    
    def __init__(self):
        # _var denotes private variables
        self._cards = [Card(rank, suit) for suit in self.suits 
                                        for rank in self.ranks]
    
    # Allows len() function to work on instances of FrenchDeck, returning the number of cards
    def __len__(self):
        return len(self._cards)
    
    # Allows positional indexing to work, e.g. deck[0], deck[-1]; and also iteration such as 'for card in deck:'
    def __getitem__(self, position):
        return self._cards[position]
    
my_deck  =FrenchDeck()
print(len(my_deck))

for card in my_deck:
    print(card)
print("---\n")
    
# __getitem__() also allows us to use reversed():
for card in reversed(my_deck):
    print(card)
print("---\n")
    
# As well as slicing:
print(my_deck[0:13]) # Picks out the Spades
print("---\n")

print(my_deck[12::13]) # Picks out the Aces (i.e. every 13th card)
print("---\n")

# 'in' also works due to the __getitem__(), as it implicitly iterates over the whole list to check if the object is in:
print(AceOfSpades, AceOfSpades in my_deck)

JokerOfSwords = Card("Joker", "Swords") 
print(JokerOfSwords, JokerOfSwords in my_deck)
print("---\n")

# We can also sort the deck according to supplied rules; e.g. by rank, then by suit within-rank with spades > hearts > diamonds > clubs
suit_values = {"spades": 3, "hearts": 2, "diamonds": 1, "clubs": 0}

def spades_high(card):
    rank_value = FrenchDeck.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]

for card in sorted(my_deck, key = spades_high):
    print(card)
print("---\n")

# __getitem__() also lets us choose items at random
print("Choose cards at random:")
print(choice(my_deck))
print(choice(my_deck))
print(choice(my_deck))
print("---\n")