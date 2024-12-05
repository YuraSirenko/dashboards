from django.db.models import Sum, Count, Avg, F, FloatField
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
import pandas as pd

from dashapp.models import Order


def get_order_count_by_days():
    data = Order.objects.annotate(
        year=ExtractYear('event_started'),
        month=ExtractMonth('event_started'),
        day=ExtractDay('event_started')
    ).values('year', 'month', 'day').annotate(
        order_count=Count('id')
    ).order_by('year', 'month', 'day')
    return data


