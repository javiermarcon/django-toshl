from django.db import models
from .model_choices import (ACCOUNT_STATUSES, ACCOUNT_TYPES, CURRENCY_TYPES, IMAGE_STATUSES,
                            NOTIFICATION_TYPES, ENTRIES_REPEAT_TYPES, ENTRIES_REPEAT_FREQ,
                            ACCOUNT_CONNECTION_STATUSES, BUDGET_STATUSES, BUDGET_TYPES,
                            RECURRENCY_FREQUENCIES, TAG_TYPES, CATEGORY_TYPES, ENTRY_IMAGES_TYPES,
                            REMINDER_PERIODS, ENTRY_REVIEW_TYPES, USER_CURRENCY_UPDATES
                            )

# Create your models here.

class CurrencyElement(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    modified = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    precision = models.IntegerField() # 0-9
    symbol = models.CharField(max_length=10)
    type = models.CharField(max_length=20, choices=CURRENCY_TYPES)


class Image(models.Model):
    deleted = models.BooleanField(blank=True, null=True)
    filename = models.CharField(max_length=100, blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    path = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=IMAGE_STATUSES)
    type = models.CharField(max_length=100, blank=True, null=True)


class Notification(models.Model):
    action = models.CharField(max_length=100)
    date = models. DateTimeField()
    deleted = models.BooleanField(blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    modified = models.CharField(max_length=100)
    text = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)


class EntryRepeat(models.Model):
    byday = models.CharField(max_length=100)
    bymonthday = models.CharField(max_length=100)
    bysetpos = models.CharField(max_length=100)
    count = models.IntegerField() # min = 1
    end = models.DateField()
    entries = models.ManyToManyField('Entry', related_name='repeated_entries', blank=True, null=True)
    frequency = models.CharField(max_length=20, choices=ENTRIES_REPEAT_FREQ)
    id = models.IntegerField(primary_key=True)
    interval = models.IntegerField() # required=True min 1 max 255
    iteration = models.IntegerField() # min 0
    start = models.DateField() # required=True)
    template = models.BooleanField(blank=True, null=True)
    template_end = models.DateField()
    template_start = models.DateField()
    type = models.CharField(max_length=20, choices=ENTRIES_REPEAT_TYPES)


class AccountAvg(models.Model):
    expenses = models.FloatField(default=0)
    incomes = models.FloatField(default=0)


class AccountBilling(models.Model):
    byday = models.CharField(max_length=100, blank=True, null=True)
    bymonthday = models.CharField(max_length=100, blank=True, null=True)
    bysetpos = models.CharField(max_length=100, blank=True, null=True)


class AccountConnection(models.Model):
    id = models.IntegerField(primary_key=True)
    logo = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=ACCOUNT_CONNECTION_STATUSES)


class Currency(models.Model):
    code = models.ForeignKey(CurrencyElement, primary_key=True, on_delete=models.CASCADE) # CharField(max_length=10) # pattern='[A-Z_]{2,10}')
    fixed = models.BooleanField(default=False)
    main_rate = models.FloatField(blank=True, null=True)
    rate = models.FloatField()


class AccountMedian(models.Model):
    expenses = models.FloatField(default=0)
    incomes = models.FloatField(default=0)


class AccountGoal(models.Model):
    amount = models.FloatField()
    end = models.DateField()
    start = models.DateField()


class AccountSettle(models.Model):
    byday = models.CharField(max_length=100, blank=True, null=True)
    bymonthday = models.CharField(max_length=100, blank=True, null=True)
    bysetpos = models.CharField(max_length=100, blank=True, null=True)


class Account(models.Model):
    id = models.IntegerField(primary_key=True)
    avg = models.ForeignKey(AccountAvg, on_delete=models.CASCADE, blank=True, null=True)
    balance = models.FloatField()
    billing = models.ForeignKey(AccountBilling, on_delete=models.CASCADE, blank=True, null=True)
    connection = models.ForeignKey(AccountConnection, on_delete=models.CASCADE, blank=True, null=True)
    count = models.IntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, blank=True, null=True)
    daily_sum_median = models.ForeignKey(AccountMedian, on_delete=models.CASCADE, blank=True, null=True)
    deleted = models.BooleanField(blank=True, null=True)
    extra = models.CharField(max_length=4096, blank=True, null=True)
    goal = models.ForeignKey(AccountGoal, on_delete=models.CASCADE, blank=True, null=True)
    initial_balance = models.FloatField()
    limit = models.FloatField(blank=True, null=True)
    modified = models. DateTimeField()
    name = models.CharField(max_length=100)
    name_override = models.BooleanField(blank=True, null=True)
    order = models.IntegerField()
    parent = models.CharField(max_length=100, blank=True, null=True)
    recalculated = models.BooleanField(blank=True, null=True)
    review = models.IntegerField(blank=True, null=True)
    settle = models.ForeignKey(AccountSettle, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=10, choices=ACCOUNT_STATUSES)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)


class BudgetProblem(models.Model):
    deleted_accounts = models.ManyToManyField('Account', blank=True, null=True)
    deleted_categories = models.ManyToManyField('Category', blank=True, null=True)
    deleted_tags = models.ManyToManyField('Tag', blank=True, null=True)
    description = models.CharField(max_length=100)
    id = models.IntegerField(primary_key=True)


class Recurrence(models.Model):
    byday = models.CharField(max_length=100)
    bymonthday = models.CharField(max_length=100)
    bysetpos = models.CharField(max_length=100)
    end = models.DateField()
    frequency = models.CharField(max_length=20, choices=RECURRENCY_FREQUENCIES)
    interval = models.IntegerField() # minimum=1, maximum=127))
    iteration = models.IntegerField() # minimum=0))
    start = models.DateField()


class Budget(models.Model):
    # exclamation_mark_accounts: Maybe[List[str]] = Property(Array(String()), source='!accounts')
    # exclamation_mark_categories: Maybe[List[str]] = Property(Array(String()), source='!categories')
    # exclamation_mark_tags: Maybe[List[str]] = Property(Array(String()), source='!tags')
    accounts = models.ManyToManyField('Account', related_name='budget_accounts', blank=True)
    amount = models.FloatField()
    categories = models.ManyToManyField('Category', related_name='budget_categories', blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, blank=True, null=True)
    deleted = models.BooleanField(blank=True, null=True)
    delta = models.FloatField()
    extra = models.CharField(max_length=4096, blank=True, null=True)
    froma = models.DateField()
    history_amount_median = models.FloatField()
    id = models.IntegerField(primary_key=True)
    limit = models.FloatField(blank=True, null=True)
    limit_planned = models.FloatField(blank=True, null=True)
    modified = models.CharField(max_length=100)
    name = models.CharField(max_length=300)
    order = models.IntegerField() # minimum=0, maximum=255))
    parent = models.CharField(max_length=100)
    percent = models.FloatField()
    planned = models.FloatField()
    problem = models.ForeignKey(BudgetProblem, on_delete=models.CASCADE, blank=True, null=True)
    recalculated = models.BooleanField(blank=True, null=True)
    recurrence = models.ForeignKey(Recurrence, on_delete=models.CASCADE, blank=True, null=True)
    rollover = models.BooleanField(default=False, blank=True, null=True)
    rollover_amount = models.FloatField(default=0)
    rollover_amount_planned = models.FloatField(default=0)
    rollover_override = models.BooleanField(default=False, blank=True, null=True)
    status = models.CharField(max_length=20, choices=BUDGET_STATUSES)
    tags = models.ManyToManyField('Tag', related_name='budget_tags', blank=True)
    to = models.DateField()
    type = models.CharField(max_length=20, choices=BUDGET_TYPES)


class CategoryCounts(models.Model):
    budgets = models.IntegerField(blank=True, null=True)
    entries = models.IntegerField(blank=True, null=True)
    expense_entries = models.IntegerField(blank=True, null=True)
    expense_tags = models.IntegerField(blank=True, null=True)
    expense_tags_used_with_category = models.IntegerField(blank=True, null=True)
    income_entries = models.IntegerField(blank=True, null=True)
    income_tags = models.IntegerField(blank=True, null=True)
    income_tags_used_with_category = models.IntegerField(blank=True, null=True)
    tags = models.IntegerField(blank=True, null=True)
    tags_used_with_category = models.IntegerField(blank=True, null=True)


class Category(models.Model):
    counts = models.ForeignKey(CategoryCounts, on_delete=models.CASCADE, blank=True, null=True)
    deleted = models.BooleanField(blank=True, null=True)
    extra = models.CharField(max_length=4096, blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    modified = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    name_override = models.BooleanField(default=False, blank=True, null=True)
    type = models.CharField(max_length=20, choices=CATEGORY_TYPES)


class CategorySumExpenses(models.Model):
    count = models.IntegerField() # minimum=0), required=True)
    sum = models.FloatField()


class CategorySumIncomes(models.Model):
    count = models.IntegerField() # minimum=0), required=True)
    sum = models.FloatField()


class CategorySum(models.Model):
    category = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    expenses = models.ForeignKey(CategorySumExpenses, on_delete=models.CASCADE, blank=True, null=True)
    incomes = models.ForeignKey(CategorySumIncomes, on_delete=models.CASCADE, blank=True, null=True)
    modified = models.CharField(max_length=100)


class EntryImage(models.Model):
    filename = models.CharField(max_length=100)
    id = models.IntegerField(primary_key=True)
    path = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=ENTRY_IMAGES_TYPES)
    type = models.CharField(max_length=100)


class EntryImport(models.Model):
    connection = models.CharField(max_length=100)
    id = models.IntegerField(primary_key=True)
    memo = models.CharField(max_length=100)
    payee = models.CharField(max_length=100)
    pending = models.BooleanField(blank=True, null=True)


class EntryLocation(models.Model):
    id = models.IntegerField(primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    venue_id = models.CharField(max_length=100)


class Reminder(models.Model):
    at = models. DateTimeField()
    number = models.IntegerField() # minimum=0, maximum=255), required=True)
    period = models.CharField(max_length=10, choices=REMINDER_PERIODS)


class EntryReview(models.Model):
    completed = models.BooleanField(blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=20, choices=ENTRY_REVIEW_TYPES)


class EntrySettle(models.Model):
    id = models.IntegerField(primary_key=True)


class EntryTransaction(models.Model):
    account = models.CharField(max_length=100)
    amount = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, blank=True, null=True)
    id = models.IntegerField(primary_key=True)


class Entry(models.Model):
    account = models.CharField(max_length=100)
    amount = models.FloatField()
    category = models.CharField(max_length=100)
    completed = models.BooleanField(default=False, blank=True, null=True)
    created = models. DateTimeField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    deleted = models.BooleanField(blank=True, null=True)
    desc = models.CharField(max_length=3072)
    extra = models.CharField(max_length=4096, blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    images = models.ManyToManyField('Image', related_name='entry_images', blank=True)
    importar = models.ForeignKey(EntryImport, on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey(EntryLocation, on_delete=models.CASCADE, blank=True, null=True)
    modified = models.CharField(max_length=100)
    # readonly: Maybe[List[str]] = Property(Array(String()))
    reminders = models.ManyToManyField('Reminder', related_name='entry_reminders', blank=True)
    repeat = models.ForeignKey(EntryRepeat, on_delete=models.CASCADE, blank=True, null=True)
    review = models.ForeignKey(EntryReview, on_delete=models.CASCADE, blank=True, null=True)
    settle = models.ForeignKey(EntrySettle, on_delete=models.CASCADE, blank=True, null=True)
    split = models.ManyToManyField('Entry', related_name='splited_entries', blank=True)
    tags = models.ManyToManyField('Tag', related_name='entry_tags', blank=True)
    transaction = models.ForeignKey(EntryTransaction, on_delete=models.CASCADE, blank=True, null=True)


#class EntrySplit(models.Model):
#    children = models.ForeignKey(Entry, on_delete=models.CASCADE)
#    parent = models.ForeignKey(Entry, on_delete=models.CASCADE )


class DayExpenses(models.Model):
    count = models.IntegerField() # minimum=0), required=True)
    sum = models.FloatField()


class DayIncomes(models.Model):
    count = models.IntegerField() # minimum=0), required=True)
    sum = models.FloatField()


class Day(models.Model):
    day = models.DateField()
    expenses = models.ForeignKey(DayExpenses, on_delete=models.CASCADE, blank=True, null=True)
    incomes = models.ForeignKey(DayIncomes, on_delete=models.CASCADE, blank=True, null=True)
    modified = models.CharField(max_length=100)


# class ExportFile(models.Model):
#     filename = models.CharField(max_length=100)
#     filesize = models.FloatField()
#     format = models.CharField(max_length=20, choices=['csv', 'xls', 'pdf', 'ofx']))


# class ExportData(models.Model):
#     filename = models.CharField(max_length=100)
#     files: Maybe[List[ExportFile]] = Property(Array(ExportFile))
#     filesize = models.FloatField()
#     path = models.CharField(max_length=100)
#     valid_until = models. DateTimeField()


# class Export(models.Model):
#     exclamation_mark_accounts: Maybe[List[str]] = Property(Array(String(), uniqueItems=True), source='!accounts')
#     exclamation_mark_categories: Maybe[List[str]] = Property(Array(String(), uniqueItems=True), source='!categories')
#     exclamation_mark_locations: Maybe[List[str]] = Property(Array(String(), uniqueItems=True), source='!locations')
#     exclamation_mark_tags: Maybe[List[str]] = Property(Array(String(), uniqueItems=True), source='!tags')
#     accounts: Maybe[List[str]] = Property(Array(String(), uniqueItems=True))
#     categories: Maybe[List[str]] = Property(Array(String(), uniqueItems=True))
#     created = models. DateTimeField()
#     data: Maybe[ExportData] = Property(ExportData)
#     emails: Maybe[List[str]] = Property(Array(String(format='email'), uniqueItems=True))
#     formats: Maybe[List[str]] = Property(Array(String(enum=['csv', 'xls', 'pdf', 'ofx']), additionalItems=False, uniqueItems=True))
#     froma = models.DateField()
#     id = models.IntegerField(primary_key=True)
#     locations: Maybe[List[str]] = Property(Array(String(), uniqueItems=True))
#     modified = models.CharField(max_length=100)
#     resources: Maybe[List[str]] = Property(Array(String(enum=['expenses', 'incomes', 'budgets', 'summary', 'attachments', 'attachments_grid', 'balances']), additionalItems=False, uniqueItems=True))
#     seen = models.BooleanField(blank=True, null=True)
#     status = models.CharField(max_length=20, choices=['sending', 'sent', 'error', 'generating', 'generated']))
#     tags: Maybe[List[str]] = Property(Array(String(), uniqueItems=True))
#     to = models.DateField()
#     type = models.CharField(max_length=20, choices=['export', 'attachments', 'user_data']))


class Expenses(models.Model):
    count = models.IntegerField() # minimum=0))
    sum = models.FloatField()


class Incomes(models.Model):
    count = models.IntegerField() # Integer(minimum=0))
    sum = models.FloatField()


class Location(models.Model):
    address = models.CharField(max_length=255)
    amount = models.FloatField()
    chain_id = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    expenses = models.ForeignKey(Expenses, on_delete=models.CASCADE, blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    incomes = models.ForeignKey(Incomes, on_delete=models.CASCADE, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    modified = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    used = models.BooleanField(blank=True, null=True)
    venue_id = models.CharField(max_length=100)
    visits = models.IntegerField() # minimum=0))


class TagCounts(models.Model):
    budgets = models.IntegerField() # required=True)
    entries = models.IntegerField() # required=True)
    unsorted_entries = models.IntegerField()


class Tag(models.Model):
    category = models.CharField(max_length=100)
    counts = models.ForeignKey(TagCounts, on_delete=models.CASCADE, blank=True, null=True)
    deleted = models.BooleanField(blank=True, null=True)
    extra = models.CharField(max_length=4096, blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    meta_tag = models.BooleanField(blank=True, null=True)
    modified = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    name_override = models.BooleanField(default=False, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TAG_TYPES)


class TagSumExpenses(models.Model):
    categories = models.ManyToManyField('Category', related_name='tagsum_expenses', blank=True)
    count = models.IntegerField() #minimum=0), required=True)
    sum = models.FloatField()


class TagSumIncomes(models.Model):
    categories = models.ManyToManyField('Category', related_name='tagsum_incomes', blank=True)
    count = models.IntegerField() # minimum=0), required=True)
    sum = models.FloatField()


class TagSum(models.Model):
    expenses = models.ForeignKey(TagSumExpenses, on_delete=models.CASCADE, blank=True, null=True)
    incomes = models.ForeignKey(TagSumIncomes, on_delete=models.CASCADE, blank=True, null=True)
    modified = models.CharField(max_length=100)
    tag = models.CharField(max_length=100)


class CustomCurrency(models.Model):
    code = models.CharField(max_length=100) # pattern='[A-Z_]{2,10}'))
    fixed = models.BooleanField(default='false', blank=True, null=True)
    rate = models.FloatField()
    reference_currency = models.CharField(max_length=100) # pattern='[A-Z_]{2,10}'))


class UserCurrency(models.Model):
    custom = models.ForeignKey(CustomCurrency, on_delete=models.CASCADE, blank=True, null=True)
    custom_exchange_rate = models.FloatField()
    main = models.CharField(max_length=100) # pattern='[A-Z_]{2,10}'))
    update = models.CharField(max_length=20, choices=USER_CURRENCY_UPDATES)
    update_accounts = models.BooleanField(blank=True, null=True)


class UserLimits(models.Model):
    accounts = models.BooleanField(blank=True, null=True)
    bank = models.BooleanField(blank=True, null=True)
    budgets = models.BooleanField(blank=True, null=True)
    export = models.BooleanField(blank=True, null=True)
    images = models.BooleanField(blank=True, null=True)
    importar = models.BooleanField(blank=True, null=True) # source='import')
    locations = models.BooleanField(blank=True, null=True)
    passcode = models.BooleanField(blank=True, null=True)
    planning = models.BooleanField(blank=True, null=True)
    pro_share = models.BooleanField(blank=True, null=True)
    reminders = models.BooleanField(blank=True, null=True)
    repeats = models.BooleanField(blank=True, null=True)


class UserMigration(models.Model):
    date_migrated = models. DateTimeField()
    finished = models.BooleanField(blank=True, null=True)
    revert_until = models. DateTimeField()


class UserPartner(models.Model):
    end = models. DateTimeField()
    name = models.CharField(max_length=100)
    start = models. DateTimeField()


# class UserProPayment(models.Model):
#    id = models.IntegerField(primary_key=True)
#    next = models. DateTimeField()
#    provider = models.CharField(max_length=20, choices=['apple', 'google', 'microsoft', 'g2s', 'adyen', 'amazon', 'bitpay', 'paypal', 'unknown'])
#    trial = models.BooleanField(default='false')


# class UserProTrial(models.Model):
#    end = models. DateTimeField()
#    start = models. DateTimeField()


# class UserProVAT(models.Model):
#    address = models.CharField(max_length=100)
#    city = models.CharField(max_length=100)
#    country = models.CharField(max_length=100)
#    name = models.CharField(max_length=100)
#    post = models.CharField(max_length=100)
#    state = models.CharField(max_length=100)
#    vat = models.CharField(max_length=100)


# class UserPro(models.Model):
#    level = models.CharField(max_length=20, choices=['pro', 'medici']))
#    partner: Maybe[List[UserPartner]] = Property(Array(UserPartner))
#    payment: Maybe[UserProPayment] = Property(UserProPayment)
#    remaining_credit = models.FloatField()
#    since = models. DateTimeField()
#    trial: Maybe[UserProTrial] = Property(UserProTrial)
#    until = models. DateTimeField()
#    vat: Maybe[UserProVAT] = Property(UserProVAT)


class ToshlUser(models.Model):
    country = models.CharField(max_length=100) # pattern='[A-Z]{2}'))
    currency = models.ForeignKey(UserCurrency, on_delete=models.CASCADE, blank=True, null=True)
    email = models.CharField(max_length=100) # format='email', maxLength=254))
    extra = models.CharField(max_length=4096, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    #flags: Maybe[List[str]] = Property(Array(String()))
    id = models.IntegerField(primary_key=True)
    joined = models. DateTimeField()
    language = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    #limits: Maybe[UserLimits] = Property(UserLimits)
    locale = models.CharField(max_length=100)
    #migration: Maybe[UserMigration] = Property(UserMigration)
    modified = models.CharField(max_length=100)
    notifications = models.IntegerField()
    otp_enabled = models.BooleanField(blank=True, null=True)
    # pro: Maybe[UserPro] = Property(UserPro)
    # social: Maybe[List[str]] = Property(Array(String(enum=['toshl', 'google', 'facebook', 'twitter', 'evernote', 'foursquare', 'etalio', 'flickr', 'apple']), additionalItems=False, uniqueItems=True))
    start_day = models.IntegerField(default=1) #, minimum=1, maximum=31))
    # steps: Maybe[List[str]] = Property(Array(String(enum=['income', 'expense', 'budget', 'budget_category']), additionalItems=False, uniqueItems=True))
    timezone = models.CharField(max_length=100)
    trial_eligible = models.BooleanField(default=False, blank=True, null=True)
