import unittest
from shared.cards import *


class TestCards(unittest.TestCase):

    def setUp(self):
        self.deck = Deck()
        self.card1 = make_card("Q", "H")
        self.card2 = make_card("J", "D")
        self.card3 = make_card("J", "H")
        self.card4 = make_card(9, "C")
        self.card5 = make_card("K", "S")

        self.hand = Hand()
        self.hand.add_card(self.card1)
        self.hand.add_card(self.card2)
        self.hand.add_card(self.card3)
        self.hand.add_card(self.card4)
        self.hand.add_card(self.card5)

    def tearDown(self):
        self.card1.reset_trump()
        self.card2.reset_trump()
        self.card3.reset_trump()
        self.card4.reset_trump()
        self.card5.reset_trump()

    def test_card_str(self):
        self.assertEquals("QH", str(self.card1))
        self.assertEquals("JD", str(self.card2))
        self.assertEquals("JH", str(self.card3))
        self.assertEquals("9C", str(self.card4))
        self.assertEquals("KS", str(self.card5))

    def test_card_eq(self):
        self.assertEquals(make_card("Q", "H"), self.card1)
        self.assertNotEquals(self.card1, self.card2)

    def test_deck_init(self):
        expected = set()
        for rank in ["9", "10", "J", "Q", "K", "A"]:
            for suit in ["C", "H", "S", "D"]:
                expected.add(rank + suit)
        self.assertEquals(expected, set([str(c) for c in Deck().cards]))

    def test_set_trump(self):
        # Queen of Trump
        self.assertEquals(self.card1.effective_suit, 3)
        self.assertEquals(self.card1.effective_rank, 12)
        self.assertFalse(self.card1.is_trump())
        self.card1.set_trump(3)
        self.assertTrue(self.card1.is_trump())
        self.assertEquals(self.card1.effective_suit, 3)
        self.assertEquals(self.card1.effective_rank, 11)

        # Jack of other suit
        self.assertEquals(self.card2.effective_suit, 1)
        self.assertEquals(self.card2.effective_rank, 11)
        self.assertFalse(self.card2.is_trump())
        self.card2.set_trump(3)
        self.assertTrue(self.card2.is_trump())
        self.assertEquals(self.card2.effective_suit, 3)
        self.assertEquals(self.card2.effective_rank, 14)

        # Jack of Trump
        self.assertEquals(self.card3.effective_suit, 3)
        self.assertEquals(self.card3.effective_rank, 11)
        self.assertFalse(self.card3.is_trump())
        self.card3.set_trump(3)
        self.assertTrue(self.card3.is_trump())
        self.assertEquals(self.card3.effective_suit, 3)
        self.assertEquals(self.card3.effective_rank, 14)

        # Non-trump
        self.assertEquals(self.card4.effective_suit, 0)
        self.assertEquals(self.card4.effective_rank, 9)
        self.assertFalse(self.card4.is_trump())
        self.card4.set_trump(3)
        self.assertFalse(self.card4.is_trump())
        self.assertEquals(self.card4.effective_suit, 0)
        self.assertEquals(self.card4.effective_rank, 9)

        # Diamond trump
        self.card1.reset_trump()
        self.assertEquals(self.card1.effective_suit, 3)
        self.assertEquals(self.card1.effective_rank, 12)
        self.assertFalse(self.card1.is_trump())
        self.card1.set_trump(1)
        self.assertFalse(self.card1.is_trump())
        self.assertEquals(self.card1.effective_suit, 3)
        self.assertEquals(self.card1.effective_rank, 12)

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
