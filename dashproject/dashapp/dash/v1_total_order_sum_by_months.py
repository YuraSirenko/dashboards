from django.shortcuts import render
from django import forms
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import pandas as pd
import plotly.graph_objects as go
from dashapp.models import Order

class CustomerFilterForm(forms.Form):
    customer = forms.ChoiceField(
        choices=[],
        label="Вибрати клієнта",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate customer choices dynamically
        customers = Order.objects.values('customer__first_name', 'customer__last_name').distinct()
        customer_choices = [("", "Всі клієнти")]  # Default option for all customers
        for c in customers:
            full_name = f"{c['customer__first_name']} {c['customer__last_name']}"
            customer_choices.append((full_name, full_name))
        self.fields['customer'].choices = customer_choices

def calculate_statistics(df):
    if df.empty:
        return {'mean': 0, 'median': 0, 'min': 0, 'max': 0}
    return {
        'mean': df['total_sum'].mean(),
        'median': df['total_sum'].median(),
        'min': df['total_sum'].min(),
        'max': df['total_sum'].max()
    }

def create_plotly_bar_chart(df):
    if df.empty:
        return "<p>Немає даних для відображення графіку.</p>"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['month_name'],
            y=df['total_sum'],
            marker=dict(color="green"),
            name="Загальна сума замовлень",
        )
    )

    fig.update_layout(
        title="Загальна сума замовлень по місяцях",
        xaxis=dict(title="Місяць"),
        yaxis=dict(title="Загальна сума замовлень"),
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

def get_total_order_sum_by_months(customer=None):
    orders = Order.objects.annotate(month=ExtractMonth('event_started'))
    if customer:
        try:
            first_name, last_name = customer.split(' ', 1)
            orders = orders.filter(customer__first_name=first_name, customer__last_name=last_name)
        except ValueError:
            orders = orders.none()
    orders = orders.values('month').annotate(total_sum=Sum('total_sum')).order_by('month')
    df = pd.DataFrame(list(orders))
    if not df.empty:
        # Map month number to month name
        month_mapping = {
            1: 'Січень', 2: 'Лютий', 3: 'Березень', 4: 'Квітень',
            5: 'Травень', 6: 'Червень', 7: 'Липень', 8: 'Серпень',
            9: 'Вересень', 10: 'Жовтень', 11: 'Листопад', 12: 'Грудень'
        }
        df['month_name'] = df['month'].map(month_mapping)
    return df

def total_order_sum_by_months(request):
    form = CustomerFilterForm(request.GET or None)
    customer_selected = None
    if form.is_valid():
        customer_selected = form.cleaned_data.get('customer')
    
    df = get_total_order_sum_by_months(customer=customer_selected)
    stats = calculate_statistics(df)
    chart_html = create_plotly_bar_chart(df)

    return render(request, 'plotly_total_order_sum_by_months.html', {
        'plot': chart_html,
        'form': form,
        'data': df.to_dict(orient='records'),
        **stats,
    })