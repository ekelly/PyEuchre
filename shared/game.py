from random import randint
from cards import Deck
from client.players import ComputerPlayer, HumanPlayer
import json

MAX_SCORE = 10
STICK_THE_DEALER = True


class Game():

    def __init__(self):
        self.rounds = []
        self.scores = [0, 0]
        self.current_round = None
        self.players = [ComputerPlayer(_id) for _id in range(4)]

    def join_game(self, player_num):
        if isinstance(self.players[player_num], HumanPlayer):
            raise JoinError("That player has already been claimed")
        else:
            self.players[player_num] = HumanPlayer(player_num)
            return True

    def leave_game(self, player_num):
        pass

    def call_trump(self, player, trump, going_alone=False):
        if not self.game_over() and self.current_round.round_state == "bid" \
                or self.current_round.round_state == "bid2":
            # Do the thing
            self.current_round.call_trump(player, trump, going_alone)

            # Update the players
            self.update_players()

    def play_card(self, player, card):
        if not self.game_over() and self.current_round.round_state == "play":
            # do the thing
            self.current_round.play_card(player, card)

            # Increment the turn counter
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
            self.update_players()
        else:
            raise GameError("Game is over")

    def start_game(self):
        for p in self.players:
            if not p.ready:
                break
        else:
            dealer = randint(0, 3)
            self.rounds.append(Round(dealer))
            self.update_players()

    def game_over(self):
        return self.scores[0] >= MAX_SCORE or self.scores[1] >= MAX_SCORE

    def update_players(self):
        for player in range(len(self.players)):
            # If the game hasn't started yet
            if self.current_round is None:
                g = PreGameState(player, [str(p) for p in self.players],
                            [p.ready for p in self.players])
                self.players[player].update_pregame(g)
            else:
                g = PlayerGameState(player, self.current_round.clone(player),
                               [str(p) for p in self.players], self.scores)
                self.players[player].update(g)


class PlayerGameState():

    def __init__(self, player_num, round, players, scores):
        self.player_num = player_num
        self.players = players
        self.current_round = round
        self.scores = scores

    def to_json(self):
        j = {
            "playerNum": self.player_num,
            "players": self.players,
            "round": self.current_round.to_dict(),
            "scores": self.scores
        }
        return json.dumps(j)


class PreGameState():

    def __init__(self, player_num, players=None, ready_status=None):
        self.player_num = player_num
        self.players = players
        self.ready_status = ready_status

    def to_json(self):
        j = {
            "playerNum": self.player_num,
            "players": self.players,
            "readyStatus": self.ready_status
        }
        return json.JSONEncoder().encode(j)


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

    def to_dict(self):
        return {
            "initialCard": str(self.initial_card),
            "cards": [str(c) for c in self._cards],
            "winner": self.trick_winner()
        }

    def __str__(self):
        print str([str(c) for c in self._cards])


class Round():
    """A Round is a sequence of 5 tricks"""

    def __init__(self, dealer, tricks=None, hands=None, round_state=None,
                 called_trump=None, trump=None, turn=None, maybe_trump=None,
                 going_alone=None):
        deck = Deck()
        self.tricks = tricks or []
        self.hands = hands or [Hand(deck.deal(5)) for x in range(4)]
        # Other valid states: "bid2", "play", "end"
        self.round_state = round_state or "bid"
        self.called_trump = called_trump or None  # Nobody has called trump yet
        self.trump = trump or None                # Initially, there is no trump
        self.dealer = dealer                      # Player num
        self.turn = turn or (dealer + 1) % 4      # Who starts?
        # The card that might be trump
        self.maybe_trump = maybe_trump or deck.deal(1)
        # Is the player who called trump going alone?
        self.going_alone = going_alone or False

    def clone(self, player):
        hands = self.hands
        if player is not None:
            for i in range(len(hands)):
                if i != player:
                    hands[i] = len(hands[i])
        return Round(dealer=self.dealer, tricks=self.tricks, hands=hands,
                     round_state=self.round_state,
                     called_trump=self.called_trump, trump=self.trump,
                     turn=self.turn, maybe_trump=self.maybe_trump,
                     going_alone=self.going_alone)

    def to_dict(self):
        hands = self.hands
        for i in range(len(self.hands)):
            if isinstance(self.hands[i], Hand):
                hands[i] = self.hands[i].to_json()
        return {
            "tricks": self.tricks.to_dict(),
            "hands": hands,
            "roundState": self.round_state,
            "calledTrump": self.called_trump,
            "trump": self.trump,
            "turn": self.turn,
            "maybeTrump": str(self.maybe_trump),
            "goingAlone": self.going_alone
        }

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


class EuchreError(RuntimeError):

    def __init__(self, message=""):
        self.message = message


class JoinError(EuchreError):
    pass


class CallTrumpError(EuchreError):
    pass

class GameError(EuchreError):
    pass


__author__ = 'eric'
