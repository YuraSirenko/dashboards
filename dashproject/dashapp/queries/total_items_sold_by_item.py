from django.db.models import Sum, Count, Avg, F, FloatField
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
import pandas as pd

from dashapp.models import ItemHasOrder


def get_total_items_sold_by_item():
    data = ItemHasOrder.objects.values('item__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')
    return data

