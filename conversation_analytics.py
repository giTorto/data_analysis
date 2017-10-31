import csv
import subprocess
import csv
from optparse import OptionParser
import os
import sys
from db_manager import DBManager
import datetime
from scipy import stats
import numpy as np
from stat_classes import DefaultStatFunction, Experiment,\
    is_date_after_07_15, is_date_before_07_27, t_test_classes, is_date_after_07_1, is_date_before_08_15, \
    SentimentExperiment, is_date_before_08_4, t_test_classes_general, UserExperiment, average_returning_customers, \
    is_date_after_07_21, is_date_before_08_9, t_test_both_none_quiz_path, PathExperiment, is_date_after_08_07, \
    is_date_after_08_01, is_date_before_08_2, is_date_after_07_27, is_date_before_08_8, is_date_after_08_02, \
    is_date_after_08_03, is_date_after_07_28, is_date_before_08_7, is_date_after_07_22, is_date_before_08_1, \
    is_date_before_07_26, is_date_before_08_6, average_count, is_date_after_07_14, is_date_before_07_18
from groupers import DefaultGrouper, DateGrouper, RatingGrouperWith3, UserGrouper, PathGrouper, DateGrouperPathVsLast, \
    DateGrouperBeforeVsQuiz, DateGrouperQuizPeriodPathPeriod, DayGrouper
from simplifiers import SentimentSimplifier,SentimentSimplifierWithoutYN, SentimentSimplifierWithYN,DefaultSimplifier, DateSimplifier, RatingSimplifier, \
    ConversationSimplifier


def copy_last_ratings_here():
    if not os.path.exists("ratings"):
        os.makedirs("ratings")
    subprocess.call("aws s3 cp s3://alexaprize/317926991407/ratings.csv ../ratings/ratings.csv", shell=True)

def transform_discriminant(discriminant, transformation="before_after"):
    if transformation == 'before_after':
        date = datetime.date(2017, 07, 22)

        if discriminant < date:
            discriminant = 'before'
        else:
            discriminant = 'after'

    return discriminant


def group_by(elements, discriminative_index, index_to_take):
    grouped_elements = {}
    for element in elements:
        discriminant = element[discriminative_index]
        discriminant = transform_discriminant(discriminant)
        if discriminant not in grouped_elements:
            grouped_elements[discriminant] = []

        grouped_elements[discriminant].append(element[index_to_take])
    return grouped_elements


def is_date_after(date, threshold_date):
    if threshold_date is None:
        threshold_date = datetime.date(2017, 07, 01)
    return date >= threshold_date


def print_advancement_percentage(current_index, total):
    if current_index % 1000 == 0:
        print float(current_index) / float(len(total)) * 100.0

def load_ratings():
    ratings_dict = {}
    with open("ratings/ratings.csv", 'r') as in_file:
        csv_reader = csv.reader(in_file, delimiter=",")
        for line in csv_reader:
            ratings_dict[line[0]] = line[2]
    return ratings_dict

def stats_by_date(db_manager):
    rating_dict = load_ratings()
    rated_conversation_list = []
    for i, conversation_id in enumerate(rating_dict.keys()):
        print_advancement_percentage(i, rating_dict.keys())
        results = db_manager.get_conversation_date(conversation_id)
        if len(results) < 1:
            continue
        else:
            date_found = results[0][0]
        if is_date_after(date_found, datetime.date(2017, 07, 15)):
            rating = float(rating_dict.get(conversation_id).replace("*", ""))
            rated_conversation_list.append([date_found, rating])
    result = group_by(rated_conversation_list, discriminative_index=0, index_to_take=1)

    print "before ", len(result.get('before')), "after ", len(result.get('after'))
    print "before mean ", np.mean(result.get('before')), " after ", np.mean(result.get('after'))
    print stats.ttest_ind(result.get('before'), result.get('after'), equal_var=False)

def main(argv=None):
    op = OptionParser()
    op.add_option("-e", "--experiment", type=str, dest="experiment_name", help="The name of the experiment to perform",
                  default="prompting_exp")
    (opts, args) = op.parse_args()
    copy_last_ratings_here()

    db_manager = DBManager()
    try:
        #stats_by_date(db_manager)
        experiment = give_me_experiments(opts.experiment_name, db_manager)
        experiment.run()
        # experiment_sentiment = Experiment()

    finally:
        db_manager.close()


def give_me_experiments(index, db_manager):
    if index == "prompting_exp": #1
        conditions = [is_date_after_07_15, is_date_before_07_26]
        grouper = DateGrouper()
        rating_simplifier = RatingSimplifier()
        experiment_prompting = Experiment(conditions, grouper, rating_simplifier, t_test_classes, db_manager)
        """
        after   1333   before   3216
        after  mean  2.75408852213   before   2.44115360697
        Ttest_indResult(statistic=6.5495869598960601, pvalue=7.0696442090782814e-11)
        --- moved window of 1-day (taken)
        after   1332   before   3008
        after  mean  2.69797297297   before   2.43243018617
        Ttest_indResult(statistic=5.5620490707569807, pvalue=2.9584262604906071e-08)
        """
        return experiment_prompting
    elif index == "sentiment_exp": #2
        conditions = [is_date_after_07_1, is_date_before_08_4]
        grouper = RatingGrouperWith3()
        rating_simplifier = SentimentSimplifierWithYN()
        experiment_sentiment = SentimentExperiment(conditions, grouper, rating_simplifier, t_test_classes_general, db_manager)
        return experiment_sentiment
    elif index == "sentiment_no_yn":
        conditions = [is_date_after_07_1, is_date_before_08_15]
        grouper = RatingGrouperWith3()
        rating_simplifier = SentimentSimplifierWithoutYN()
        experiment_sentiment = SentimentExperiment(conditions, grouper, rating_simplifier, t_test_classes_general, db_manager)
        return experiment_sentiment
    elif index == "returning_customers":
        conditions = [is_date_after_07_21, is_date_before_08_15]
        grouper = UserGrouper()
        conversation_simplifier = ConversationSimplifier()
        experiment_users = UserExperiment(conditions, grouper, conversation_simplifier, average_returning_customers, db_manager)
        return experiment_users
    elif index == "path_not_quiz":
        conditions = [is_date_after_07_21, is_date_before_08_9]
        grouper = PathGrouper()
        conversation_simplifier = RatingSimplifier()
        experiment_path = PathExperiment(conditions, grouper, conversation_simplifier, t_test_both_none_quiz_path, db_manager)
        """
        path   261   3.03831417625
        none   2738   2.7626734843
        both   182   3.65412087912
        quiz   495   3.10735675152
        t_test_between  path   none  Ttest_indResult(statistic=3.1598585858625214, pvalue=0.0017253008837173726)
        t_test_between  none   both  Ttest_indResult(statistic=-9.0169514087694242, pvalue=1.0438411030445049e-16)
        t_test_between  both   quiz  Ttest_indResult(statistic=4.8025350735555543, pvalue=2.3146694907300142e-06)
        t_test_between  path   both  Ttest_indResult(statistic=-4.9153189397531785, pvalue=1.2962365563055481e-06)
        t_test_between  path   quiz  Ttest_indResult(statistic=-0.66445372749238218, pvalue=0.50667448280444427)
        t_test_between  none   quiz  Ttest_indResult(statistic=-4.9365775839639516, pvalue=9.8972763152263774e-07)
        """
        return experiment_path
    elif index == "path_vs_last_week":
        conditions = [is_date_after_08_02, is_date_before_08_15] #extremes included
        grouper = DateGrouperPathVsLast()
        rating_simplifier = RatingSimplifier()
        experiment_prompting = Experiment(conditions, grouper, rating_simplifier, t_test_classes, db_manager)
        """
        after   981   before   972
        after  mean  3.20354387816   before   3.07566872428
        Ttest_indResult(statistic=1.9312205490150192, pvalue=0.05360088653139021)
                --- moved window of 1-day
        after   1262   before   1162 (taken)
        after  mean  3.17684353762   before   3.07405335628
        Ttest_indResult(statistic=1.7227801859681033, pvalue=0.085057732699887034)
                        -- or moving the split from 8 to 7
        after   1273   before   982
        after  mean  3.20477340493   before   3.0132892057
        Ttest_indResult(statistic=3.0645844471971815, pvalue=0.0022077169617001698)

        """
        return experiment_prompting
    elif index == "prompt_vs_quiz":
        conditions = [is_date_after_07_21, is_date_before_08_1] #extremes included
        grouper = DateGrouperBeforeVsQuiz()
        rating_simplifier = RatingSimplifier()
        experiment_prompting = Experiment(conditions, grouper, rating_simplifier, t_test_classes, db_manager)
        """
        after   1135   before   1333
        after  mean  2.88867100617   before   2.75408852213
        Ttest_indResult(statistic=2.215731957701971, pvalue=0.026803545607454956)
                --- moved window of 1-day (taken)
        after   1154   before   1332
        after  mean  2.86624054766   before   2.69797297297
        Ttest_indResult(statistic=2.7969225793928763, pvalue=0.0052000747514132995)

        """
        return experiment_prompting
    elif index == "quiz_period_vs_path_period":
        conditions = [is_date_after_07_27, is_date_before_08_8] #extremes included
        grouper = DateGrouperQuizPeriodPathPeriod()
        rating_simplifier = RatingSimplifier()
        experiment_prompting = Experiment(conditions, grouper, rating_simplifier, t_test_classes, db_manager)
        """
        after   972   before   1135
        after  mean  3.07566872428   before   2.88867100617
        Ttest_indResult(statistic=2.8487170474650969, pvalue=0.0044331253314975165)
                --- moved window of 1-day (taken)
        after   1162   before   1154
        after  mean  3.07405335628   before   2.86624054766
        Ttest_indResult(statistic=3.3254019242781525, pvalue=0.00089670274407656326)
                --- or moving from 7 to 6
        after   982   before   1154
        after  mean  3.0132892057   before   2.86624054766
        Ttest_indResult(statistic=2.2567541754723086, pvalue=0.024126325255506897)
        """
        return experiment_prompting
    elif index == "day_average":
        conditions = [is_date_after_07_1, is_date_before_08_15] #extremes included
        grouper = DayGrouper()
        rating_simplifier = RatingSimplifier()
        experiment_prompting = Experiment(conditions, grouper, rating_simplifier, average_count, db_manager)
        """
        number of days 45
        average of interactions  223.444444444 27117.9802469
        """
        return experiment_prompting
    elif index == "day_average_peak":
        conditions = [is_date_after_07_14, is_date_before_07_18] #extremes included
        grouper = DayGrouper()
        rating_simplifier = RatingSimplifier()
        experiment_prompting = Experiment(conditions, grouper, rating_simplifier, average_count, db_manager)
        """
        number of days 5
        average of interactions  625.2 32807.76
        """
        return experiment_prompting


if __name__ == "__main__":
    sys.exit(main())
    """
    experiments and dates:
    - changed opening prompt 21/07/2017
    - added quizzes  27/07/2017
    - major bug fixing 28/07/2017 e 31/07/2017
    - changed opening prompt 1/08/2017
    - added paths 2/08/2017
    - change of unsupported request management - 7/08/2017
    """
    """
    main evaluation periods:(extremes included)
    - 15/07 - 20/07: baseline (mean 2.44)
    - 21/07 - 26/07: baseline + directive prompt (mean 2.75)
    - 27/07 - 01/08: baseline + directive prompt + quizzes ( mean 2.89)
    - 02/08 - 07/08: baseline + directive prompt + quizzes + path (mean 3.07)
    - 08/08 - 15/08: baseline + directive prompt + quizzes + path + directive unsupported prompt (mean 3.20)
    """
#2017-04-09T22:09:02.654-07:00



"""
  ----- Sentiment:
INCLUDING rating 3 in bucket 3-5
INCLUDING Yes/No answers
AGGREGATE:
means:  16.09   21.66
counts:         4198    3385
Mean difference: 5.57
Statistically RELEVANT
Statistic: -7.99
pValue: 0.00 (1.5543122344752192e-15)
EXCLUDING rating 3 from the bucket 3-5
INCLUDING Yes/No answers
AGGREGATE:
means:  16.09   21.92
counts:         4198    1989
Mean difference: 5.84
Statistically RELEVANT
Statistic: -6.97
pValue: 0.00 (3.724132113802625e-12)

INCLUDING rating 3 in bucket 3-5
EXCLUDING Yes/No answers
AGGREGATE:
means:  12.36   16.49
counts:         4188    3379
Mean difference: 4.13
Statistically RELEVANT
Statistic: -6.22
pValue: 0.00 (5.280276216268476e-10)
EXCLUDING rating 3 from the bucket 3-5
EXCLUDING Yes/No answers
AGGREGATE:
means:  12.36   16.22
counts:         4188    1984
Mean difference: 3.86
Statistically RELEVANT
Statistic: -4.89
pValue: 0.00 (1.0338537899112765e-6)
"""


"""
 -- turn length
Means:  1-2: 4.05       3-5:3.73
Mean difference: 0.32 (+1-2)
Statistically RELEVANT
Statistic: 6.55
pValue: 0.00 (6.064387744571606e-11)
INCLUDING rating 3 in bucket 3-5
EXCLUDING Yes/No answers
Means:  1-2: 4.37       3-5:4.10
Mean difference: 0.27 (+1-2)
Statistically RELEVANT
Statistic: 5.31
pValue: 0.00 (1.1331270996422761e-7)
EXCLUDING rating 3 from the bucket 3-5
EXCLUDING Yes/No answers
Means:  1-2: 4.37       3-5:4.06
Mean difference: 0.30 (+1-2)
Statistically RELEVANT
Statistic: 5.02
pValue: 0.00 (5.199327547193602e-7)
EXCLUDING rating 3 from the bucket 3-5
INCLUDING Yes/No answers
Means:  1-2: 4.05       3-5:3.70
Mean difference: 0.35 (+1-2)
Statistically RELEVANT
Statistic: 6.01
pValue: 0.00 (1.965916078335426e-9)
INCLUDING rating 3 in bucket 3-5
INCLUDING Yes/No answers
Means:  1-2: 4.05       3-5:3.73
Mean difference: 0.32 (+1-2)
Statistically RELEVANT
Statistic: 6.55
pValue: 0.00 (6.064387744571606e-11)
"""

