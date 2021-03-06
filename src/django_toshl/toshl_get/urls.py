from django.urls import path
from . import views

urlpatterns = [
    path('toshl/accounts/import/', views.accounts_import),
    path('toshl/tags/import/', views.tags_import),
    path('toshl/transactions/import/', views.transactions_import),
    path('toshl/all/import/', views.all_import),

    path('toshl/currencies/view/', views.currencyElement_view),
    path('toshl/accounts/view/', views.account_view),
    path('toshl/categories/view/', views.category_view),
    path('toshl/tags/view/', views.tag_view),
    path('toshl/transactions/view/', views.transaction_view),
    ]