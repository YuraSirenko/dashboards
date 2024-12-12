from django import forms

class RangeFilterForm(forms.Form):
    def __init__(self, *args, field_name="value", min_val=0, max_val=100, **kwargs):
        super().__init__(*args, **kwargs)
        extended_max = max_val * 2

        self.fields[f'min_{field_name}'] = forms.IntegerField(
            label=f'Мінімальне значення',
            min_value=min_val,
            max_value=extended_max,
            initial=min_val,
            required=False
        )
        self.fields[f'max_{field_name}'] = forms.IntegerField(
            label=f'Максимальне значення',
            min_value=min_val,
            max_value=extended_max,
            initial=max_val,
            required=False
        )
        self.fields['sort_order'] = forms.ChoiceField(
            choices=[
                ('default', 'За замовчуванням'),
                ('asc', 'Зростання'),
                ('desc', 'Спадання')
            ],
            label="Сортування",
            required=False
        )

class CustomerFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        customers = Order.objects.values('customer__first_name', 'customer__last_name').distinct()
        customer_choices = [("", "Всі клієнти")]
        for c in customers:
            full_name = f"{c['customer__first_name']} {c['customer__last_name']}"
            customer_choices.append((full_name, full_name))
        self.fields['customer'] = forms.ChoiceField(
            choices=customer_choices,
            label="Вибрати клієнта",
            required=False
        )