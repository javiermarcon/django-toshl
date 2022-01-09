import django_tables2 as tables
from .models import CurrencyElement, Account, Category, Tag, Entry


class CurrencyElementTable(tables.Table):
    class Meta:
        model = CurrencyElement


class AccountTable(tables.Table):
    currency = tables.Column(accessor='currency.code.code')
    connection = tables.Column(accessor='connection.name')
    class Meta:
        model = Account
        sequence = ('id', 'name', 'currency', 'balance', 'connection')
        exclude = ('daily_sum_median', 'order', 'name_override')


class CategoryTable(tables.Table):
    class Meta:
        model = Category
        sequence = ('id', 'name', 'type', 'modified')
        exclude = ('name_override', )


class TagTable(tables.Table):
    class Meta:
        model = Tag
        sequence = ('id', 'name', 'category', 'type')
        exclude = ('name_override', )

    def render_category(self, value):
        cat = Category.objects.get(id=value)
        return cat.name


class EntryTable(tables.Table):
    tags = tables.ManyToManyColumn(transform=lambda tag: tag.name) #verbose_name="Tags")
    class Meta:
        model = Entry
        sequence = ('id', 'date', 'amount', 'currency', 'desc', 'account', 'category', 'tags')
        #exclude = ('name_override', )

    def render_category(self, value):
        cat = Category.objects.get(id=value)
        return cat.name

    def render_account(self, value):
        aco = Account.objects.get(id=value)
        return aco.name
