
from datetime import datetime
import pytz


def timezone_time(time):
    tehran = pytz.timezone("Asia/Tehran")
    fmt = '%Y-%m-%d %H:%M:%S'
    return tehran.localize(time).strftime(fmt)
