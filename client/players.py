from shared.cards import EuchreCard, CardError


class Player():

    def __init__(self, _id, game):
        self.id = _id
        self.game = game
        self.partner = (_id + 2) % 4
        self.team = _id % 2
        self.hand = None
        self.scores = [0, 0]
        self.name = "Computer Player %d" % (_id + 1)
        self.ready = True

    def from_human_player(self):
        pass

    def to_computer_player(self):
        pass

    def update(self, game_state):
        pass

    def update_pregame(self, pregame_state):
        pass

    def play_card(self):
        pass

    def set_readiness(self, ready):
        pass

    def rename(self, name):
        self.name = name

    def __str__(self):
        return self.name


class ComputerPlayer(Player):

    def __init__(self, _id, game):
        Player.__init__(_id, game)

    def from_human_player(self):
        pass

    def update(self, game_state):
        r = game_state.current_round
        self.hand = r.hands[self.id]
        if r.round_state == "bid":
            if r.turn == self.id:
                if r.trump is None:
                    self.call_trump(r.maybe_trump)
                else:
                    self.exchange_card()
        elif r.round_state == "bid2":
            if r.turn == self.id:
                if r.dealer != self.id:
                    self.call_trump2(r.maybe_trump)
                else:
                    self.actually_call_trump2(r.maybe_trump)
        else:
            if r.turn == self.id:
                print "My hand: %s" % str(self.hand)
                self.play_card()

    def play_card(self):
        self.game.play_card(self.id, self.hand.valid_cards()[0])

    def call_trump(self, maybe_trump):
        self.game.call_trump(self.id, None)

    def call_trump2(self, maybe_trump):
        self.game.call_trump(self.id, None)

    def actually_call_trump2(self, maybe_trump):
        s = (maybe_trump.suit + 1) % 4
        self.game.call_trump(self.id, ['C', 'D', 'S', 'H'][s])

    def exchange_card(self):
        cards = self.hand.valid_cards()
        self.game.exchange_trump(self.id, cards[0])
        self.hand.remove_card(cards[0])


class HumanPlayer(Player):

    def __init__(self, _id, game):
        Player.__init__(self, _id, game)
        self.ready = False

    def update(self, game_state):
        """Update a human player by sending the json over sockets"""
        print str(game_state.to_json())

    def update_pregame(self, pregame_state):
        print str(pregame_state.to_json())

    def set_readiness(self, ready):
        self.ready = ready


class HumanConsolePlayer(HumanPlayer):

    def __init__(self, _id, game):
        HumanPlayer.__init__(self, _id, game)
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
                self.game.play_card(self.id, card)
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
            self.game.call_trump(self.id, maybe_trump.trump)
        elif t == "N":
            self.game.call_trump(self.id, None)
        elif t == "G":
            self.game.call_trump(self.id, maybe_trump.trump, True)
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
                self.game.call_trump(self.id, t, True)
            else:
                self.game.call_trump(self.id, t)
        elif t == "N":
            self.game.call_trump(self.id, None)
        else:
            print "Please input C/D/S/H/N"
            self.call_trump2(maybe_trump)

    def exchange_card(self):
        c = raw_input("Which card do you want to return?")
        try:
            card = EuchreCard.from_str(c)
            if card in self.hand:
                self.game.exchange_trump(self.id, card)
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
                pregame_state.ready_status[i]

__author__ = 'eric'
