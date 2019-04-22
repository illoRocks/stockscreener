import datetime
from pprint import pformat
from operator import itemgetter
from functools import total_ordering
from _collections import defaultdict
from typing import Iterable
from stockscreener.sec_schema import SecSchema


def as_list(x):
    if not isinstance(x, list):
        return [x]
    else:
        return x


@total_ordering
class FillingTimeDelta:
    delta = None
    tolerance = 10

    def __init__(self, delta):
        if isinstance(delta, datetime.timedelta):
            self.delta = delta.days
        else:
            self.delta = delta

    def __eq__(self, other):
        if isinstance(other, int):
            return (self.delta - self.tolerance) <= other <= (self.delta + self.tolerance)
        return self.delta == other

    def __lt__(self, other):
        return self.delta < other

    def __str__(self):
        return str(self.delta)


@total_ordering
class FillingDate:

    @property
    def period_end(self) -> datetime.datetime:
        return self.instant if self.instant else self.endDate

    @property
    def duration(self) -> datetime.timedelta:
        if not self.endDate:
            return FillingTimeDelta(0)
        return FillingTimeDelta(self.endDate - self.startDate)

    def __init__(self, instant=None, endDate=None, startDate=None):
        self.instant = instant  # type: datetime.datetime
        self.startDate = startDate  # type: datetime.datetime
        self.endDate = endDate  # type: datetime.datetime

    def get_date(self):
        return self.instant if self.instant else {'startDate': self.startDate, 'endDate': self.endDate, 'duration': self.duration}

    def __repr__(self):
        return pformat(self.get_date())

    def __lt__(self, other):
        return self.period_end < other.period_end

    def __eq__(self, other):
        if isinstance(other, FillingDate):
            return self.period_end == other.period_end
        return self.period_end == other

    def __str__(self):
        if self.instant:
            return self.instant.strftime("%d/%m/%Y")
        return self.startDate.strftime("%d/%m/%Y") + ' - ' + self.endDate.strftime("%d/%m/%Y")

    def __hash__(self):
        return hash(self.__str__())


class Filling:

    @property
    def duration(self):
        return self.date.duration

    @property
    def is_instant(self):
        return self.date.instant is not None

    def __init__(self, _id=None, cik=None, company=None, form=None, label=None, label_old=None, updated=None, duration=None, value=None, instant=None, endDate=None, startDate=None, segment=None):
        self._id = _id  # type: str
        self.cik = cik if cik else company  # type: str
        self.label = label  # type: str
        self.label_old = label_old  # type: str
        self.date = FillingDate(
            instant=instant, endDate=endDate, startDate=startDate)
        self.segment = segment  # type: str
        self.updated = updated  # type: datetime.datetime
        self.value = value  # type: int
        self.form = form  # type: int

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return '\n' + pformat(vars(self), indent=4) + '\n'

    def __getitem__(self, item):
        return getattr(self, item)


class FillingPosition:

    @property
    def dates(self):
        return set(l['date'] for l in self._inner_list)

    def __init__(self, label, form, filling=None):
        self.label = label
        self.form = form
        self._inner_list = []
        if filling:
            self.append(filling)

    def append(self, filling):
        """append filling to inner filling list"""

        if isinstance(filling, list):
            for f in filling:
                self.append(f)

        elif isinstance(filling, dict):
            self._inner_list.append(Filling(**filling))

        elif isinstance(filling, Filling):
            self._inner_list.append(filling)

        elif isinstance(filling, FillingPosition):
            self._inner_list.extend(filling._inner_list)

        else:
            raise ValueError(
                "value is not of class list, dict, Filling, FillingPosition")

    def filter(self, **kwargs):
        fillings = []
        for key in kwargs:
            values = as_list(kwargs[key])
            fillings.extend(
                [item for item in self._inner_list if item[key] in values])
        return FillingPosition(self.label, self.form, list(fillings))

    def __repr__(self):
        return pformat(self._inner_list)

    def __getitem__(self, item):
        if type(item) is str:
            return getattr(self, item)

        return self._inner_list[item]

    def __len__(self):
        return len(self._inner_list)

    def __str__(self):
        return "; ".join(str(d['value']) for d in self._inner_list)


class FillingList:

    @property
    def dates(self):
        dates = [d for f in self._inner_list.values() for d in f['dates']]
        return sorted(set(dates), reverse=True)

    def __init__(self, fillings=None, as_position_dict=False):

        if as_position_dict:
            self._inner_list = fillings

        elif fillings:
            sec_schema = SecSchema()
            self._inner_list = {}
            for f in fillings:
                raw_label = f.get('label')  # type: str
                if not raw_label:
                    raise KeyError("no label in filling")

                form, label = sec_schema.get_form_and_label(raw_label)

                if not form:
                    if 'instant' in f:
                        form = SecSchema.UNALLOCATED_BALANCE
                    else:
                        form = SecSchema.UNALLOCATED_INCOME_OR_CASHFLOW

                f['label'] = label
                f['label_old'] = raw_label
                f['form'] = form

                if label not in self._inner_list:
                    self._inner_list[label] = FillingPosition(label, form)

                self._inner_list[label].append(f)

        else:
            self._inner_list = None

    def filter(self, label=None, form=None, find_one=False, **kwargs) -> 'FillingList':
        """filter fillings by one or more keys: _id, date, cik, form, label"""

        if not self._inner_list:
            return FillingList()

        positions = self._inner_list.copy()  # type: Iterable[FillingPosition]

        if label:
            labels = [l for l in as_list(label) if l in positions]
            if len(labels) is 0:
                return FillingList()
            positions = {k: positions[k] for k in labels}

        if form:
            form = as_list(form)
            positions = {k: positions[k]
                         for k in positions if positions[k]['form'] in form}

        if kwargs:
            for label in positions:
                positions[label] = positions[label].filter(**kwargs)

        if find_one:
            for k in positions:
                return positions[k]

        positions = {k: positions[k] for k in positions if positions[k]}

        return FillingList(positions, True)

    def filter_one(self, label=None, form=None, **kwargs) -> 'FillingPosition':
        return self.filter(label, form, True, **kwargs)

    def sort_by_date(self, desc=False):
        self.balance_dates = sorted(self.balance_dates, reverse=desc)
        self._inner_list = sorted(
            self._inner_list, key=itemgetter('date'), reverse=desc)

    def __iter__(self):
        """ iter over key and values """
        for key in self._inner_list:
            yield key

    def __repr__(self):
        if not self._inner_list:
            return ''
        return pformat(self._inner_list)

    def __getitem__(self, item):
        return self._inner_list[item]

    def values(self):
        return self._inner_list.values()

    def items(self):
        return self._inner_list.items()


if __name__ == "__main__":
    from pprint import pprint

    def header(x):
        print("\n<<<<<<<<<<<<<<<<<<<< " + x + " >>>>>>>>>>>>>>>>>>\n")

    header("Date operations")
    d1 = FillingDate(instant=datetime.datetime(2016, 4, 1, 0, 0))
    d2 = FillingDate(instant=datetime.datetime(2016, 4, 1, 0, 0))
    d3 = FillingDate(instant=datetime.datetime(2019, 4, 1, 0, 0))
    d4 = FillingDate(startDate=datetime.datetime(
        2018, 4, 1, 0, 0), endDate=datetime.datetime(2019, 4, 1, 0, 0))

    print("is equal: %s" % (d1 == d2))
    print("is not equal: %s" % (d1 == d3))
    print("is lower: %s" % (d1 < d3))
    print("is not lower: %s" % (d3 < d1))
    print("is greater: %s" % (d3 > d1))
    print("duration: %s" % d4.duration)
    print("is yearly: %s" % (d4.duration == 365))
    print("is yearly with tolerance: %s" % (d4.duration == 370))
    print("is duration in array: %s" % (d4.duration in [365]))

    raw = [{'instant': datetime.datetime(2018, 3, 30, 0, 0),
            'updated': datetime.datetime(2019, 2, 21, 0, 0),
            'label': 'Goodwill',
            'value': 3014000000},
           {'instant': datetime.datetime(2017, 3, 31, 0, 0),
            'updated': datetime.datetime(2019, 2, 21, 0, 0),
            'label': 'Goodwill',
            'value': 0},
           {'startDate': datetime.datetime(2016, 4, 1, 0, 0),
            'endDate': datetime.datetime(2017, 4, 1, 0, 0),
            'updated': datetime.datetime(2019, 2, 21, 0, 0),
            'label': 'revenue',
            'value': 111}]

    l = FillingList(raw)

    # header("loop FillingList")
    # for k, v in l:
    #     print('<< ' + k + ' >>')
    #     print(v)

    header("get by label")
    print(l.filter(label='revenue'))

    header("filter date")
    print(l.filter(label='revenue', date=datetime.datetime(2018, 3, 30, 0, 0)))

    # header("show dates")
    # print(l.balance_dates)

    header("duration")
    print(l.filter(duration=360))
    # l2 = l['revenue']  # type: FillingPosition
    # pprint(l2[0].duration == 360)

    # pprint(type(l2[0]))
    # print(l2[0] == 365)
    # print(l2[''])
