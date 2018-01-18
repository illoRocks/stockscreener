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
        print('TypeError: variable is %s. It must be dict or list!' % type(t))
        return
    summary += '\t' + str(type(t))
    print(summary)