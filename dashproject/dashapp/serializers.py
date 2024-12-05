from rest_framework import serializers
from .models import Customer, Item, ItemHasOrder, ItemType, Order, PaymentMethod, SalaryHistory, SalaryType, Sale, TableInRestaurant, Waiter, WaiterHasOrder

class CustomerSerializer(serializers.ModelSerializer):
    sale = serializers.PrimaryKeyRelatedField(queryset=Sale.objects.all())

    class Meta:
        model = Customer
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    item_type = serializers.PrimaryKeyRelatedField(queryset=ItemType.objects.all())

    class Meta:
        model = Item
        fields = '__all__'

class ItemHasOrderSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    class Meta:
        model = ItemHasOrder
        fields = '__all__'

class ItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemType
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    table = serializers.PrimaryKeyRelatedField(queryset=TableInRestaurant.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    payment_method = serializers.PrimaryKeyRelatedField(queryset=PaymentMethod.objects.all())
    waiters = serializers.PrimaryKeyRelatedField(queryset=Waiter.objects.all(), many=True)
    items = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), many=True)

    class Meta:
        model = Order
        fields = '__all__'

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

class SalaryHistorySerializer(serializers.ModelSerializer):
    waiter = serializers.PrimaryKeyRelatedField(queryset=Waiter.objects.all())
    salary_type = serializers.PrimaryKeyRelatedField(queryset=SalaryType.objects.all())

    class Meta:
        model = SalaryHistory
        fields = '__all__'

class SalaryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryType
        fields = '__all__'

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'

class TableInRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableInRestaurant
        fields = '__all__'

class WaiterSerializer(serializers.ModelSerializer):
    salary_type = serializers.PrimaryKeyRelatedField(queryset=SalaryType.objects.all())

    class Meta:
        model = Waiter
        fields = '__all__'

class WaiterHasOrderSerializer(serializers.ModelSerializer):
    waiter = serializers.PrimaryKeyRelatedField(queryset=Waiter.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = WaiterHasOrder
        fields = '__all__'