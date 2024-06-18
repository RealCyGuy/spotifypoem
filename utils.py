import re
from itertools import zip_longest


def sanitize(string: str) -> str:
    return re.sub(r"\W", "", string.lower())


def grouper(iterable, n):
    args = [iter(iterable)] * n
    return zip_longest(*args)
