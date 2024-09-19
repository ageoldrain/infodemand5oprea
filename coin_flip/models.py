from otree.api import *
from otree.models.participant import Participant as oTreeParticipant
import numpy as np
import random

class ChooseCoin(Page):
    form_model = 'player'
    form_fields = ['coin_choice']

    def vars_for_template(self):
        # Define and shuffle the two coins
        coins = ['Fair', 'Biased']  # Capitalize here
        random.shuffle(coins)
        
        return {
            'coins': coins,
            'fair_left': self.session.vars.get('fair_left', 0),
            'biased_left': self.session.vars.get('biased_left', 0),
            'round_number': self.round_number
        }

    def is_displayed(self):
        return self.round_number <= C.NUM_ROUNDS

    def before_next_page(self):
        # Flip the chosen coin after the player makes a choice
        self.player.flip_chosen_coin(p_fair=P_FAIR, p_biased=P_BIASED)

doc = """
Curiosity and Information Demand
"""

debug = False

class C(BaseConstants):
    NAME_IN_URL = 'economics_experiment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10

class Player(BasePlayer):
    # Choice between 'fair' or 'biased' coin
    coin_choice = models.StringField(choices=['fair', 'biased'])

    # Choice between HH, TT, HT, TH  where format is [Fair][Bias]
    coin_permutation_choice = models.StringField(choices=['HH', 'TT', 'HT', 'TH'], initial='')

    # Results
    chosen_coin_result = models.StringField(initial='')
    chosen_coin_permutation = models.StringField(initial='')
    coin_permutation_result = models.StringField(initial='')

    total_winnings = models.CurrencyField(initial=cu(0))

    # New fields for guessing the outcome of each coin individually
    fair_outcome = models.StringField(
        choices=['H', 'T'],
        widget=widgets.RadioSelect,
        label="Your guess for the outcome of the Fair coin"
    )

    biased_outcome = models.StringField(
        choices=['H', 'T'],
        widget=widgets.RadioSelect,
        label="Your guess for the outcome of the Biased coin"
    )

    def flip_chosen_coin(self, p_fair: float, p_biased: float):
        """
        Flip the chosen coin and store the result.
        
        For simplicity, we assume:
        - 'fair' coin has equal probability of Heads or Tails (e.g., 0.5).
        - 'biased' coin's probability is given by p_biased.
        """
        assert 0 <= p_fair <= 1, "Probability for the fair coin must be between 0 and 1."
        assert 0 <= p_biased <= 1, "Probability for the biased coin must be between 0 and 1."

        # Check second question was not answered yet and is empty
        if self.coin_permutation_choice == '':
            if self.coin_choice == 'fair':
                self.chosen_coin_result = 'H' if np.random.rand() < p_fair else 'T'
            else:
                self.chosen_coin_result = 'H' if np.random.rand() < p_biased else 'T'
        else:
            if self.coin_choice == 'fair':
                # Flip the biased coin since fair was already flipped
                second_coin_result = 'H' if np.random.rand() < p_biased else 'T'
                # Concatenate the string outcomes
                self.coin_permutation_result = self.chosen_coin_result + second_coin_result
            else:
                # Flip the fair coin since biased was already flipped
                second_coin_result = 'H' if np.random.rand() < p_fair else 'T'
                # Concatenate the string outcomes
                self.coin_permutation_result = second_coin_result + self.chosen_coin_result

            # Concatenate the string outcomes
            self.coin_permutation_result = self.chosen_coin_result + second_coin_result

            # Add winnings if the chosen permutation matched the simulated flippings
            if self.coin_permutation_result == self.coin_permutation_choice:
                # Give a dollar
                self.total_winnings += cu(1)

            if debug:
                print(f'permutation choice: {self.coin_permutation_choice}')
                print(f'permutation result: {self.coin_permutation_result}')
                print(self.coin_permutation_result == self.coin_permutation_choice)
                print(sum([player.total_winnings for player in self.in_all_rounds()]))

class Group(BaseGroup):
    pass

class Subsession(BaseSubsession):
    def creating_session(self):
        for player in self.get_players():
            if 'fair_left' not in self.session.vars:
                self.session.vars['fair_left'] = 0  # Or some default value
            if 'biased_left' not in self.session.vars:
                self.session.vars['biased_left'] = 0  # Or some default value
