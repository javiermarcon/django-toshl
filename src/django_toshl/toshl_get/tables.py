import django_tables2 as tables
from .models import CurrencyElement

class CurrencyElementTable(tables.Table):
    class Meta:
        model = CurrencyElement

