def calculate_percentage(nominator, denominator, round_to=2):
    """
    helper method for calculating the percentage
    :param nominator: what to divide
    :param denominator: on what to divide
    :param round_to: how many digits after comma
    :return: float
    """
    if denominator <= 0:
        denominator = 1
    return round(nominator / denominator * 100, round_to)
