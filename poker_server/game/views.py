# Create your views here.
import pickle
import random
from itertools import combinations

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from game.models import Game, Deck, Card, Player, Hand, DiscardPile, DealtCards, LearningData, LearningModels
from game.serializers import GameSerializer
from .tasks import fit_models


def create_deck():
    new_deck = Deck.objects.create()
    suits = ['h', 'c', 's', 'd']
    for suit in suits:
        for value in range(2, 15):
            card = Card.objects.create(deck=new_deck, suit=suit, value=value)
            card.save()
    new_deck.refresh_from_db()
    return new_deck


def check_four_of_a_kind(hand, letters, numbers, rnum, rlet):
    for i in numbers:
        if numbers.count(i) == 4:
            four = i
        elif numbers.count(i) == 1:
            card = i
    score = 105 + four + card / 100
    return score


def check_full_house(hand, letters, numbers, rnum, rlet):
    for i in numbers:
        if numbers.count(i) == 3:
            full = i
        elif numbers.count(i) == 2:
            p = i
    score = 90 + full + p / 100
    return score


def check_three_of_a_kind(hand, letters, numbers, rnum, rlet):
    cards = []
    for i in numbers:
        if numbers.count(i) == 3:
            three = i
        else:
            cards.append(i)
    score = 45 + three + max(cards) + min(cards) / 1000
    return score


def check_two_pair(hand, letters, numbers, rnum, rlet):
    pairs = []
    cards = []
    for i in numbers:
        if numbers.count(i) == 2:
            pairs.append(i)
        elif numbers.count(i) == 1:
            cards.append(i)
            cards = sorted(cards, reverse=True)
    score = 30 + max(pairs) + min(pairs) / 100 + cards[0] / 1000
    return score


def check_pair(hand, letters, numbers, rnum, rlet):
    pair = []
    cards = []
    for i in numbers:
        if numbers.count(i) == 2:
            pair.append(i)
        elif numbers.count(i) == 1:
            cards.append(i)
            cards = sorted(cards, reverse=True)
    score = 15 + pair[0] + cards[0] / 100 + cards[1] / 1000 + cards[2] / 10000
    return score


def score_hand(hand):
    letters = [hand[i][:1] for i in range(5)]
    numbers = [int(hand[i][1:]) for i in range(5)]
    rnum = [numbers.count(i) for i in numbers]
    rlet = [letters.count(i) for i in letters]
    dif = max(numbers) - min(numbers)
    handtype = ''
    score = 0
    if 5 in rlet:
        if numbers == [14, 13, 12, 11, 10]:
            handtype = 'royal_flush'
            score = 135

        elif dif == 4 and max(rnum) == 1:
            handtype = 'straight_flush'
            score = 120 + max(numbers)

        elif 4 in rnum:
            handtype = 'four of a kind'
            score = check_four_of_a_kind(hand, letters, numbers, rnum, rlet)

        elif sorted(rnum) == [2, 2, 3, 3, 3]:
            handtype = 'full house'
            score = check_full_house(hand, letters, numbers, rnum, rlet)

        elif 3 in rnum:
            handtype = 'three of a kind'
            score = check_three_of_a_kind(hand, letters, numbers, rnum, rlet)

        elif rnum.count(2) == 4:
            handtype = 'two pair'
            score = check_two_pair(hand, letters, numbers, rnum, rlet)

        elif rnum.count(2) == 2:
            handtype = 'pair'
            score = check_pair(hand, letters, numbers, rnum, rlet)

        else:
            handtype = 'flush'
            score = 75 + max(numbers) / 100

    elif 4 in rnum:
        handtype = 'four of a kind'
        score = check_four_of_a_kind(hand, letters, numbers, rnum, rlet)

    elif sorted(rnum) == [2, 2, 3, 3, 3]:
        handtype = 'full house'
        score = check_full_house(hand, letters, numbers, rnum, rlet)

    elif 3 in rnum:
        handtype = 'three of a kind'
        score = check_three_of_a_kind(hand, letters, numbers, rnum, rlet)

    elif rnum.count(2) == 4:
        handtype = 'two pair'
        score = check_two_pair(hand, letters, numbers, rnum, rlet)

    elif rnum.count(2) == 2:
        handtype = 'pair'
        score = check_pair(hand, letters, numbers, rnum, rlet)

    elif dif == 4:
        handtype = 'straight'
        score = 65 + max(numbers)


    else:
        handtype = 'high card'
        n = sorted(numbers, reverse=True)
        score = n[0] + n[1] / 100 + n[2] / 1000 + n[3] / 10000 + n[4] / 100000

    return score


class Games(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @action(detail=False, methods=['post'])
    def start_game(self, request):
        player_num = int(request.data['player_num'])
        player_num = 2
        deck = create_deck()
        discard_pile = DiscardPile.objects.create()
        dealt_cards = DealtCards.objects.create()
        new_game = Game.objects.create(deck=deck, discard_pile=discard_pile, dealt_cards=dealt_cards,
                                       small_bet=0)
        hand = Hand.objects.create()

        human_player = Player.objects.create(game=new_game, hand=hand, type='Human')
        for _ in range(2):
            random_card = deck.card_set.order_by('?').first()
            random_card.deck = None
            random_card.hand = hand
            random_card.save()
            hand.save()
        for _ in range(player_num - 1):
            hand = Hand.objects.create()
            cpu_player = Player.objects.create(game=new_game, hand=hand, type='CPU')
            for _ in range(2):
                random_card = deck.card_set.order_by('?').first()
                random_card.deck = None
                random_card.hand = hand
                random_card.save()
                hand.save()

        human_player.money_put = 50
        human_player.money -= 50
        cpu_player.money_put = 100
        cpu_player.money -= 100
        human_player.save()
        cpu_player.save()
        return Response({'id': new_game.id})

    @action(detail=True, methods=['post'])
    def continue_game(self, request, pk=None):
        last_game = self.get_object()
        last_player = last_game.player_set.get(type='Human')
        last_cpu = last_game.player_set.get(type='CPU')
        deck = create_deck()
        discard_pile = DiscardPile.objects.create()
        dealt_cards = DealtCards.objects.create()
        new_game = Game.objects.create(deck=deck, discard_pile=discard_pile, dealt_cards=dealt_cards,
                                       small_bet=0)
        hand = Hand.objects.create()

        human_player = Player.objects.create(game=new_game, hand=hand, type='Human')
        human_player.money = last_player.money
        human_player.save()
        for _ in range(2):
            random_card = deck.card_set.order_by('?').first()
            random_card.deck = None
            random_card.hand = hand
            random_card.save()
            hand.save()

        hand = Hand.objects.create()
        cpu_player = Player.objects.create(game=new_game, hand=hand, type='CPU')
        cpu_player.money = last_cpu.money
        cpu_player.save()
        for _ in range(2):
            random_card = deck.card_set.order_by('?').first()
            random_card.deck = None
            random_card.hand = hand
            random_card.save()
            hand.save()
        human_player.money_put = 50
        human_player.money -= 50
        cpu_player.money_put = 100
        cpu_player.money -= 100
        human_player.save()
        cpu_player.save()
        return Response({'id': new_game.id})

    @action(detail=True, methods=['post'])
    def advance_game(self, request, pk=None):
        """
        choice = 0 fold
        choice = 1 check
        choice = 2 raise
        game.state = 0 only player cards
        game.state = 1 3 cards dealt
        game.state = 2 4 cards dealt
        game.state = 3 5 cards dealt
        :param request:
        :param pk:
        :return:
        """
        game = self.get_object()
        human_player = game.player_set.get(type='Human')
        cpu_player = game.player_set.get(type='CPU')
        player_choice = int(request.data['check'])
        self.collect_data(human_player, cpu_player, player_choice)
        if player_choice == 1:
            self.even_bets(human_player, cpu_player)
        if player_choice == 2:
            self.bet(human_player, cpu_player)
        cpu_choice = self.cpu_prediction(cpu_player, human_player)
        if cpu_choice == 1:
            self.even_bets(cpu_player, human_player)
        if cpu_choice == 2 and not (cpu_player.previous_choice == 2 and player_choice == 1) and player_choice != 0:
            self.bet(cpu_player, human_player)
            human_player.previous_choice = player_choice
            human_player.save()
            cpu_player.previous_choice = cpu_choice
            cpu_player.save()
            return Response({'result': 'ongoing'})
        if (player_choice == 1 and cpu_choice == 1) or (player_choice == 2 and cpu_choice == 1) or (
                cpu_player.previous_choice == 2 and player_choice == 1):
            game.money_pool += (human_player.money_put + cpu_player.money_put)
            game.save()
            human_player.money_put = 0
            human_player.save()
            cpu_player.money_put = 0
            cpu_player.save()
            if game.state == 0:
                random_card = game.deck.card_set.order_by('?').first()
                random_card.deck = None
                random_card.discard_pile = game.discard_pile
                random_card.save()
                for _ in range(3):
                    random_card = game.deck.card_set.order_by('?').first()
                    random_card.deck = None
                    random_card.dealt_cards = game.dealt_cards
                    random_card.save()
            if game.state == 1:
                random_card = game.deck.card_set.order_by('?').first()
                random_card.deck = None
                random_card.discard_pile = game.discard_pile
                random_card.save()
                random_card = game.deck.card_set.order_by('?').first()
                random_card.deck = None
                random_card.dealt_cards = game.dealt_cards
                random_card.save()
            if game.state == 2:
                random_card = game.deck.card_set.order_by('?').first()
                random_card.deck = None
                random_card.discard_pile = game.discard_pile
                random_card.save()
                random_card = game.deck.card_set.order_by('?').first()
                random_card.deck = None
                random_card.dealt_cards = game.dealt_cards
                random_card.save()
            if game.state == 3:
                human_score = 0
                cpu_score = 0
                for player in game.player_set.all():
                    player_numbers = [card.value for card in player.hand.card_set.all()]
                    player_letters = [card.suit for card in player.hand.card_set.all()]
                    drawn_numbers = [card.value for card in game.dealt_cards.card_set.all()]
                    drawn_letters = [card.suit for card in game.dealt_cards.card_set.all()]
                    combined_numbers = player_numbers + drawn_numbers
                    combined_suits = player_letters + drawn_letters
                    prepared_deck = []
                    scores = []
                    for number, suit in zip(combined_numbers, combined_suits):
                        prepared_deck.append(suit + str(number))
                    for hand in combinations(prepared_deck, 5):
                        scores.append(score_hand(hand))
                    player.score = max(scores)
                    player.save()
                    if player.type == 'Human':
                        human_score = max(scores)
                    else:
                        cpu_score = max(scores)
                if human_score >= cpu_score:
                    self.payout_winnings(human_player, cpu_player)
                    return Response({'result': 'won'})
                else:
                    self.payout_winnings(cpu_player, human_player)
                    return Response({'result': 'lost'})

            game.state += 1
            game.save()
            human_player.previous_choice = 1
            human_player.save()
            cpu_player.previous_choice = 1
            cpu_player.save()
            return Response({'result': 'ongoing'})
        elif player_choice == 0 and (cpu_choice == 1 or cpu_choice == 2):
            self.payout_winnings(cpu_player, human_player)
            return Response({'result': 'lost'})
        elif cpu_choice == 0:
            self.payout_winnings(human_player, cpu_player)
            return Response({'result': 'won'})
        else:
            human_player.previous_choice = player_choice
            human_player.save()
            cpu_player.previous_choice = cpu_choice
            cpu_player.save()
            return Response({'result': 'ongoing'})

    def payout_winnings(self, winner, loser):
        game = self.get_object()
        winner.money = winner.money + winner.money_put + loser.money_put + game.money_pool
        print(f'{winner.money_put} {loser.money_put} {game.money_pool}')
        winner.money_put = 0
        winner.save()
        loser.money_put = 0
        loser.save()
        game.money_pool = 0
        game.save()

    def bet(self, betting_player, other_player):
        if betting_player.money_put < other_player.money_put:
            difference = other_player.money_put - betting_player.money_put
            betting_player.money_put += (difference + 100)
            betting_player.money -= (difference + 100)
        else:
            betting_player.money_put += 100
            betting_player.money -= 100
        betting_player.save()

    def even_bets(self, ev_player, other_player):
        if ev_player.money_put < other_player.money_put:
            difference = other_player.money_put - ev_player.money_put
            ev_player.money_put += difference
            ev_player.money -= difference
            ev_player.save()

    def collect_data(self, human, cpu, choice):
        game = self.get_object()
        suit_dict = {'h': 1, 'c': 2, 's': 3, 'd': 4}
        learning_data = LearningData.objects.create(decision=choice,
                                                    game_state=game.state,
                                                    total_money=human.money / 100,
                                                    money_put=human.money_put / 100,
                                                    opp_money=cpu.money / 100,
                                                    opp_money_put=cpu.money_put / 100,
                                                    money_pool=game.money_pool / 100)
        hand_cards = list(Card.objects.all().filter(hand_id=human.hand.id))
        learning_data.hand_1_val = hand_cards[0].value
        learning_data.save()
        learning_data.hand_1_suit = suit_dict[hand_cards[0].suit]
        learning_data.save()
        learning_data.hand_2_val = hand_cards[1].value
        learning_data.save()
        learning_data.hand_2_suit = suit_dict[hand_cards[1].suit]
        learning_data.save()
        table_cards = game.dealt_cards.get_cards().all()

        for num, card in enumerate(table_cards, 1):
            exec(f'learning_data.card_{num}_val = {card.value}')
            learning_data.save()
            exec(f'learning_data.card_{num}_suit = {suit_dict[card.suit]}')
            learning_data.save()

        if LearningData.objects.all().count() % 50 == 0:
            fit_models.delay()

    def cpu_prediction(self, cpu_player, human_player):
        game = self.get_object()
        suit_dict = {'h': 1, 'c': 2, 's': 3, 'd': 4}
        table_cards = game.dealt_cards.get_cards().all()
        random_tree = LearningModels.objects.filter(type='RandomForestClassifier')
        bayes = LearningModels.objects.filter(type='GaussianNB')
        decision_tree = LearningModels.objects.filter(type='DecisionTreeClassifier')
        if (not random_tree) or (not bayes) or (not decision_tree):
            return random.randint(0, 2)
        print('going to predictions...')
        random_tree = random_tree.latest('id')
        bayes = bayes.latest('id')
        decision_tree = decision_tree.latest('id')
        models_list = [random_tree, bayes, decision_tree]
        models_list.sort(reverse=True, key=lambda x: x.accuracy)
        best_model = models_list[0]
        classifier = pickle.loads(best_model.learning_model)
        hand_cards = list(Card.objects.all().filter(hand_id=cpu_player.hand.id))
        card_values = [0, 0, 0, 0, 0]
        card_suits = [0, 0, 0, 0, 0]
        for num, card in enumerate(table_cards):
            card_values[num] = card.value
            card_suits[num] = suit_dict[card.suit]
        predicting_data = [[game.state, hand_cards[0].value, suit_dict[hand_cards[0].suit], hand_cards[1].value,
                            suit_dict[hand_cards[1].suit],
                            card_values[0], card_suits[0], card_values[1], card_suits[1], card_values[2], card_suits[2],
                            card_values[3], card_suits[3], card_values[4], card_suits[4], cpu_player.money / 100,
                            cpu_player.money_put / 100, human_player.money / 100, human_player.money_put / 100,
                            game.money_pool / 100]]
        print(predicting_data)
        print(classifier.predict(predicting_data))
        return classifier.predict(predicting_data)[0]
