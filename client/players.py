import json


class Player():

    def __init__(self, _id, client):
        self.id = _id
        self.client = client
        self.name = "Computer Player %d" % (_id + 1)
        self.ready = True
        self.human = True

    def send_data(self, response, data):
        d = json.dumps({
            "response": response,
            "payload": data
        })
        print "sending data", d
        self.client.send(d)

    def update(self, game_state):
        self.send_data("gamestate", game_state.to_dict())

    def update_pregame(self, pregame_state):
        self.send_data("pregame", pregame_state.to_dict())

    def __str__(self):
        return self.name


class ComputerPlayer(Player):

    def __init__(self, _id, client):
        Player.__init__(self, _id, client)
        self.human = False

    def from_human_player(self):
        pass

    def update(self, game_state):
        Player.update(self, game_state)


class HumanPlayer(Player):

    def __init__(self, _id, client):
        Player.__init__(self, _id, client)
        self.ready = False

    def update(self, game_state):
        """Update a human player by sending the json over sockets"""
        # print str(game_state.to_json())
        pass

    def update_pregame(self, pregame_state):
        print str(pregame_state.to_json())


__author__ = 'eric'
