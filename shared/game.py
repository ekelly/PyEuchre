from random import randint
from cards import Deck

MAX_SCORE = 10
STICK_THE_DEALER = True


class Player():

    def __init__(self, _id):
        self.id = _id
        self.partner = (_id + 2) % 4
        self.team = _id % 2
        self.cards = Hand()
        self.score = 0
        self.name = "Computer Player %d" % (_id + 1)

    def from_human_player(self):
        pass

    def to_computer_player(self):
        pass

    def update(self, game_state):
        pass

    def rename(self, name):
        self.name = name


class ComputerPlayer(Player):

    def __init__(self, _id):
        Player.__init__(_id)

    def from_human_player(self):
        pass


class HumanPlayer(ComputerPlayer):

    def __init__(self, _id):
        Player.__init__(self, id)

    def to_computer_player(self):
        pass

    def update(self, game_state):
        """Update a human player by sending the json over sockets"""
        pass


class Game():

    def __init__(self):
        self.rounds = []
        self.players = [ComputerPlayer(_id) for _id in range(4)]
        self.scores = [0, 0]
        self.current_round = None

    def join_game(self, player_num):
        if isinstance(self.players[player_num], HumanPlayer):
            raise JoinError("That player has already been claimed")
        else:
            self.players[player_num] = HumanPlayer(player_num)
            return True

    def leave_game(self, player_num):
        pass

    def play_card(self, json_data):
        if not self.game_over():
            # do the thing
            self.current_round.next_turn()

            if self.current_round.round_over():
                # Update the scores
                self.scores[0] += self.current_round.team_score(0)
                self.scores[1] += self.current_round.team_score(1)

                if self.game_over():
                    # TODO: Do game over stuff
                    pass

                # make a new round
                dealer = self.current_round.dealer
                dealer = self.current_round.next_player(dealer)
                self.current_round = Round(dealer)

                # Send updates to all the players
                for player in self.players:
                    # TODO: Figure out how to send updates
                    pass

    def start_game(self):
        dealer = randint(0, 3)
        current_round = Round(dealer)
        while not self.game_over():
            while not current_round.round_over():
                # TODO: Update players

                # TODO: Wait for player response

                # Increment the turn
                current_round.next_turn()
                pass
            # Update the scores
            self.scores[0] += current_round.team_score(0)
            self.scores[1] += current_round.team_score(1)
        self.rounds.append(Round(dealer))

    def game_over(self):
        return self.scores[0] >= MAX_SCORE or self.scores[1] >= MAX_SCORE


class Trick():

    def __init__(self):
        self.initial_card = None
        self._cards = [None for x in range(4)]
        pass

    def set_player_card(self, player, card):
        """Indicate that the player played card"""
        if self.initial_card is None:
            self.initial_card = card
        self._cards[player] = card

    def trick_winner(self):
        """Assumes that all players have played a card"""
        played_cards = filter(lambda x: x is not None, self._cards)
        follow_suit = self.initial_card.effective_suit
        current_winner = self.initial_card
        for c in played_cards:
            current_winner = self.max(current_winner, c, follow_suit)
        return self._cards.index(current_winner)

    def trick_done(self):
        for c in self._cards:
            if c is None:
                return False
        return True

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
        print str([str(c) for c in self._cards])


class Round():
    """A Round is a sequence of 5 tricks"""

    def __init__(self, dealer):
        deck = Deck()
        self.tricks = []
        self.hands = [Hand(deck.deal(5)) for x in range(4)]
        self.round_state = "bid"  # Other valid states: "bid2", "play", "end"
        self.called_trump = None  # Nobody has called trump yet
        self.trump = None         # Initially, there is no trump
        self.dealer = dealer      # Player num
        self.turn = (dealer + 1) % 4  # Who starts?
        self.maybe_trump = deck.deal(1)  # The card that might be trump
        self.going_alone = False  # Is the player who called trump going alone?

    def next_turn(self):
        """Increment the turn counter"""
        self.turn = self.next_player(self.turn)

    @staticmethod
    def next_player(player):
        return (player + 1) % 4

    def set_trump(self, player, trump):
        self.called_trump = player
        self.trump = trump
        self.round_state = "play"
        self.turn = self.next_player(self.dealer)

    def verify_valid_trump(self, player, trump):
        if self.round_state == "bid":
            if trump != self.maybe_trump.trump:
                raise CallTrumpError("Invalid suit")
            return player == self.turn
        elif self.round_state == "bid2":
            if trump == self.maybe_trump.trump:
                raise CallTrumpError("Cannot choose trump suit")
            return player == self.turn
        else:
            raise CallTrumpError("Invalid round state to call trump")

    def call_trump(self, player, trump, going_alone=False):
        if player == self.turn:
            if trump is not None:
                if self.verify_valid_trump(player, trump):
                    self.set_trump(player, trump)
                self.going_alone = going_alone
            else:
                if self.round_state == "bid":
                    if player == self.dealer:
                        self.round_state = "bid2"
                elif self.round_state == "bid2" and player == self.dealer:
                    if STICK_THE_DEALER:
                        raise CallTrumpError("Dealer is stuck")
                    else:
                        self.hands = [[] for x in range(4)]
                        self.round_state = "end"
            self.next_turn()

    def play_card(self, player, card):
        if player == self.turn and card in self.hands[player]:
            current_trick = self.tricks[-1]
            if current_trick.is_done():
                self.turn = current_trick.trick_winner()
                current_trick = Trick()
                self.tricks.append(current_trick)
            if self.hands[player].valid_card(card, current_trick.initial_card):
                current_trick.set_player_card(player, card)
                self.hands[player].remove_card(card)
                self.next_turn()
        for hand in self.hands:
            if len(hand) != 0:
                break
        else:
            self.round_state = "end"

    def player_tricks(self, player):
        win_count = 0
        for trick in self.tricks:
            if trick is not None and trick.trick_winner() == player:
                win_count += 1
        return win_count

    def team_tricks(self, team):
        return self.player_tricks(team) + self.player_tricks(team + 2)

    def team_score(self, team, ):
        tricks_taken = self.team_tricks(team)
        if self.called_trump == team:
            if tricks_taken == 5:
                if self.going_alone:
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

    def round_over(self):
        return self.round_state == "end"


class Hand():

    def __init__(self, cards=None):
        if cards is None:
            cards = []
        self._cards = cards

    def add_card(self, card):
        """Add a card to the hand"""
        self._cards.append(card)

    def remove_card(self, card):
        """Remove a card from the hand"""
        self._cards.remove(card)

    def sorted_hand(self, trump):
        """
        Side Effect: Sets trump on the entire hand
        :return: Sorted hand
        """
        self.set_trump(trump)
        return sorted(self._cards)

    def set_trump(self, trump):
        """Sets trump on the entire hand"""
        for c in self._cards:
            c.set_trump(trump)
        return self._cards

    def valid_card(self, card, suit_led=None):
        """Is the card valid to play given the suit led?"""
        return suit_led is None or card in self.valid_cards(suit_led)

    def valid_cards(self, suit_led):
        """Return the list of valid cards"""
        follow_suit = filter(lambda c: c.effective_suit == suit_led,
                             self._cards)
        if len(follow_suit) > 0:
            return follow_suit
        else:
            return self._cards

    def __str__(self):
        hand = []
        if len(self._cards) != 0:
            trump = self._cards[0].trump
            for c in self.sorted_hand(trump):
                hand.append(str(c))
        return str(hand)

    def __len__(self):
        return len(self._cards)


class EuchreError(RuntimeError):

    def __init__(self, message=""):
        self.message = message


class JoinError(EuchreError):
    pass


class CallTrumpError(EuchreError):
    pass


__author__ = 'eric'
