import django_tables2 as tables
from .models import CurrencyElement, Account


class CurrencyElementTable(tables.Table):
    class Meta:
        model = CurrencyElement


class AccountTable(tables.Table):
    class Meta:
        model = Account
        sequence = ('id', 'name', 'currency','balance')
        exclude = ('daily_sum_median', 'order')
