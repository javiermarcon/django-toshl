import django_tables2 as tables
from .models import CurrencyElement, Account


class CurrencyElementTable(tables.Table):
    class Meta:
        model = CurrencyElement


class AccountTable(tables.Table):
    currency = tables.Column(accessor='currency.code.code')
    connection = tables.Column(accessor='connection.name')
    class Meta:
        model = Account
        sequence = ('id', 'name', 'currency','balance', 'connection')
        exclude = ('daily_sum_median', 'order', )
