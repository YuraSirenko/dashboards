# Generated by Django 5.1.3 on 2024-12-04 21:42

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(blank=True, max_length=45, null=True)),
                ('birth_date', models.DateField()),
                ('phone', models.CharField(max_length=18)),
            ],
            options={
                'db_table': 'customer',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=45)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity_in_stock', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'item',
            },
        ),
        migrations.CreateModel(
            name='ItemType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type_name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'item_type',
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('payment_type', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'payment_method',
            },
        ),
        migrations.CreateModel(
            name='SalaryType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fixed', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('percent', models.FloatField(default=0.0)),
            ],
            options={
                'db_table': 'salary_type',
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sale_type', models.CharField(blank=True, max_length=45, null=True)),
                ('sale_percent', models.FloatField()),
            ],
            options={
                'db_table': 'sale',
            },
        ),
        migrations.CreateModel(
            name='TableInRestaurant',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('location', models.CharField(max_length=45, null=True)),
                ('is_taken', models.SmallIntegerField(default=0)),
            ],
            options={
                'db_table': 'table_in_restaurant',
            },
        ),
        migrations.CreateModel(
            name='ItemHasOrder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=1)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashapp.item')),
            ],
            options={
                'db_table': 'item_has_order',
            },
        ),
        migrations.AddField(
            model_name='item',
            name='item_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dashapp.itemtype'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('number_of_customers', models.IntegerField(default=1)),
                ('total_sum', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('event_started', models.DateTimeField(blank=True, default=datetime.datetime(2024, 12, 4, 23, 42, 14, 698943), null=True)),
                ('event_ended', models.DateTimeField(blank=True, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dashapp.customer')),
                ('items', models.ManyToManyField(through='dashapp.ItemHasOrder', to='dashapp.item')),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dashapp.paymentmethod')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dashapp.tableinrestaurant')),
            ],
            options={
                'db_table': 'order',
            },
        ),
        migrations.AddField(
            model_name='itemhasorder',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashapp.order'),
        ),
        migrations.AddField(
            model_name='customer',
            name='sale',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='dashapp.sale'),
        ),
        migrations.CreateModel(
            name='Waiter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(blank=True, max_length=45, null=True)),
                ('birth_date', models.DateField()),
                ('phone', models.CharField(max_length=18)),
                ('hire_date', models.DateField()),
                ('salary_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dashapp.salarytype')),
            ],
            options={
                'db_table': 'waiter',
            },
        ),
        migrations.CreateModel(
            name='SalaryHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('total_earned', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('salary_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dashapp.salarytype')),
                ('waiter', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dashapp.waiter')),
            ],
            options={
                'db_table': 'salary_history',
            },
        ),
        migrations.CreateModel(
            name='WaiterHasOrder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashapp.order')),
                ('waiter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashapp.waiter')),
            ],
            options={
                'db_table': 'WaiterHasOrder',
                'unique_together': {('order', 'waiter')},
            },
        ),
        migrations.AddField(
            model_name='order',
            name='waiters',
            field=models.ManyToManyField(through='dashapp.WaiterHasOrder', to='dashapp.waiter'),
        ),
        migrations.AlterUniqueTogether(
            name='itemhasorder',
            unique_together={('order', 'item')},
        ),
    ]
