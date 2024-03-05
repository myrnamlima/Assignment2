from otree.api import *
import random

doc = """
This is the second-price sealed bid auction
"""


class C(BaseConstants):
    NAME_IN_URL = 'auction'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    highest_bid = models.CurrencyField()
    second_highest_bid = models.CurrencyField()
    winning_player = models.IntegerField()
    price = models.CurrencyField()  # in here it is cost that the winning player pay for the good (second_highest_bid)

class Player(BasePlayer):
    bid = models.CurrencyField()
    value = models.CurrencyField(initial=-999) # zero is a non bid, you could use an initial value of -999
    win = models.BooleanField(initial=False) # indicates whether subject won or lost
    price = models.CurrencyField() # in here it is cost that the winning player pay for the good (second_highest_bid)
    is_winner = models.BooleanField(default=False)


## Building functions for players
def creating_session(subsession):
    if subsession.round_number == 1 or subsession.round_number == 6:
        subsession.group_randomly()
    else:
        subsession.group_like_round(subsession.round_number - 1)

    for p in subsession.get_players():
        p.value = random.random()*100
        #p.is_winner = False
        if subsession.round_number == 1:
            p.participant.vars['totalEarnings'] = 0
            p.participant.vars['finished'] = False

def auction_outcome(g: Group): # function process a single group at a time
    players = g.get_players() #get the set of players in the group
    # bids = [p.bid for p in players if p.bid >= 0]
    # get the set of bids from the players
    bids = [p.bid for p in players if p.bid >= 0]
    bids.sort(reverse=True) # sort the bids in descending order

    g.highest_bid = bids[0] # set the highest and second-highest bids to the appropriate group variables
    g.second_highest_bid = bids[1]

    # in the case of a tie
    highest_bidders = [p.id_in_group for p in players if p.bid == g.highest_bid]
    g.winning_player = random.choice(highest_bidders)

    winning_player = g.get_player_by_id(g.winning_player)
    # winning_player.win = True (this is commented out because I was trying to see if the problem was the wrong syntax)
    winning_player.is_winner = True

    for p in players:
        print("player#", p.id_in_group)
        if p.is_winner and p.value >= g.second_highest_bid:
            p.payoff = p.value - g.second_highest_bid
            # p.participant.var['finished'] = True
            print("true")
        else:
            p.payoff = 0
            print("false")
        g.price = g.second_highest_bid


# PAGES


class Bid(Page):
    form_model = 'player'
    form_fields = ['bid'] # html variables


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'auction_outcome' #after all players arrived, execute the following function...
    body_text = 'The other players are placing their bids.'

class Results(Page):
    body_text = "This is the end of the game."


page_sequence = [Bid, ResultsWaitPage, Results]



