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
    suit_order = ['clubs', 'diamonds', 'spades', 'hearts']
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


class Trick():

    def __init__(self):
        self.initial_card = None
        self.__cards = [None for x in range(4)]
        pass

    def set_player_card(self, player, card):
        """Indicate that the player played card"""
        if self.initial_card is None:
            self.initial_card = card
        self.__cards[player] = card

    def trick_winner(self):
        """Assumes that all players have played a card"""
        follow_suit = self.initial_card.effective_suit
        current_winner = self.initial_card
        for c in self.__cards:
            current_winner = self.max(current_winner, c, follow_suit)
        return self.__cards.index(current_winner)

    @staticmethod
    def max(c1, c2, suit_led):
        """Given the suit which has been led, which card is higher?"""
        if c1.effective_suit == c2.effective_suit:
            if c1.effective_rank == c2.effective_rank:
                if c1.suit == c1.trump:
                    return c1
                else:
                    return c2
            if c1.effective_rank > c2.effective_rank:
                return c1
            else:
                return c2
        else:
            if c1.is_trump():
                return c1
            if c2.is_trump():
                return c2
            if c1.effective_suit == suit_led:
                return c1
            else:
                return c2

    def __str__(self):
        print str([str(c) for c in self.__cards])


class Round():
    """A Round is a sequence of 5 tricks"""

    def __init__(self):
        self.tricks = [None for x in range(5)]

    def player_tricks(self, player):
        win_count = 0
        for trick in self.tricks:
            if trick is not None and trick.trick_winner() == player:
                win_count += 1
        return win_count

    def team_tricks(self, team):
        return self.player_tricks(team) + self.player_tricks(team + 2)

    def team_score(self, team, called_trump, going_alone=False):
        tricks_taken = self.team_tricks(team)
        if called_trump == team:
            if tricks_taken == 5:
                if going_alone:
                    return 4
                else:
                    return 2
            if tricks_taken > 2:
                return 1
            else:
                return 0
        else:
            if tricks_taken > 2:
                return 2
            return 0


class Hand():

    def __init__(self):
        self.cards = []

    def add_card(self, card):
        """Add a card to the hand"""
        self.cards.append(card)

    def sorted_hand(self, trump):
        """Side Effect: Sets trump on the entire hand"""
        for c in self.cards:
            c.set_trump(trump)
        return sorted(self.cards)

    def valid_card(self, card, suit_led):
        """Is the card valid to play given the suit led?"""
        return card in self.valid_cards(suit_led)

    def valid_cards(self, suit_led):
        """Return the list of valid cards"""
        follow_suit = filter(lambda c: c.effective_suit == suit_led, self.cards)
        if len(follow_suit) > 0:
            return follow_suit
        else:
            return self.cards

    def __str__(self):
        hand = []
        if len(self.cards) != 0:
            trump = self.cards[0].trump
            for c in self.sorted_hand(trump):
                hand.append(str(c))
        return str(hand)


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