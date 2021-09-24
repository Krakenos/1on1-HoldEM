from rest_framework import serializers

from game.models import Card, Game, Hand, DealtCards, Deck, Player


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['suit', 'value']


class DeckSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = ['cards']

    def get_cards(self, obj):
        cards = obj.get_cards()
        return CardSerializer(cards, many=True).data


class DealtCardsSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField()

    class Meta:
        model = DealtCards
        fields = ['cards']

    def get_cards(self, obj):
        cards = obj.get_cards()
        return CardSerializer(cards, many=True).data


class HandSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField()

    class Meta:
        model = Hand
        fields = ['cards']

    def get_cards(self, obj):
        cards = obj.get_cards()
        return CardSerializer(cards, many=True).data


class PlayerHandSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField()

    class Meta:
        model = Hand
        fields = ['cards']

    def get_cards(self, obj):
        cards = obj.get_cards()
        return CardSerializer(cards, many=True).data


class PlayerSerializer(serializers.ModelSerializer):
    hand = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['type', 'hand', 'money', 'money_put']

    def get_hand(self, obj):
        cards = obj.hand.get_cards()
        return CardSerializer(cards, many=True).data


class GameSerializer(serializers.ModelSerializer):
    dealt_cards = DealtCardsSerializer(read_only=True)
    hand = serializers.SerializerMethodField()
    cpu_hand = serializers.SerializerMethodField()
    money_bet = serializers.SerializerMethodField()
    money_total = serializers.SerializerMethodField()
    opponent_bet = serializers.SerializerMethodField()
    opponent_total = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['hand', 'money_bet', 'money_total', 'opponent_bet', 'opponent_total', 'dealt_cards',
                  'cpu_hand', 'money_pool']

    def get_hand(self, obj):
        for player in obj.player_set.all():
            if player.type == 'Human':
                return CardSerializer(player.hand.card_set, many=True).data
        return None

    def get_cpu_hand(self, obj):
        for player in obj.player_set.all():
            if player.type == 'CPU':
                return CardSerializer(player.hand.card_set, many=True).data
        return None

    def get_money_bet(self, obj):
        for player in obj.player_set.all():
            if player.type == 'Human':
                return player.money_put
        return None

    def get_money_total(self, obj):
        for player in obj.player_set.all():
            if player.type == 'Human':
                return player.money
        return None

    def get_opponent_bet(self, obj):
        for player in obj.player_set.all():
            if player.type == 'CPU':
                return player.money_put
        return None

    def get_opponent_total(self, obj):
        for player in obj.player_set.all():
            if player.type == 'CPU':
                return player.money
        return None
