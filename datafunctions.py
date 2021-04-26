from datetime import datetime
from pytz import timezone, utc
import random, string

# Gets the current time in PST, to get the time, do print(get_pst_time())
def get_pst_time():
    date_format='%m-%d-%Y %H:%M:%S %Z'
    date = datetime.now(tz=utc)
    date = date.astimezone(timezone('US/Pacific'))
    pstDateTime=date.strftime(date_format)
    return pstDateTime

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))