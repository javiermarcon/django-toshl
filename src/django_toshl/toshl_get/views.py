from django.shortcuts import render
from .processor import do_processing
from .tables import CurrencyElementTable
from django_tables2 import SingleTableView
from .models import CurrencyElement
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


def currencyElement_view(request):
    ''' view the currencies '''
    table = CurrencyElementTable(CurrencyElement.objects.all())
    table.order_by = request.GET.get('sort', ('type', 'code'))
    table.paginate(page=request.GET.get('page', 1), per_page=20)
    return render(request, 'toshl_get/table_view.html', {
        'table': table, 'title': 'Listado de divisas'
    })


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