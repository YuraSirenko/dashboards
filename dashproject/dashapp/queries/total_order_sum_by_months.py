from django.db.models import Sum, Count, Avg, F, FloatField
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
import pandas as pd

from dashapp.models import Order


def get_total_order_sum_by_months():
    data = Order.objects.annotate(
        year=ExtractYear('event_started'),
        month=ExtractMonth('event_started')
    ).values('year', 'month').annotate(
        total_sum=Sum('total_sum')
    ).order_by('year', 'month')
    return data

