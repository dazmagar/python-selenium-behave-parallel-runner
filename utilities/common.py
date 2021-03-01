from contextlib import contextmanager

import random
import string


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))
