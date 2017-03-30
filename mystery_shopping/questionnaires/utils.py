from datetime import datetime


# TODO methods from this file should be moved to mystery_shopping_utils/utils.py

def check_q_param_date(string_to_check):
    try:
        date = datetime.strptime(string_to_check, '%Y-%m-%d').date()
        return date
    except:
        return None


def check_interval_date(data):
    start = check_q_param_date(data.get('start'))
    end = check_q_param_date(data.get('end'))

    return start, end


def update_attributes(instance, data):
    for attr, value in data.items():
        setattr(instance, attr, value)


def first_or_none(list):
    try:
        return list[0]
    except IndexError:
        return None
