import os
import random


def get_token(*, regen: bool = False):
    if "MELCHIOR_DAEMON_TOKEN" in os.environ and not regen:
        return os.environ["MELCHIOR_DAEMON_TOKEN"]
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # noqa
    token = "".join(random.choices(chars, k=32))
    os.environ["MELCHIOR_DAEMON_TOKEN"] = token
    return token
