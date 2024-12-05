from django.contrib import admin
from .models import Customer, Waiter, Item, ItemHasOrder, ItemType, Order, PaymentMethod, SalaryHistory, SalaryType, Sale, TableInRestaurant, WaiterHasOrder

admin.site.register(Customer)
admin.site.register(Waiter)
admin.site.register(Item)
admin.site.register(ItemHasOrder)
admin.site.register(ItemType)
admin.site.register(Order)
admin.site.register(PaymentMethod)
admin.site.register(SalaryHistory)
admin.site.register(SalaryType)
admin.site.register(Sale)
admin.site.register(TableInRestaurant)
admin.site.register(WaiterHasOrder)