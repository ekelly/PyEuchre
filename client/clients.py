from shared.cards import EuchreCard, CardError
from multiprocessing import Process, Pipe
from client.players import *
import os
import json

# Players are what the server sees
# Clients are what the individual user sees


def make_computer_player(_id):
    server, client = Pipe()
    p = Process(target=make_computer_client, args=(_id, server))
    p.start()
    return ComputerPlayer(_id, client)


def make_computer_client(_id, connection):
    p = ComputerClient(_id, connection)
    p.receive_data()


def make_human_player(_id):
    server, client = Pipe()
    p = Process(target=make_human_client, args=(_id, server))
    p.start()
    return HumanPlayer(_id, client)


def make_human_client(_id, connection):
    p = HumanConsoleClient(_id, connection)
    p.receive_data()


class Client():

    def __init__(self, _id, server):
        self.id = _id
        self.server = server
        self.partner = (_id + 2) % 4
        self.team = _id % 2
        self.hand = None
        self.scores = [0, 0]
        self.name = "Computer Player %d" % (_id + 1)
        self.ready = True

    @staticmethod
    def game_over(scores):
        return scores[0] >= 10 or scores[1] >= 10

    def receive_data(self):
        while True:
            print os.getpid(), "( player ", self.id, ") is waiting for data"
            data = self.server.recv()
            if data:
                print "Received data: ", data
                try:
                    j = json.loads(data)
                    if "response" in j and "payload" in j:
                        state = j["response"]
                        payload = j["payload"]
                        if state == "gamestate":
                            if self.game_over(payload["scores"]):
                                break
                            self.update(payload)
                        elif state == "pregame":
                            self.update_pregame(payload)
                        else:
                            raise RuntimeError("Invalid server response")
                    else:
                        raise RuntimeError("Invalid server response")
                except RuntimeError:
                    pass
        print "Game over!"

    def send_data(self, request, data):
        try:
            js = json.dumps({
                "player": self.id,
                "request": request,
                "payload": data
            })
            self.server.send_bytes(js)
        except RuntimeError:
            raise RuntimeError("Invalid json")

    def update(self, game_state):
        print "updating client", game_state
        pass

    def update_pregame(self, pregame_state):
        pass

    def send_trump(self, trump, going_alone=False):
        t_possibles = ["H", "D", "S", "C", None]
        if trump in t_possibles:
            self.send_data("trump", {
                "trump": trump,
                "goingAlone": going_alone
            })
        else:
            raise RuntimeError("Invalid trump")

    def send_card(self, card):
        self.send_data("playCard", str(card))

    def send_discard(self, card):
        self.send_data("discard", str(card))

    def send_readiness(self, ready):
        self.send_data("ready", ready)

    def send_rename(self, name):
        self.send_data("namechange", name)

    def __str__(self):
        return self.name


class ComputerClient(Client):

    def __init__(self, _id, server):
        Client.__init__(self, _id, server)

    def from_human_player(self):
        pass

    def update(self, game_state):
        print "updating computer client"
        r = game_state["round"]
        self.hand = r["hands"][self.id]
        if r["roundState"] == "bid":
            if r["turn"] == self.id:
                if r["trump"] is None:
                    self.call_trump(r["maybeTrump"])
                else:
                    self.exchange_card()
        elif r["roundState"] == "bid2":
            if r["turn"] == self.id:
                if r["dealer"] != self.id:
                    self.call_trump2(r["maybeTrump"])
                else:
                    self.actually_call_trump2(r["maybeTrump"])
        else:
            if r["turn"] == self.id:
                print "My hand: %s" % str(self.hand)
                self.play_card()

    def update_pregame(self, pregame_state):
        print pregame_state

    def play_card(self):
        print "Player", self.id, "plays card"
        self.send_card(self.hand.valid_cards()[0])

    def call_trump(self, maybe_trump):
        print "Player", self.id, "calls trump"
        self.send_trump(None)

    def call_trump2(self, maybe_trump):
        print "Player", self.id, "calls trump2"
        self.send_trump(None)

    def actually_call_trump2(self, maybe_trump):
        print "Player", self.id, "actually calls trump"
        s = (maybe_trump.suit + 1) % 4
        self.send_trump(['C', 'D', 'S', 'H'][s])

    def exchange_card(self):
        print "Player", self.id, "exchanges card"
        cards = self.hand.valid_cards()
        self.send_discard(cards[0])
        self.hand.remove_card(cards[0])


class HumanClient(Client):

    def __init__(self, _id, game):
        Client.__init__(self, _id, game)
        self.ready = False

    def update(self, game_state):
        """Update a human player by sending the json over sockets"""
        print str(game_state.to_json())

    def update_pregame(self, pregame_state):
        print str(pregame_state.to_json())

    def set_readiness(self, ready):
        self.ready = ready

    def rename(self, name):
        self.name = name


class HumanConsoleClient(HumanClient):

    def __init__(self, _id, game):
        HumanClient.__init__(self, _id, game)
        self.name = "Human Player %d" % (self.id + 1)
        self.players = []

    def update(self, game_state):
        if self.scores != game_state.scores:
            self.scores = game_state.scores
            print "Current score: Us - %d, Them - %d" % \
                  (self.scores[self.team], self.scores[self.team + 1 % 2])
        if self.players != game_state.players:
            self.players = game_state.players
            print "Players: %s" % str(game_state.players)
        r = game_state.current_round
        self.hand = r.hands[self.id]
        if r.round_state == "bid":
            if r.turn == self.id:
                if r.trump is None:
                    print "My hand: %s" % str(self.hand)
                    print "Maybe trump? %s" % str(r.maybe_trump)
                    self.call_trump(r.maybe_trump)
                else:
                    self.exchange_card()
        elif r.round_state == "bid2":
            if r.turn == self.id:
                print "My hand: %s" % str(self.hand)
                self.call_trump2(r.maybe_trump)
        else:
            current_trick = r.tricks[-1]
            print "Current trick: %s" % str(current_trick)
            if r.turn == self.id:
                print "My hand: %s" % str(self.hand)
                self.play_card()

    def play_card(self):
        c = raw_input("Which card do you want to play?")
        try:
            card = EuchreCard.from_str(c)
            if card in self.hand:
                self.send_card(str(card))
                self.hand.remove_card(card)
            else:
                print "That card is not in your hand. Try again"
                self.play_card()
        except CardError:
            print "That is not a valid card. Try again"
            self.play_card()

    def call_trump(self, maybe_trump):
        t = raw_input("Call trump? (Y/N/G)")
        if t == "Y":
            self.send_trump(maybe_trump.get_suit_str())
        elif t == "N":
            self.send_trump(None)
        elif t == "G":
            self.send_trump(maybe_trump.get_suit_str(), True)
        else:
            print "Please input Y/N/G"
            self.call_trump(maybe_trump)

    def call_trump2(self, maybe_trump):
        t = raw_input("Call trump? (C/D/S/H/N)")
        if t == maybe_trump.suit:
            print "You cannot choose the trump suit you previously passed on"
            self.call_trump2(maybe_trump)
        elif t == "C" or t == "D" or t == "S" or t == "H":
            g = raw_input("Go alone? (Y/[N])")
            if g == "Y":
                self.send_trump(t, True)
            else:
                self.send_trump(t)
        elif t == "N":
            self.send_trump(None)
        else:
            print "Please input C/D/S/H/N"
            self.call_trump2(maybe_trump)

    def exchange_card(self):
        c = raw_input("Which card do you want to return?")
        try:
            card = EuchreCard.from_str(c)
            if card in self.hand:
                self.send_discard(str(card))
                self.hand.remove_card(card)
            else:
                print "That card is not in your hand. Try again"
                self.exchange_card()
        except CardError:
            print "That is not a valid card. Try again"
            self.exchange_card()

    def update_pregame(self, pregame_state):
        print "You are player %d." % pregame_state.player_num
        print "Current players: %s" % str(pregame_state.players)
        for i in range(len(pregame_state.players)):
            print pregame_state.players[i] + ": " + \
                str(pregame_state.ready_status[i])

__author__ = 'eric'
