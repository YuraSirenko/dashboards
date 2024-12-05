import pandas as pd
from django.db.models import Sum
from dashapp.models import Order

def get_total_order_sum_by_customers():
    data = Order.objects.values('customer__first_name', 'customer__last_name').annotate(
        total_sum=Sum('total_sum')
    )
    return data