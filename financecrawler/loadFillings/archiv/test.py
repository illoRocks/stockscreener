import time
import sys
import pprint
# t = [time.time()]
# t.append()
# time.sleep(1)
# t.append(time.time())
# time.sleep(2)
# t.append(time.time())
# time.sleep(3)
# t.append(time.time())

t = {'start': time.time()}
time.sleep(1)
t['2'] = time.time()
time.sleep(1)
t['3'] = time.time()
time.sleep(1)
t['4'] = time.time()


def ctime(t, digit=1):
    summary = 'Verbrauchte Zeit: '
    w = False
    n = 1
    if type(t) == list:
        for s in t:
            if w:
                summary += 't%s-%s\t' % (n, round(s-w, digit))
            w = s
            n += 1
    elif type(t) == dict:
        for s in t:
            if w:
                summary += '%s - %ssec | \t' % (n, round(t[s]-w, digit))
            w = t[s]
            n += 1
    else:
        print('TypeError: variable is %s. It must be dict or list!' % type(t))
        return
    print(summary)

ctime(t)
pprint.pprint(t)
