from django.db import models
from django.conf import settings
# from django.utils.timezone import make_aware
import toshling
# import datetime
from dateutil import tz
import six
from dateutil.parser import parse
from .models import (Account, AccountAvg, AccountBilling, AccountConnection, Currency, AccountMedian, AccountGoal,
                     AccountSettle, CurrencyElement, Category, Tag, CategoryCounts, TagCounts, Entry, EntryImport,
                     EntryReview, EntryTransaction)
import pprint
# import pdb

class EntriesProcessor(object):
    client = None
    action = ''
    querysets = {}
    actionClases = {'accounts': Account,
                    'currencies': CurrencyElement,
                    'categories': Category,
                    'tags': Tag,
                    'entries': Entry,
                    }
    fieldExceptions = {'import_': 'importar'}
    unknown_fields = {}

    def __init__(self):
        self.get_toshl_client()
        self.reversedFieldExceptions = dict((v, k) for k, v in self.fieldExceptions.items())

    def excepted_params(self, params):
        newParams = params.copy()
        for index, item in enumerate(newParams):
            if item in self.fieldExceptions:
                newParams[index] = self.fieldExceptions[item]
        return newParams

    def check_values(self, record, data, primary):
        # check if we only have the pk just to get the object
        all_null = [x for x in data if data[x] and x != primary]
        if all_null:
            return False
        # check if values are different
        for d in data:
            if getattr(record, d) != data[d]:
                return True
        return False

    def get_toshl_client(self):
        self.client = toshling.Client(settings.TOSHL_API)

    def upsert_record(self, modelName, data, primary):
        obj = None
        # print(("upserting", modelName, data, primary))
        # import pdb; pdb.set_trace()
        queryset = self.get_queryset(modelName, primary)
        if primary in data and data[primary] in queryset:
            obj = queryset[data[primary]]
            if self.check_values(obj, data, primary):
                obj.update(**data)
                obj.save()
        else:
            obj = modelName(**data)
            obj.save()
        return obj

    def get_queryset(self, modelName, primary):
        if modelName not in self.querysets:
            self.querysets[modelName] = dict([(getattr(record, primary), record) for record in modelName.objects.all()])
        return self.querysets[modelName]

    def get_fields(self, modelClass):
        return modelClass._meta.get_fields()

    def get_primary(self, fields):
        return [fld.name for fld in fields if hasattr(fld, 'primary_key') and fld.primary_key][0]

    def get_related(self, field):
        relatedName = field.related_model.__name__
        #if relatedName not in globals():
        #    pdb.set_trace()
        relatedModel = globals()[relatedName]
        relatedModelFields = self.get_fields(relatedModel)
        relatedPrimary = self.get_primary(relatedModelFields)
        return (relatedModel, relatedModelFields, relatedPrimary)

    def process_foreign_key_field(self, field, fldValue):
        #print((fldValue, field, "foreign_key"))
        # import pdb;pdb.set_trace()
        (relatedModel, relatedModelFields, relatedPrimary) = self.get_related(field)
        # related_params = dir(fldValue)
        if not isinstance(fldValue, six.string_types):
            objValues = {field.name: self.process_fldValue(getattr(fldValue, field.name), field) for field in relatedModelFields if
                         hasattr(fldValue, field.name)}
            #for field in relatedModelFields:
            #    if field.name in objValues and isinstance(field, models.ForeignKey):
            #        objValues[field.name] = self.process_foreign_key_field(field, objValues[field.name])
        else:
            objValues = {relatedPrimary: fldValue}
        fldValue = self.upsert_record(relatedModel, objValues, relatedPrimary)
        # import pdb; pdb.set_trace()
        return fldValue

    def process_m2m_field(self, field, dataObject, mainObject):
        try:
            # import pdb;pdb.set_trace()
            if hasattr(dataObject, field.name):
                fldValue = getattr(dataObject, field.name)
                if str(fldValue) == 'NotPassed':
                    return
                #print((fldValue, field, "m2m_key"))
                (relatedModel, relatedModelFields, relatedPrimary) = self.get_related(field)
                searchId = '{}__in'.format(relatedPrimary)
                searchParam = {searchId: fldValue}
                tags = relatedModel.objects.filter(**searchParam)
                for tag in tags:
                    getattr(mainObject, field.name).add(getattr(tag, relatedPrimary))
                mainObject.save()
                # https://stackoverflow.com/questions/15658399/django-assign-m2m-after-saving
        except Exception as e:
            print(e)
            import pdb;pdb.set_trace()

    def process_fldValue(self, fldValue, field):
        # import pdb;pdb.set_trace()
        if str(fldValue) == 'NotPassed':
            fldValue = None
        elif isinstance(field, (models.ForeignKey, models.OneToOneField)):
            fldValue = self.process_foreign_key_field(field, fldValue)
        elif isinstance(field, models.DateTimeField) and isinstance(fldValue, six.string_types):
            timezone = tz.gettz(settings.TIME_ZONE)
            fldValue = parse(str(fldValue))
            fldValue = fldValue.replace(tzinfo=fldValue.tzinfo or timezone)
            #if isinstance(fldValue, datetime.datetime):
            #    fldValue = make_aware(fldValue)
            # str(fldValue).split('.')[0], '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        return fldValue

    def process_field(self, field, params, entry, primary):
        newParams = self.excepted_params(params)
        if field.name in newParams:
            if hasattr(entry, field.name):
                # import pdb;pdb.set_trace()
                fldValue = getattr(entry, field.name)
            else:
                fldValue = getattr(entry, self.reversedFieldExceptions[field.name])
                if fldValue != 'NotPassed':
                    pdb.set_trace()
            return self.process_fldValue(fldValue, field)
        else:
            fld = str(field)
            if fld not in self.unknown_fields:
                self.unknown_fields[fld] = entry
            #pdb.set_trace()

    def process_fields(self, entry, action, queryset, fields, params, primary, m2m_fields, pkValue = None):
        try:
            #import pdb; pdb.set_trace()
            values = {}
            if pkValue:
                values[primary] = pkValue
                fields = [ x for x in fields if x.name != primary] #.pop(primary)
            for field in fields:
                fldValue = self.process_field(field, params, entry, primary)
                values[field.name] = fldValue
                #print((field.name, fldValue))
            #print(values)
            ups = self.upsert_record(self.actionClases[action], values, primary)
            for field in m2m_fields:
                fldValue = self.process_m2m_field(field, entry, ups)
            return ups
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
            #pdb.set_trace()

    def process_list_entries(self, entries, action, queryset, fields, primary, m2m_fields):
        params = dir(entries[0])
        result = []
        for entry in entries:
            result.append(self.process_fields(entry, action, queryset, fields, params, primary, m2m_fields))

    def process_dict_entries(self, entries, action, queryset, fields, primary, m2m_fields):
        #import pdb; pdb.set_trace()
        params = dir(six.next(six.itervalues(entries)))
        result = []
        for entry in entries:
            result.append(self.process_fields(entries[entry], action, queryset, fields, params, primary, m2m_fields, entry))

    def update_records(self, action, params=None):
        ''' updates the models from the objects'''
        # import pdb; pdb.set_trace()
        self.action = action
        if params:
            entries = getattr(self.client, action).list(**params)
        else:
            entries = getattr(self.client, action).list()
        if not entries:
            return
        # many to many fields should be handled differently
        all_fields = self.get_fields(self.actionClases[action])
        fields = [field for field in all_fields if not isinstance(field, (models.ManyToManyRel, models.ManyToManyField))]
        m2m_fields = [field for field in all_fields if isinstance(field, (models.ManyToManyRel, models.ManyToManyField))]
        primary = self.get_primary(fields)
        queryset = self.get_queryset(self.actionClases[action], primary)
        if isinstance(entries, list):
            res = self.process_list_entries(entries, action, queryset, fields, primary, m2m_fields)
        elif isinstance(entries, dict):
            res = self.process_dict_entries(entries, action, queryset, fields, primary, m2m_fields)
        #print(res)
        if self.unknown_fields:
            print('review_unknown')
            pprint.pprint(self.unknown_fields)
            #pdb.set_trace()
        return


def do_processing(actions, params=None):
    ''' performs the processing of the updates'''
    results = []
    processor = EntriesProcessor()
    if not params:
        params = [None] * len(actions)
    for action, param in zip(actions, params):
        print("processing_{}".format(action))
        results.append(processor.update_records(action, param))
    return results