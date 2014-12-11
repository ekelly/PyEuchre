from cards import Hand, Round


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


class Game():

    def __init__(self):
        self.rounds = []
        self.players = [ComputerPlayer(_id) for _id in range(4)]
        self.scores = [0, 0]

    def join_game(self, player_num):
        if isinstance(self.players[player_num], HumanPlayer):
            raise JoinError("That player has already been claimed")
        else:
            self.players[player_num] = HumanPlayer(player_num)
            return True

    def leave_game(self, player_num):
        pass

    def start_game(self):
        self.rounds.append(Round(0, ))


class JoinError(RuntimeError):

    def __init__(self, message=""):
        self.message = message


__author__ = 'eric'
