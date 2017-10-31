import datetime
import json


class DefaultGrouper:
    def transform_discriminant(self, discriminant, transformation):
        raise NotImplementedError()
    def get_group(self, element, discriminant_element, transformation):
        raise NotImplementedError()

class DateGrouper(DefaultGrouper):

    def transform_discriminant(self, discriminant, transformation="before_after"):
        if transformation == 'before_after':
            date = datetime.date(2017, 07, 21)

            if discriminant < date:
                discriminant = 'before'
            else:
                discriminant = 'after'

        return discriminant

    def get_group(self, element, discriminant_element,transformation= 'before_after' ):
        discriminant = discriminant_element
        discriminant = self.transform_discriminant(discriminant, transformation)
        return discriminant


class DateGrouperPathVsLast(DefaultGrouper):

    def transform_discriminant(self, discriminant, transformation="before_after"):
        if transformation == 'before_after':
            date = datetime.date(2017, 8, 8)

            if discriminant < date:
                discriminant = 'before'
            else:
                discriminant = 'after'

        return discriminant

    def get_group(self, element, discriminant_element,transformation= 'before_after' ):
        discriminant = discriminant_element
        discriminant = self.transform_discriminant(discriminant, transformation)
        return discriminant

class DateGrouperBeforeVsQuiz(DefaultGrouper):

    def transform_discriminant(self, discriminant, transformation="before_after"):
        if transformation == 'before_after':
            date = datetime.date(2017, 7, 27)

            if discriminant < date:
                discriminant = 'before'
            else:
                discriminant = 'after'

        return discriminant

    def get_group(self, element, discriminant_element,transformation= 'before_after' ):
        discriminant = discriminant_element
        discriminant = self.transform_discriminant(discriminant, transformation)
        return discriminant


class DayGrouper(DefaultGrouper):

    def transform_discriminant(self, discriminant, transformation="before_after"):
        return discriminant

    def get_group(self, element, discriminant_element,transformation= 'before_after' ):
        discriminant = discriminant_element
        discriminant = self.transform_discriminant(discriminant, transformation)
        return discriminant


class DateGrouperQuizPeriodPathPeriod(DefaultGrouper):

    def transform_discriminant(self, discriminant, transformation="before_after"):
        if transformation == 'before_after':
            date = datetime.date(2017, 8, 2)

            if discriminant < date:
                discriminant = 'before'
            else:
                discriminant = 'after'

        return discriminant

    def get_group(self, element, discriminant_element,transformation= 'before_after' ):
        discriminant = discriminant_element
        discriminant = self.transform_discriminant(discriminant, transformation)
        return discriminant

class UserGrouper(DefaultGrouper):
    def transform_discriminant(self, discriminant, transformation=None):
        return discriminant
    def get_group(self, element, discriminant_element, transformation=None):
        discriminant = discriminant_element
        discriminant = self.transform_discriminant(discriminant, transformation)
        return discriminant


class RatingGrouperWith3(DefaultGrouper):

    def transform_discriminant(self, discriminant, transformation):
        discriminant = discriminant.replace("*","")
        discriminant = float(discriminant)
        result = "more_than_3.0"
        if discriminant < 3.0:
            result = "less_than_3.0"
        return result

    def get_group(self, element, discriminant_element, transformation=None):
        discriminant = discriminant_element
        discriminant = self.transform_discriminant(discriminant, transformation)
        return discriminant


class PathGrouper(DefaultGrouper):

    def analyse_all_turns(self, conversation):
        path = False
        quiz = False
        for turn in conversation:
            run_info = turn.run_info
            if run_info is None:
                continue
            run_info = json.loads(run_info)
            utterances = run_info.get("machine_result")

            for utterance in utterances:
                strategy_name = utterance.get("strategy_name")
                if strategy_name == "ContinuePath":
                    path = True
                elif strategy_name == "ContinueQuiz":
                    quiz = True
        return path,quiz

    def transform_discriminant(self, discriminant, transformation):
        conversation_as_discriminant = discriminant
        path, quiz = self.analyse_all_turns(conversation_as_discriminant)
        if path and not quiz:
            return "path"
        elif quiz and not path:
            return "quiz"
        elif not quiz and not path:
            return "none"
        else:
            return "both"

    def get_group(self, element, discriminant_element, transformation=None):
        discriminant = discriminant_element
        discriminant = self.transform_discriminant(discriminant, transformation)
        return discriminant