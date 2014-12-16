from shared.cards import Hand


class Player():

    def __init__(self, _id):
        self.id = _id
        self.partner = (_id + 2) % 4
        self.team = _id % 2
        self.hand = Hand()
        self.score = [0, 0]
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

    def __init__(self, _id):
        Player.__init__(_id)

    def from_human_player(self):
        pass


class HumanPlayer(Player):

    def __init__(self, _id):
        Player.__init__(self, _id)
        self.ready = False

    def to_computer_player(self):
        pass

    def update(self, game_state):
        """Update a human player by sending the json over sockets"""
        print str(game_state.to_json())

    def update_pregame(self, pregame_state):
        print str(pregame_state.to_json())

    def set_readiness(self, ready):
        self.ready = ready

__author__ = 'eric'
