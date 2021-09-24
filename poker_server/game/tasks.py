import pickle

import numpy as np
from celery import shared_task
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

from game.models import LearningData, LearningModels
import pathlib

@shared_task()
def update_spreadsheets():
    LearningData.push_to_sheet()


@shared_task()
def fit_models():
    learning_raw = LearningData.objects.all()
    data_amount = len(learning_raw)
    learning_target = learning_raw.values_list('decision', flat=True)
    learning_data = learning_raw.values_list('game_state', 'hand_1_val', 'hand_1_suit', 'hand_2_val', 'hand_2_suit',
                                             'card_1_val', 'card_1_suit', 'card_2_val', 'card_2_suit', 'card_3_val',
                                             'card_3_suit', 'card_4_val', 'card_4_suit', 'card_5_val', 'card_5_suit',
                                             'total_money', 'money_put', 'opp_money', 'opp_money_put', 'money_pool')
    learning_target = list(learning_target)
    learning_data = list(learning_data)
    data_train, data_test, target_train, target_test = train_test_split(learning_data, learning_target)
    random_forest = RandomForestClassifier()
    naive_bayes = GaussianNB()
    decision_tree = DecisionTreeClassifier()
    random_forest.fit(data_train, target_train)
    naive_bayes.fit(data_train, target_train)
    decision_tree.fit(data_train, target_train)
    random_forest_score = random_forest.score(data_test, target_test)
    naive_bayes_score = naive_bayes.score(data_test, target_test)
    decision_tree_score = decision_tree.score(data_test, target_test)
    binarized_classifier = pickle.dumps(random_forest)
    LearningModels.objects.create(type='RandomForestClassifier', learning_model=binarized_classifier,
                                  data_amount=data_amount, accuracy=random_forest_score)
    binarized_classifier = pickle.dumps(naive_bayes)
    LearningModels.objects.create(type='GaussianNB', learning_model=binarized_classifier,
                                  data_amount=data_amount, accuracy=naive_bayes_score)
    binarized_classifier = pickle.dumps(decision_tree)
    LearningModels.objects.create(type='DecisionTreeClassifier', learning_model=binarized_classifier,
                                  data_amount=data_amount, accuracy=decision_tree_score)
