from django.contrib import admin

# Register your models here.
from .models import Deck, Hand, DiscardPile, DealtCards, Game, Player, Card

admin.site.register(Deck)
admin.site.register(Hand)
admin.site.register(DiscardPile)
admin.site.register(DealtCards)
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Card)