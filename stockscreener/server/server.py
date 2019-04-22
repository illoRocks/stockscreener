from stockscreener.interfaces import FillingList, SecSchema
from stockscreener.database.db_client import DBClient
from flask import Flask, render_template
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
import json
from pprint import pprint
import logging
logger = logging.getLogger(__name__)


client = DBClient()
client.connect()

sec_schema = SecSchema()

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'you-will-never-guess'


class SetLabelForm(FlaskForm):
    form = StringField('form')
    label_company = StringField('Label')
    label_in_json = StringField('LabelInJSON')
    submit = SubmitField('save')


@app.route('/')
def overview():
    context = {
        'companies': client.get_companies()
    }
    return render_template('index.html', **context)


@app.route('/id/<id>', methods=['GET', 'POST'])
def show_company(id: str):
    context = {}

    form = SetLabelForm()
    if form.is_submitted():
        sec_schema.set_label(form.form.data, form.label_in_json.data, form.label_company.data)
        sec_schema.save()
        sec_schema.reload()
    context['form'] = form

    company = client.get_one_company({"_id": id})
    fillings = client.get_fillings(company['cik'])
    context['sec_schema'] = sec_schema
    context['company'] = company
    context['shares'] = fillings.filter(form=SecSchema.SHARES)
    context['balance'] = fillings.filter(form=SecSchema.BALANCE)
    context['balance_all'] = fillings.filter(form=SecSchema.UNALLOCATED_BALANCE)
    context['income'] = fillings.filter(form=SecSchema.INCOME, duration=360)
    context['income_all'] = fillings.filter(form=SecSchema.UNALLOCATED_INCOME_OR_CASHFLOW, duration=360)

    
    return render_template('fillings.html', **context)

if __name__ == '__main__':
   app.run()
