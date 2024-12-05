from django.db import models
from datetime import datetime

class Human(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45, null=True, blank=True)
    birth_date = models.DateField()
    phone = models.CharField(max_length=18)

    class Meta:
        abstract = True

class Customer(Human):
    sale = models.ForeignKey('Sale', models.DO_NOTHING, default=1)


    class Meta:
        db_table = 'customer'

class Waiter(Human):
    salary_type = models.ForeignKey('SalaryType', models.DO_NOTHING)
    hire_date = models.DateField()

    class Meta:
        db_table = 'waiter'

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    item_type = models.ForeignKey('ItemType',models.DO_NOTHING)
    quantity_in_stock = models.IntegerField(default=0)

    class Meta:
        db_table = 'item'

class ItemHasOrder(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Order', models.CASCADE)
    item = models.ForeignKey('Item', models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'item_has_order'
        unique_together = ('order', 'item')

class ItemType(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=45)

    class Meta:
        db_table = 'item_type'

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    table = models.ForeignKey('TableInRestaurant', models.DO_NOTHING)
    customer = models.ForeignKey('Customer', models.DO_NOTHING, blank=True, null=True)
    number_of_customers = models.IntegerField(default=1)
    total_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    event_started = models.DateTimeField(blank=True, null=True, default=datetime.now())
    payment_method = models.ForeignKey('PaymentMethod', models.DO_NOTHING, blank=True, null=True)
    event_ended = models.DateTimeField(blank=True, null=True)
    waiters = models.ManyToManyField('Waiter', through='WaiterHasOrder')
    items = models.ManyToManyField('Item', through='ItemHasOrder')

    class Meta:
        db_table = 'order'

class PaymentMethod(models.Model):
    id = models.AutoField(primary_key=True)
    payment_type = models.CharField(max_length=45)

    class Meta:
        db_table = 'payment_method'

class SalaryHistory(models.Model):
    id = models.AutoField(primary_key=True)
    waiter = models.ForeignKey('Waiter', models.DO_NOTHING)
    salary_type = models.ForeignKey('SalaryType', models.DO_NOTHING)
    date = models.DateField()
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'salary_history'

class SalaryType(models.Model):
    id = models.AutoField(primary_key=True)
    fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    percent = models.FloatField(default=0.00)

    class Meta:
        db_table = 'salary_type'

class Sale(models.Model):
    id = models.AutoField(primary_key=True)
    sale_type = models.CharField(max_length=45, blank=True, null=True)
    sale_percent = models.FloatField()

    class Meta:
        db_table = 'sale'

class TableInRestaurant(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    location = models.CharField(max_length=45, null=True)
    is_taken = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'table_in_restaurant'

class WaiterHasOrder(models.Model):
    id = models.AutoField(primary_key=True)
    waiter = models.ForeignKey('Waiter', models.CASCADE)
    order = models.ForeignKey('Order', models.CASCADE)

    class Meta:
        db_table = 'WaiterHasOrder'
        unique_together = ('order', 'waiter')