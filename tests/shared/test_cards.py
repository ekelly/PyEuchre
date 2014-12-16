import unittest
from shared.cards import *


class TestCards(unittest.TestCase):

    def setUp(self):
        self.deck = Deck()
        self.card = [None for i in range(5)]
        self.card[0] = make_card("Q", "H")
        self.card[1] = make_card("J", "D")
        self.card[2] = make_card("J", "H")
        self.card[3] = make_card(9, "C")
        self.card[4] = make_card("K", "S")

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

        self.assertEquals(self.card[0], EuchreCard.from_str("QH"))
        self.assertEquals(self.card[1], EuchreCard.from_str("JD"))
        self.assertEquals(self.card[2], EuchreCard.from_str("JH"))
        self.assertEquals(self.card[3], EuchreCard.from_str("9C"))
        self.assertEquals(self.card[4], EuchreCard.from_str("KS"))

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


def make_card(rank, suit):
    return EuchreCard.from_str(str(rank) + suit)


if __name__ == '__main__':
    unittest.main()

__author__ = 'eric'
