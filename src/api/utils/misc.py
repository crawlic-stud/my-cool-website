from datetime import datetime, timezone
import random


def random_6_digit_number():
    return random.randint(100_000, 999_999)


def utcnow():
    dt = datetime.now(timezone.utc)
    return dt
