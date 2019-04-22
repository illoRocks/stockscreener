import json
from os import path, getcwd
from stockscreener.helper import Singleton

def _get_form_and_label(label_schema, form, raw_label):
    for label in label_schema[form]:
        for l in label_schema[form][label]:
            if raw_label == l:
                return label
    return None


class SecSchema(metaclass=Singleton):
    BALANCE = 'balance'
    INCOME = 'income'
    CASHFLOW = 'cashflow'
    SHARES = 'shares'
    UNALLOCATED_INCOME_OR_CASHFLOW = 'IncomeOrCashFlow'
    UNALLOCATED_BALANCE = 'UnallocatedBalance'

    @property
    def forms(self):
        return [self.BALANCE, self.INCOME, self.CASHFLOW]

    @property
    def label_schema(self):
        return self.schema['labels']

    @property
    def days_yearly(self) -> list:
        """ return lower and upper days for yearly fillings """
        return self.schema['settings']['quarter']['q4']

    def __init__(self, schema_path=None):
        self.json_path = schema_path or path.join(getcwd(), 'sec_schema.json') # './sec_schema.json'
        self.reload()

    def reload(self):
        self.schema = json.load(
            open(path.join(path.dirname(__file__), self.json_path)))
        import pprint
        pprint.pprint(self.schema)


    def get_form_and_label(self, raw_label) -> (str, str):
        """ return form and correct label from a raw filling label """

        label = _get_form_and_label(self.label_schema, self.BALANCE, raw_label)
        if label:
            return self.BALANCE, label

        label = _get_form_and_label(self.label_schema, self.SHARES, raw_label)
        if label:
            return self.SHARES, label

        label = _get_form_and_label(self.label_schema, self.INCOME, raw_label)
        if label:
            return self.INCOME, label

        label = _get_form_and_label(self.label_schema, self.CASHFLOW, raw_label)
        if label:
            return self.CASHFLOW, label

        return None, raw_label

    def get_labels(self, form):
        if form not in self.forms:
            raise ValueError(form + " not in forms!")
        return [l for l in self.label_schema[form] if l != 'desc']

    def set_label(self, form, my_label, company_label):
        if form not in self.forms:
            raise ValueError
        if my_label not in self.label_schema[form]:
            self.label_schema[form][my_label] = []

        self.label_schema[form][my_label].append(company_label)

    def save(self, json_path=None) -> None:
        json_path = json_path or self.json_path
        for form in self.label_schema:
            for label in self.label_schema[form]:
                self.label_schema[form][label] = list(
                    set(self.label_schema[form][label]))
        with open(json_path, 'w') as f:
            json.dump(self.schema, f, indent=4)
