from datetime import datetime


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


def update_attributes(validated_data, instance):
    for attr, value in validated_data.items():
        setattr(instance, attr, value)


def first_or_none(list):
    try:
        return list[0]
    except IndexError:
        return None
