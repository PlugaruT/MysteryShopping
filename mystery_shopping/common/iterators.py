def pairs(elements, include_last=True):
    """
    Returns pairs of (current, next) elements for a given collection.\n
    The last element from collection is returned as a pair: (current, None) in case `include_last` parameter is `True`

    :param elements: the collection of elements to
    :param include_last: specifies if the last element should be returned additionally as (current, None)
    :return: pairs of (current, next) elements from the collection
    """
    if not elements:
        return
    it = iter(elements)
    curr = next(it)

    for nxt in it:
        yield (curr, nxt)
        curr = nxt

    if include_last:
        yield (curr, None)
