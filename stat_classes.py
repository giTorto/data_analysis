import csv

import datetime

import numpy as np
from scipy.stats import stats


class Experiment:

    def __init__(self, conditions, grouper, simplifier, stat_function, db_manager):
        self.conditions = conditions
        self.grouper = grouper
        self.simplifier = simplifier
        self.db_manager = db_manager
        self.rating_dict = Experiment.load_ratings()
        self.stat_function = stat_function

    @staticmethod
    def print_advancement_percentage(current_index, total):
        if current_index % 1000 == 0:
            print float(current_index) / float(len(total)) * 100.0


    @staticmethod
    def load_ratings():
        ratings_dict = {}
        with open("../ratings/ratings.csv", 'r') as in_file:
            csv_reader = csv.reader(in_file, delimiter=",")
            for line in csv_reader:
                ratings_dict[line[0]] = line[2]
        return ratings_dict

    def apply_filters(self, conversation):
        verified = all([map(condition,[conversation])[0] for condition in self.conditions])
        return verified

    def get_filtered_conversations(self):

        for i, conversation_id in enumerate(self.rating_dict.keys()):
            Experiment.print_advancement_percentage(i, self.rating_dict.keys())
            conversation_and_date = self.db_manager.get_all_conversation_info(conversation_id)
            if conversation_and_date[0] is None:
                continue
            conversation_and_date = conversation_and_date[0], conversation_and_date[1], self.rating_dict.get(conversation_id)
            if conversation_and_date[2] is None:
                continue
            conditions_are_verified = self.apply_filters(conversation_and_date)
            if not conditions_are_verified:
                continue
            yield conversation_and_date

    def run(self):
        result = {}
        for conversation, date, rating in self.get_filtered_conversations():
            group = self.grouper.get_group(conversation, discriminant_element=date)
            representation = self.simplifier.transform([conversation,date,rating])
            if group not in result:
                result[group] = []
            result[group].append(representation)
        self.stat_function(result)


class SentimentExperiment(Experiment):
    def run(self):
        result = {}
        number_of_conversations = 0
        for conversation, date, rating in self.get_filtered_conversations():
            number_of_conversations += 1
            group = self.grouper.get_group(conversation, discriminant_element=rating)
            representation = self.simplifier.transform([conversation,date,rating])
            if representation is None:
                continue
            if group not in result:
                result[group] = []
            result[group].append(representation)
        print "Total conversations found ", number_of_conversations
        self.stat_function(result)


class UserExperiment(Experiment):

    def get_user(self, conversation):
        user_id = conversation[0].user_id
        return user_id

    def run(self):
        result = {}
        for conversation, date, rating in self.get_filtered_conversations():
            user_id = self.get_user(conversation)
            group = self.grouper.get_group(conversation, discriminant_element=user_id)
            representation = self.simplifier.transform([conversation,date,rating])
            if representation is None:
                continue
            if group not in result:
                result[group] = []
            result[group].append(representation)
        self.stat_function(result)


class PathExperiment(Experiment):

    def get_user(self, conversation):
        user_id = conversation[0].user_id
        return user_id

    def run(self):
        result = {}
        for conversation, date, rating in self.get_filtered_conversations():
            user_id = self.get_user(conversation)
            group = self.grouper.get_group(conversation, discriminant_element=conversation)
            representation = self.simplifier.transform([conversation,date,rating])
            if representation is None:
                continue
            if group not in result:
                result[group] = []
            result[group].append(representation)
        self.stat_function(result)

class DefaultStatFunction:

    def perform_stat(self, result_dict):
        raise NotImplementedError()


def is_date_after(date, threshold_date):
    if threshold_date is None:
        threshold_date = datetime.date(2017, 07, 01)
    return date >= threshold_date


def is_date_before(date, threshold_date):
    if threshold_date is None:
        threshold_date = datetime.date(2017, 7, 27)
    return date <= threshold_date


def is_date_strict_before(date, threshold_date):
    if threshold_date is None:
        threshold_date = datetime.date(2017, 7, 27)
    return date < threshold_date


def is_date_before_07_27(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 7, 27))

def is_date_before_07_26(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 7, 26))

def is_date_after_07_15(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 7, 15))

def is_date_after_07_14(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 7, 14))

def is_date_before_07_18(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 7, 18))

def is_date_before_08_15(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 8, 15))


def is_date_before_08_4(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_strict_before(date, datetime.date(2017, 8, 4))


def is_date_after_07_1(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 7, 1))


def is_date_after_07_21(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 7, 21))

def is_date_after_07_22(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 7, 22))

def is_date_after_07_27(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 7, 27))

def is_date_after_07_28(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 7, 28))

def is_date_after_08_07(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 8, 7))

def is_date_after_08_01(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 8, 1))

def is_date_after_08_02(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 8, 2))

def is_date_after_08_03(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_after(date, datetime.date(2017, 8, 3))

def is_date_before_08_9(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 8, 9))

def is_date_before_08_2(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 8, 2))

def is_date_before_08_1(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 8, 1))

def is_date_before_08_8(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 8, 8))

def is_date_before_08_7(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 8, 7))

def is_date_before_08_6(conversation_date_rating):
    date = conversation_date_rating[1]
    return is_date_before(date, datetime.date(2017, 8, 6))

def t_test_classes(result):
    keys = result.keys()
    if len(keys) != 2:
        raise RuntimeError("To perform t-test just 2 classes are needed, found ", len(keys))
    key_1 = keys[0]
    key_2 = keys[1]
    print key_1, " ", len(result.get(key_1)), " ", key_2," ", len(result.get(key_2))
    print key_1, " mean ", np.mean(result.get(key_1))," ",key_2 , " ", np.mean(result.get(key_2))
    print stats.ttest_ind(result.get(key_1), result.get(key_2), equal_var=False)


def just_take_one_column(element_list):
    final_list = [x[0] for x in element_list]
    return final_list


def t_test_classes_general(result):
    keys = result.keys()
    if len(keys) != 2:
        raise RuntimeError("To perform t-test just 2 classes are needed, found ", len(keys))
    for key in keys:
        print key, " ", len(result.get(key)), " ", np.mean(result.get(key),axis=0)

    key_1 = keys[0]
    key_2 = keys[1]
    print stats.ttest_ind(result.get(key_1),result.get(key_2),
                          equal_var=False)


def t_test_both_none_quiz_path(result):
    keys = result.keys()
    for key in keys:
        print key, " ", len(result.get(key)), " ", np.mean(result.get(key),axis=0)

    key_1 = keys[0]
    key_2 = keys[1]
    key_3 = keys[2]
    key_4 = keys[3]
    print "t_test_between ", key_1, " ", key_2, "",\
        stats.ttest_ind(result.get(key_1), result.get(key_2),
                        equal_var=False)
    print "t_test_between ", key_2, " ", key_3, "", \
            stats.ttest_ind(result.get(key_2), result.get(key_3),
                            equal_var=False)
    print "t_test_between ", key_3, " ", key_4, "", \
        stats.ttest_ind(result.get(key_3), result.get(key_4),
                        equal_var=False)
    print "t_test_between ", key_1, " ", key_3, "", \
        stats.ttest_ind(result.get(key_1), result.get(key_3),
                        equal_var=False)
    print "t_test_between ", key_1, " ", key_4, "", \
        stats.ttest_ind(result.get(key_1), result.get(key_4),
                        equal_var=False)
    print "t_test_between ", key_2, " ", key_4, "", \
        stats.ttest_ind(result.get(key_2), result.get(key_4),
                        equal_var=False)

def count_more_than_2(number):
    return number>2


def average_count(resulting_dictionary):
    conversations_per_day = []
    for day in resulting_dictionary.keys():
        ratings = resulting_dictionary.get(day)
        conversations_per_day.append(len(ratings))

    print "number of days", len(conversations_per_day)
    print "average of interactions ", np.mean(conversations_per_day), np.var(conversations_per_day)



def average_returning_customers(result_dict):
    users = result_dict.keys()
    print "number of users ", len(users)
    print "number of interactions ", np.sum([len(x) for x in result_dict.values()])
    interactions = [len(x) for x in result_dict.values()]
    print "average of interactions ", np.mean(interactions), np.var(interactions)
    print "maximum number of interactions ", max(interactions)
    print "minimum number of interactions ", min(interactions)
    print "number of returning customers at least 3 times", len(filter(count_more_than_2, interactions))