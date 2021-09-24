from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from gsheets import mixins

import celery


class Deck(models.Model):

    def get_cards(self):
        return self.card_set


class Hand(models.Model):
    def get_cards(self):
        return self.card_set


class DiscardPile(models.Model):
    pass


class DealtCards(models.Model):
    def get_cards(self):
        return self.card_set


class Game(models.Model):
    deck = models.ForeignKey('Deck', on_delete=models.CASCADE, null=True, blank=True)
    discard_pile = models.ForeignKey(DiscardPile, on_delete=models.CASCADE, null=True, blank=True)
    dealt_cards = models.ForeignKey(DealtCards, on_delete=models.CASCADE, null=True, blank=True)
    state = models.IntegerField(max_length=2000, null=True, blank=True, default=0)
    money_pool = models.IntegerField(default=0)
    small_bet = models.IntegerField(default=0)


class Player(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    hand = models.ForeignKey(Hand, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=2000, null=True, blank=True)
    score = models.IntegerField(null=True, blank=True, default=0)
    money = models.IntegerField(default=2000)
    money_put = models.IntegerField(default=0)
    previous_choice = models.IntegerField(null=True, blank=True)


class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, null=True, blank=True)
    hand = models.ForeignKey(Hand, on_delete=models.CASCADE, null=True, blank=True)
    dealt_cards = models.ForeignKey(DealtCards, on_delete=models.CASCADE, null=True, blank=True)
    discard_pile = models.ForeignKey(DiscardPile, on_delete=models.CASCADE, null=True, blank=True)
    suit = models.CharField(max_length=2000, null=True, blank=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.value}{self.suit}'


class LearningData(models.Model, mixins.SheetPushableMixin):
    spreadsheet_id = ''
    sheet_name = ''

    decision = models.IntegerField(default=1)
    game_state = models.IntegerField(null=True, blank=True)
    hand_1_val = models.IntegerField(null=True, blank=True)
    hand_1_suit = models.IntegerField(null=True, blank=True)
    hand_2_val = models.IntegerField(null=True, blank=True)
    hand_2_suit = models.IntegerField(null=True, blank=True)
    card_1_val = models.IntegerField(default=0)
    card_1_suit = models.IntegerField(default=0)
    card_2_val = models.IntegerField(default=0)
    card_2_suit = models.IntegerField(default=0)
    card_3_val = models.IntegerField(default=0)
    card_3_suit = models.IntegerField(default=0)
    card_4_val = models.IntegerField(default=0)
    card_4_suit = models.IntegerField(default=0)
    card_5_val = models.IntegerField(default=0)
    card_5_suit = models.IntegerField(default=0)
    total_money = models.FloatField(default=0)
    money_put = models.FloatField(default=0)
    opp_money = models.FloatField(default=0)
    opp_money_put = models.FloatField(default=0)
    money_pool = models.FloatField(default=0)

class LearningModels(models.Model):
    type = models.CharField(max_length=2000, null=True, blank=True)
    learning_model = models.BinaryField()
    accuracy = models.FloatField()
    creation_date = models.DateField(default=datetime.now)
    data_amount = models.IntegerField(default=0)


@receiver(post_save, sender=LearningData)
def learningdata_post_save(sender, **kwargs):
    """
    Updates learning models every 50 data entries, and spreadsheet every 20 entries
    """
    learning_data, created = kwargs["instance"], kwargs["created"]
    if created:
        pass
        if learning_data.id % 50 == 0:
            celery.current_app.send_task('game.tasks.update_spreadsheets')

