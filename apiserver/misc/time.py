import pytz
from datetime import timedelta
import dateutil.parser


TZINFOS = {
    'NZDT': pytz.timezone('Pacific/Auckland'),
    'NZST': pytz.timezone('Pacific/Auckland'),
}

TZINFOS = {
    'NZDT': 13*60*60,
    'NZST': 12*60*60,
}

def unix(date_str, tz=None, tzinfos=TZINFOS):
    try:
        dt = dateutil.parser.parse(date_str, tzinfos=tzinfos)
        if tz:
            dt = pytz.timezone(tz).localize(dt)
        return int(dt.timestamp())
    except:
        pass
    return 0
