from otree.api import *
import numpy as np
import random

doc = """
Curiosity and Information Demand
"""

class C(BaseConstants):
    NAME_IN_URL = 'economics_experiment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10

class Player(BasePlayer):
    # Player's choice between 'fair' or 'biased' coin
    coin_choice = models.StringField(choices=['fair', 'biased'])

    # Player's guess for the outcome of both coins
    fair_outcome = models.StringField(choices=['H', 'T'], initial='')
    biased_outcome = models.StringField(choices=['H', 'T'], initial='')

    # Combined permutation choice and result fields
    coin_permutation_choice = models.StringField(choices=['HH', 'TT', 'HT', 'TH'], initial='')
    chosen_coin_result = models.StringField(initial='')
    coin_permutation_result = models.StringField(initial='')

    total_winnings = models.CurrencyField(initial=cu(0))

    # Coin flip logic for each round
    def flip_chosen_coin(self, p_fair: float, p_biased: float):
        assert 0 <= p_fair <= 1, "Fair coin probability must be between 0 and 1."
        assert 0 <= p_biased <= 1, "Biased coin probability must be between 0 and 1."

        # Flip the chosen coin
        if self.coin_choice == 'fair':
            self.chosen_coin_result = 'H' if np.random.rand() < p_fair else 'T'
        elif self.coin_choice == 'biased':
            self.chosen_coin_result = 'H' if np.random.rand() < p_biased else 'T'

        # Combine coin outcomes for winnings calculation
        if self.coin_permutation_choice == self.coin_permutation_result:
            self.total_winnings += cu(1)

class Group(BaseGroup):
    pass

class Subsession(BaseSubsession):
    def creating_session(self):
        # Initialize session-level variables if needed
        if 'fair_left' not in self.session.vars:
            self.session.vars['fair_left'] = 0
        if 'biased_left' not in self.session.vars:
            self.session.vars['biased_left'] = 0
