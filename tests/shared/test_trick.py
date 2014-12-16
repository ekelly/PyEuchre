import unittest
from shared.cards import EuchreCard
from shared.game import Trick


class TestTrick(unittest.TestCase):

    def setUp(self):
        self.card = [None for i in range(5)]
        self.card[0] = EuchreCard.from_str("QH")
        self.card[1] = EuchreCard.from_str("JD")
        self.card[2] = EuchreCard.from_str("JH")
        self.card[3] = EuchreCard.from_str("9C")
        self.card[4] = EuchreCard.from_str("KS")
        self.trick = Trick()

    def tearDown(self):
        self.card[0].reset_trump()
        self.card[1].reset_trump()
        self.card[2].reset_trump()
        self.card[3].reset_trump()
        self.card[4].reset_trump()

    def test_set_player_card(self):
        self.trick.set_player_card(1, self.card[1])
        self.assertEquals(self.card[1], self.trick._cards[1])
        self.assertEquals(self.card[1], self.trick.initial_card)
        self.trick.set_player_card(2, self.card[2])
        self.assertEquals(self.card[2], self.trick._cards[2])
        self.assertEquals(self.card[1], self.trick.initial_card)
        self.assertIsNone(self.trick._cards[0])
        self.assertIsNone(self.trick._cards[3])

    def test_trick_winner(self):
        self.trick.set_player_card(0, self.card[0])
        self.assertEquals(0, self.trick.trick_winner())
        self.trick.set_player_card(1, self.card[1])
        self.trick.set_player_card(2, self.card[2])
        self.trick.set_player_card(3, self.card[3])
        self.assertEquals(0, self.trick.trick_winner())
        for c in self.card:
            c.set_trump(3)
        self.assertEquals(2, self.trick.trick_winner())

    def test_trick_winner2(self):
        t = Trick()
        for i in range(4):
            self.card[i].set_trump(3)
            t.set_player_card(i, self.card[i])
        self.assertEquals(2, t.trick_winner())

        for i in range(4):
            self.card[i].set_trump(1)
            t.set_player_card(i, self.card[i])
        self.assertEquals(1, t.trick_winner())

    def test_trick_done(self):
        self.trick.set_player_card(0, self.card[0])
        self.trick.set_player_card(1, self.card[1])
        self.trick.set_player_card(2, self.card[2])
        self.assertFalse(self.trick.trick_done())
        self.trick.set_player_card(3, self.card[3])
        self.assertTrue(self.trick.trick_done())


if __name__ == '__main__':
    unittest.main()

__author__ = 'eric'
