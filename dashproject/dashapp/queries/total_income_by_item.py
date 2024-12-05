import pandas as pd
from django.db.models import Sum, F, FloatField
from dashapp.models import ItemHasOrder

from django.db.models import Sum, F, FloatField
from dashapp.models import ItemHasOrder

def get_total_income_by_item():
    data = ItemHasOrder.objects.values('item__id', 'item__name').annotate(
        total_income=Sum(F('quantity') * F('item__price'), output_field=FloatField())
    ).order_by('-total_income')
    return data