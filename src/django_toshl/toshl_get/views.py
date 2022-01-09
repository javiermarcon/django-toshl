from django.shortcuts import render
from django_tables2.config import RequestConfig
from django_tables2.export.export import TableExport
from .processor import do_processing
from .tables import CurrencyElementTable, AccountTable, CategoryTable, TagTable, EntryTable
from .models import CurrencyElement, Account, Category, Tag, Entry
# Create your views here.


def render_imported(request):
    ''' Imports the accounts'''
    return render(request, "toshl_get/data_imported.html")


def process_and_render(request, actions, params=None):
    _ = do_processing(actions, params)
    return render_imported(request)


def accounts_import(request):
    ''' Imports the accounts'''
    actions = ['currencies', 'accounts']
    return process_and_render(request, actions)


def tags_import(request):
    ''' Imports the tags'''
    actions = ['categories', 'tags']
    return process_and_render(request, actions)


def transactions_import(request):
    ''' Imports the transactions'''
    params = [{'from_': '2000-01-01', 'to': '2022-12-01'}]
    return process_and_render(request, ['entries'], params)


def all_import(request):
    ''' Imports the accounts, tags and transactions'''
    actions = ['currencies', 'accounts', 'categories', 'tags', 'entries']
    transaction_params = {'from_': '2000-01-01', 'to': '2022-12-01'}
    params = [None, None, None, None, transaction_params]
    return process_and_render(request, actions, params)


def table_view(request, table, title):
    ''' Muestra una tabla y permite exportarla'''
    # TODO: ver django-filter para filtrar los datos que se muestran en la tabla
    RequestConfig(request, paginate={"per_page": 20}).configure(table)
    # para exportar en formatos
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table)
        return exporter.response("table.{}".format(export_format))
    return render(request, 'toshl_get/table_view.html', {
        'table': table, 'title': title
    })


def currencyElement_view(request):
    ''' view the currencies '''
    table = CurrencyElementTable(CurrencyElement.objects.all(), order_by="type, code")
    title = 'Listado de divisas'
    return table_view(request, table, title)


def account_view(request):
    ''' view the currencies '''
    table = AccountTable(Account.objects.all(), order_by="name")
    title = 'Listado de cuentas'
    return table_view(request, table, title)


def category_view(request):
    ''' view the currencies '''
    table = CategoryTable(Category.objects.all(), order_by="type, name")
    title = 'Listado de categorías'
    return table_view(request, table, title)


def tag_view(request):
    ''' view the currencies '''
    table = TagTable(Tag.objects.all(), order_by="type, category, name")
    title = 'Listado de etiquetas'
    return table_view(request, table, title)


def transaction_view(request):
    ''' view the currencies '''
    table = EntryTable(Entry.objects.all(), order_by="date")
    title = 'Listado de transacciones'
    return table_view(request, table, title)


"""
from django.db.models import Count, Max

unique_fields = ['field_1', 'field_2']

duplicates = (
    MyModel.objects.values(*unique_fields)
    .order_by()
    .annotate(max_id=Max('id'), count_id=Count('id'))
    .filter(count_id__gt=1)
)

for duplicate in duplicates:
    (
        MyModel.objects
        .filter(**{x: duplicate[x] for x in unique_fields})
        .exclude(id=duplicate['max_id'])
        .delete()
    )
"""