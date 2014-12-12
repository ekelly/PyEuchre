import unittest
from shared.cards import *
from shared.game import Trick, Hand


class TestCards(unittest.TestCase):

    def setUp(self):
        self.deck = Deck()
        self.card = [None for i in range(5)]
        self.card[0] = make_card("Q", "H")
        self.card[1] = make_card("J", "D")
        self.card[2] = make_card("J", "H")
        self.card[3] = make_card(9, "C")
        self.card[4] = make_card("K", "S")

        self.hand = Hand()
        self.hand.add_card(self.card[0])
        self.hand.add_card(self.card[1])
        self.hand.add_card(self.card[2])
        self.hand.add_card(self.card[3])
        self.hand.add_card(self.card[4])

    def tearDown(self):
        self.card[0].reset_trump()
        self.card[1].reset_trump()
        self.card[2].reset_trump()
        self.card[3].reset_trump()
        self.card[4].reset_trump()

    def test_card_str(self):
        self.assertEquals("QH", str(self.card[0]))
        self.assertEquals("JD", str(self.card[1]))
        self.assertEquals("JH", str(self.card[2]))
        self.assertEquals("9C", str(self.card[3]))
        self.assertEquals("KS", str(self.card[4]))

    def test_card_eq(self):
        self.assertEquals(make_card("Q", "H"), self.card[0])
        self.assertNotEquals(self.card[0], self.card[1])

    def test_deck_init(self):
        expected = set()
        for rank in ["9", "10", "J", "Q", "K", "A"]:
            for suit in ["C", "H", "S", "D"]:
                expected.add(rank + suit)
        self.assertEquals(expected, set([str(c) for c in Deck().deal(24)]))

    def test_set_trump(self):
        # Queen of Trump
        self.assertEquals(self.card[0].effective_suit, 3)
        self.assertEquals(self.card[0].effective_rank, 12)
        self.assertFalse(self.card[0].is_trump())
        self.card[0].set_trump(3)
        self.assertTrue(self.card[0].is_trump())
        self.assertEquals(self.card[0].effective_suit, 3)
        self.assertEquals(self.card[0].effective_rank, 11)

        # Jack of other suit
        self.assertEquals(self.card[1].effective_suit, 1)
        self.assertEquals(self.card[1].effective_rank, 11)
        self.assertFalse(self.card[1].is_trump())
        self.card[1].set_trump(3)
        self.assertTrue(self.card[1].is_trump())
        self.assertEquals(self.card[1].effective_suit, 3)
        self.assertEquals(self.card[1].effective_rank, 14)

        # Jack of Trump
        self.assertEquals(self.card[2].effective_suit, 3)
        self.assertEquals(self.card[2].effective_rank, 11)
        self.assertFalse(self.card[2].is_trump())
        self.card[2].set_trump(3)
        self.assertTrue(self.card[2].is_trump())
        self.assertEquals(self.card[2].effective_suit, 3)
        self.assertEquals(self.card[2].effective_rank, 14)

        # Non-trump
        self.assertEquals(self.card[3].effective_suit, 0)
        self.assertEquals(self.card[3].effective_rank, 9)
        self.assertFalse(self.card[3].is_trump())
        self.card[3].set_trump(3)
        self.assertFalse(self.card[3].is_trump())
        self.assertEquals(self.card[3].effective_suit, 0)
        self.assertEquals(self.card[3].effective_rank, 9)

        # Diamond trump
        self.card[0].reset_trump()
        self.assertEquals(self.card[0].effective_suit, 3)
        self.assertEquals(self.card[0].effective_rank, 12)
        self.assertFalse(self.card[0].is_trump())
        self.card[0].set_trump(1)
        self.assertFalse(self.card[0].is_trump())
        self.assertEquals(self.card[0].effective_suit, 3)
        self.assertEquals(self.card[0].effective_rank, 12)

    def test_hand_sort(self):
        expected = ["9C", "KS", "QH", "JD", "JH"]
        # 3 is Hearts
        self.assertEquals(expected, [str(c) for c in self.hand.sorted_hand(3)])
        for c in self.hand.cards:
            self.assertEquals(3, c.trump)

        # 1 is diamonds
        expected = ["KS", "QH", "9C", "JH", "JD"]
        self.assertEquals(expected, [str(c) for c in self.hand.sorted_hand(1)])
        for c in self.hand.cards:
            self.assertEquals(1, c.trump)

    def test_trick_winner(self):
        t = Trick()
        for i in range(4):
            self.card[i].set_trump(3)
            t.set_player_card(i, self.card[i])
        self.assertEquals(2, t.trick_winner())

        for i in range(4):
            self.card[i].set_trump(1)
            t.set_player_card(i, self.card[i])
        self.assertEquals(1, t.trick_winner())


def make_card(rank, suit):
    r = rank
    s = suit
    if isinstance(rank, basestring):
        r = 10 + ["J", "Q", "K", "A"].index(rank) + 1
    if isinstance(suit, basestring):
        s = ['C', 'D', 'S', 'H'].index(suit)
    return EuchreCard(r, s)


if __name__ == '__main__':
    unittest.main()

__author__ = 'eric'
