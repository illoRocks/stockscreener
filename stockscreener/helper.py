from datetime import datetime
import logging
import re
from argparse import ArgumentTypeError

logger = logging.getLogger(__name__)

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def ctime(t, digit=1):
    ''' berechnet verbrauchte Zeit '''

    summary = 'Verbrauchte Zeit: '
    w = False
    n = 1
    if type(t) == list:
        for s in t:
            if w:
                summary += 't%s-%s\t' % (n, round(s - w, digit))
            w = s
            n += 1
    elif type(t) == dict:
        for s in t:
            if w:
                summary += '%s - %ssec | \t' % (s, round(t[s] - w, digit))
            w = t[s]
            n += 1
    else:
        logger.error('TypeError: variable is %s. It must be dict or list!' % type(t))
        return
    # summary += '\t' + str(type(t))
    logger.debug(summary)


def bool_or_int(v):
    if v.lower() in ('yes', 'true', 't', 'y'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', '1'):
        return False
    else:
        try:
            int(v)
            return int(v)
        except ValueError:
            raise ArgumentTypeError('Boolean value expected.')


def parse_date(str):
    if str == None:
        return None
    # pattern = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
    # pattern.match(str)

    format = '%Y-%m-%d'
    return datetime.strptime(str, format)
