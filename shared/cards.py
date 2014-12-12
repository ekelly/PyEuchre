from random import shuffle

# TODO: Make cards immutable?

"""

Players are 0, 1, 2, 3, where the table looks like so:

       2
   1       3
       0

The Canonical "Suit" is one of 0, 1, 2, 3, with the numbers representing
the suits as below.

- "hearts" (3)
- "spades" (2)
- "diamonds" (1)
- "clubs" (0)

The Canonical "Rank" is one of [2-14], with the numbers representing the
ranks as below.

- 2 ... 10
- "J" (11)
- "Q" (12)
- "K" (13)
- "A" (14)

"""


class Card():
    suit_order = ['C', 'D', 'S', 'H']
    rank_order = ["2", "3", "4", "5", "6", "7", "8",
                  "9", "10", "J", "Q", "K", "A"]

    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank

    def get_suit_str(self):
        """
        From a number representing a suit, return the string
        representation of the suit
        :return: String
        """
        return Card.suit_order[self.suit]

    def get_rank_str(self):
        """Return the string representation of the rank"""
        return Card.rank_order[self.rank - 2]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.rank == other.rank and self.suit == other.suit
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.get_rank_str() + self.get_suit_str()[:1].upper()

    def __hash__(self):
        return self.suit * 100 + self.rank


class EuchreCard(Card):
    trump_rank_order = ["2", "3", "4", "5", "6", "7", "8",
                        "9", "10", "Q", "K", "A", "J"]

    def __init__(self, rank, suit):
        Card.__init__(self, rank, suit)
        self.effective_suit = suit
        self.effective_rank = rank
        self.trump = -1

    def is_trump(self):
        """Is this card trump?"""
        return self.effective_suit == self.trump

    def set_trump(self, t):
        """Set the trump suit [0-3] and adjust the card's value accordingly"""
        # It's important to reset trump before resetting the rank, because
        # the rank depends on whether or not this card is trump
        self.trump = t
        if t != -1 and self.get_rank_str() == "J" \
                and (self.trump + 2) % 4 == self.suit:
            self.effective_suit = self.trump
        else:
            self.effective_suit = self.suit

        if self.is_trump():
            rank_val = self.get_rank_str()
            self.effective_rank = self.trump_rank_order.index(rank_val) + 2
        else:
            self.effective_rank = self.rank
        return self

    def reset_trump(self):
        """Reset trump status to not have trump"""
        return self.set_trump(-1)

    def __gt__(self, other):
        """
        Assume: No duplicate cards
        This comparison function is only correct for sorting hands, not
        deciding a trick winner.
        """
        if self.effective_suit == other.effective_suit:
            # if they are both the same effective suit
            if self.is_trump():
                if self.effective_rank == other.effective_rank:
                    # If they are both Jacks
                    return self.suit == self.trump
                else:
                    return self.effective_rank > other.effective_rank
            else:
                return self.rank > other.rank

        # We just want to return which suit is "higher"
        # "higher" means that the suits are always in the same order, modulo
        # some value so that the trump suit is always highest
        return ((self.effective_suit + (3 - self.trump)) % 4) > \
               ((other.effective_suit + (3 - self.trump)) % 4)

    def __lt__(self, other):
        return not self.__gt__(other)


class Deck():

    def __init__(self):
        self.__cards = []
        for suit in range(4):
            for rank in range(9, 15):
                self.__cards.append(EuchreCard(rank, suit))
        shuffle(self.__cards)

    def deal(self, num_cards):
        """return num_cards number of cards from the top of the deck"""
        if num_cards > len(self.__cards):
            raise RuntimeError("Not enough cards left to deal")
        dealt = []
        for i in range(num_cards):
            dealt.append(self.__cards.pop())
        return dealt

__author__ = 'eric'