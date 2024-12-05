from django.db.models import Sum, Count, Avg, F, FloatField
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
import pandas as pd

from dashapp.models import WaiterHasOrder


def get_total_order_sum_by_waiters():
    data = WaiterHasOrder.objects.values('waiter__first_name', 'waiter__last_name').annotate(
        total_sum=Sum('order__total_sum')
    )
    return data