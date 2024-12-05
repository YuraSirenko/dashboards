from django.contrib import admin
from django.urls import path

from dashapp.dash.v1_total_income_by_item import total_income_by_item
from dashapp.dash.v1_total_items_sold_by_item import total_items_sold_by_item
from dashapp.dash.v1_total_order_sum_by_customers import total_order_sum_by_customers
from dashapp.dash.v1_total_order_sum_by_waiters import total_order_sum_by_waiters
from dashapp.dash.v1_total_order_sum_by_months import total_order_sum_by_months
from dashapp.dash.v1_order_count_by_days import order_count_by_days
from dashapp.dash.v2_order_count_by_days import total_order_count_by_days_view
from dashapp.dash.v2_total_income_by_item import total_income_by_item_view
from dashapp.dash.v2_total_items_sold_by_item import total_items_sold_view

from dashapp.dash.v2_total_order_sum_by_customers import total_order_sum_by_customers_view
from dashapp.dash.v2_total_order_sum_by_months import total_order_sum_by_months_view
from dashapp.dash.v2_total_order_sum_by_waiters import total_order_sum_by_waiters_view
from dashapp.perfomance_test import performance_chart
from dashapp.views import home
from dashapp.views import dashboard_v1, dashboard_v2

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home, name='home'),
    path('performance-chart/', performance_chart, name='performance_chart'),

    path('v1/dashboard/', dashboard_v1, name='dashboard_v1'),
    path('v2/dashboard/', dashboard_v2, name='dashboard_v2'),


    path('v1/total-order-sum-by-customers/', total_order_sum_by_customers, name='total_order_sum_by_customers'),
    path('v1/total-order-sum-by-waiters/', total_order_sum_by_waiters, name='total_order_sum_by_waiters'),
    path('v1/total-order-sum-by-months/', total_order_sum_by_months, name='total_order_sum_by_months'),
    path('v1/order-count-by-days/', order_count_by_days, name='order_count_by_days'),
    path('v1/total-items-sold-by-item/', total_items_sold_by_item, name='total_items_sold_by_item'),
    path('v1/total-income-by-item/', total_income_by_item, name='total_income_by_item'),
    path('v2/total-order-sum-by-customers/', total_order_sum_by_customers_view, name='total_order_sum_by_customers'),
    path('v2/total-order-sum-by-waiters/', total_order_sum_by_waiters_view, name='total_order_sum_by_waiters'),
    path('v2/total-order-sum-by-months/', total_order_sum_by_months_view, name='total_order_sum_by_months'),
    path('v2/order-count-by-days/', total_order_count_by_days_view, name='order_count_by_days'),
    path('v2/total-items-sold-by-item/', total_items_sold_view, name='total_items_sold_by_item'),
    path('v2/total-income-by-item/', total_income_by_item_view, name='total_income_by_item'),
]