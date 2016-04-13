from datetime import datetime
from mystery_shopping.mystery_shopping_utils.constants import Constants


class ValidateQuestion:
    def single_multiple(self, to_validate):
        results = to_validate.split(Constants.CHOICES_SPLITTER)
        errors = []
        for result in results:
            answer = result.split(Constants.CHOICE_BODY_VALUE_SPLITTER)
            if answer[0] == '':
                errors.append("in answer '" + result + "' answer value is none")
            try:
                answer[1]
                try:
                    int(answer[1])
                except ValueError:
                    errors.append("in answer '" + result + "' the weight is not a number")
            except IndexError:
                errors.append("in answer '" + result + "' the weight does not exist")
        return errors

    def date_validator(self, to_validate):
        error = ''
        if len(to_validate) < 11:
            try:
                datetime.strptime(to_validate, Constants.DATE_VALIDATOR)
            except ValueError:
                error = 'the answer is not of date type'
        else:
            try:
                datetime.strptime(to_validate, Constants.DATETIME_VALIDATOR)
            except ValueError:
                error = 'the answer is not of datetime type'
        return error
