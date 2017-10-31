import json

from ynServer import DialogueActTagger
import spacy
import numpy as np
from scipy.stats import stats
import datetime

class DefaultSimplifier:

    def transform(self, object):
        raise NotImplementedError()


class RatingSimplifier(DefaultSimplifier):

    def transform(self, conversation_date_rating):
        conversation = conversation_date_rating[0]
        date = conversation_date_rating[1]
        rating = conversation_date_rating[2]
        rating = rating.replace("*","")
        return float(rating)


class DateSimplifier(DefaultSimplifier):
    def transform(self, conversation_date_rating):
        conversation = conversation_date_rating[0]
        date = conversation_date_rating[1]
        rating = conversation_date_rating[2]
        return date

class ConversationSimplifier(DefaultSimplifier):
    def transform(self, conversation_date_rating):
        conversation = conversation_date_rating[0]
        date = conversation_date_rating[1]
        rating = conversation_date_rating[2]
        return conversation

class SentimentSimplifier(DefaultSimplifier):

    @staticmethod
    def compute_sentiment_vector(sentiment_dict,total):
        if np.sum(sentiment_dict.values()) != total:
            raise Exception("Sum of the values is different from total")
        sent_to_index = {"Negative": 0, "Neutral": 1, "Positive": 2}
        final_vector = np.zeros(3)
        if total == 0:
            return None
        for key in sentiment_dict.keys():
            index =sent_to_index.get(key)
            percentage = float(sentiment_dict.get(key))/float(total)
            np.put(final_vector, [index], [percentage], mode='raise')
        return final_vector

    def compute_percentage_per_sentiment(self, sentiments_list):
        sentiment_dict = {"Neutral": 0, "Negative": 0, "Positive": 0}
        total = 0
        for sentiment in sentiments_list:
            sentiment_dict[sentiment] += 1
            total += 1
        conversation_vector = SentimentSimplifier.compute_sentiment_vector(sentiment_dict, total)
        return conversation_vector

    def transform(self, object):
        raise NotImplementedError()

class SentimentSimplifierWithYN(SentimentSimplifier):

    def transform(self, conversation_date_rating):
        conversation = conversation_date_rating[0]
        sentiments = []

        for turn in conversation:
            run_info = turn.run_info
            if run_info is None:
                continue
            run_info = json.loads(run_info)
            slu_result = run_info.get("slu_result")
            utterances = slu_result.get("utterances")
            for utterance in utterances:
                sentiment = utterance.get("intent").get("sentiment").get("tag")
                sentiments.append(sentiment)
        conversation = self.compute_percentage_per_sentiment(sentiments)

        return conversation


class SentimentSimplifierWithoutYN(SentimentSimplifier):

    def __init__(self):
        self.yn_classifier = DialogueActTagger(spacy_inst=spacy.load("en"))

    def transform(self, conversation_date_rating):
        conversation = conversation_date_rating[0]
        sentiments = []
        for turn in conversation:
            run_info = turn.run_info
            if run_info is None:
                continue

            run_info = json.loads(run_info)
            slu_result = run_info.get("slu_result")
            utterances = slu_result.get("utterances")
            for utterance in utterances:
                sentiment = utterance.get("intent").get("sentiment").get("tag")
                classified = self.yn_classifier.classifyYN(utterance.get("content"))
                if classified == "YN":
                    sentiment = "Neutral"
                sentiments.append(sentiment)
        conversation = self.compute_percentage_per_sentiment(sentiments)

        return conversation
