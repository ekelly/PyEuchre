import unittest
from shared.cards import EuchreCard
from shared.game import Hand


class TestHand(unittest.TestCase):

    def setUp(self):
        self.card = [None for i in range(5)]
        self.card[0] = EuchreCard.from_str("QH")
        self.card[1] = EuchreCard.from_str("JD")
        self.card[2] = EuchreCard.from_str("JH")
        self.card[3] = EuchreCard.from_str("9C")
        self.card[4] = EuchreCard.from_str("KS")

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

    def test_sorted_hand(self):
        expected = ["9C", "KS", "QH", "JD", "JH"]
        # 3 is Hearts
        self.assertEquals(expected, [str(c) for c in self.hand.sorted_hand(3)])
        for c in self.hand._cards:
            self.assertEquals(3, c.trump)

        # 1 is diamonds
        expected = ["KS", "QH", "9C", "JH", "JD"]
        self.assertEquals(expected, [str(c) for c in self.hand.sorted_hand(1)])
        for c in self.hand._cards:
            self.assertEquals(1, c.trump)

    def test_set_trump(self):
        self.hand.set_trump(1)
        for c in self.hand._cards:
            self.assertEquals(1, c.trump)

    def test_valid_card(self):
        self.hand.set_trump(1)
        self.assertTrue(self.hand.valid_card(self.card[0]))
        self.assertTrue(self.hand.valid_card(self.card[1]))
        self.assertTrue(self.hand.valid_card(self.card[2]))
        self.assertTrue(self.hand.valid_card(self.card[3]))
        self.assertTrue(self.hand.valid_card(self.card[4]))

        self.assertTrue(self.hand.valid_card(self.card[0], 3))
        self.assertFalse(self.hand.valid_card(self.card[0], 0))
        self.assertTrue(self.hand.valid_card(self.card[1], 1))
        self.assertFalse(self.hand.valid_card(self.card[1], 3))
        self.assertTrue(self.hand.valid_card(self.card[2], 1))
        self.assertFalse(self.hand.valid_card(self.card[2], 3))
        self.assertTrue(self.hand.valid_card(self.card[3], 0))
        self.assertFalse(self.hand.valid_card(self.card[3], 1))
        self.assertTrue(self.hand.valid_card(self.card[4], 2))
        self.assertFalse(self.hand.valid_card(self.card[4], 3))

if __name__ == '__main__':
    unittest.main()

__author__ = 'eric'
