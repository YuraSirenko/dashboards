from django.db.models import Sum
from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go

from dashapp.models import Order
from dashapp.queries.total_order_sum_by_customers import get_total_order_sum_by_customers

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)

    if not df.empty:
        df['customer_name'] = df['customer__first_name'] + ' ' + df['customer__last_name']

        if sort_order == "asc":
            df = df.sort_values(by='total_sum', ascending=True).reset_index(drop=True)
        elif sort_order == "desc":
            df = df.sort_values(by='total_sum', ascending=False).reset_index(drop=True)

    return df

def calculate_statistics(df):
    if df.empty:
        return {
            'mean': 0,
            'median': 0,
            'min': 0,
            'max': 0
        }
    return {
        'mean': df['total_sum'].mean(),
        'median': df['total_sum'].median(),
        'min': df['total_sum'].min(),
        'max': df['total_sum'].max()
    }

def create_plotly_chart(df):
    if df.empty:
        return "<p>No data available for the chart.</p>"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['customer_name'],
            y=df['total_sum'],
            marker=dict(color="green"),
            name="Total Order Sum",
        )
    )

    fig.update_layout(
        title="Total Order Sum by Customers",
        xaxis=dict(title="Customer", tickangle=-45),
        yaxis=dict(title="Total Order Sum"),
        height=500,
        width=900,
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

from django.shortcuts import render
from django import forms
from django.db.models import Sum
import pandas as pd
import plotly.graph_objects as go
from dashapp.models import Order

class CustomerSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        customers = kwargs.pop('customers', [])
        super().__init__(*args, **kwargs)
        customer_choices = [('All', 'Всі Клієнти')] + [(c, c) for c in customers]
        self.fields['customer'] = forms.ChoiceField(
            choices=customer_choices,
            label="Обрати клієнта",
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

class OrderSumForm(forms.Form):
    def __init__(self, *args, **kwargs):
        total_sums = kwargs.pop('total_sums', [0, 100])
        super().__init__(*args, **kwargs)
        min_sum = int(min(total_sums))
        max_sum = int(max(total_sums))
        extended_max_sum = max_sum * 2  # Increase the max sum to 2x

        self.fields['min_sum'] = forms.IntegerField(
            label='Мінімальна сума замовлень',
            min_value=min_sum,
            max_value=extended_max_sum,  # Use the extended max sum
            initial=min_sum,
            required=False
        )
        self.fields['max_sum'] = forms.IntegerField(
            label='Максимальна сума замовлень',
            min_value=min_sum,
            max_value=extended_max_sum,  # Use the extended max sum
            initial=max_sum,  # You may choose to set initial to max_sum or extended_max_sum
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
        
def get_total_order_sum_by_customers():
    orders = Order.objects.values(
        'customer__first_name',
        'customer__last_name'
    ).annotate(total_sum=Sum('total_sum'))
    df = pd.DataFrame(list(orders))
    df['customer_name'] = df['customer__first_name'] + ' ' + df['customer__last_name']
    return df

def total_order_sum_by_customers(request):
    df = get_total_order_sum_by_customers()
    total_sums = df['total_sum']
    form = OrderSumForm(request.POST or None, total_sums=total_sums)

    if form.is_valid():
        min_sum = form.cleaned_data.get('min_sum') or total_sums.min()
        max_sum = form.cleaned_data.get('max_sum') or (total_sums.max() * 2)  # Use extended max sum
        sort_order = form.cleaned_data.get('sort_order', 'default')
    else:
        min_sum = total_sums.min()
        max_sum = total_sums.max() * 2  # Use extended max sum
        sort_order = 'default'

    # Filtering based on sum
    df = df[(df['total_sum'] >= min_sum) & (df['total_sum'] <= max_sum)]

    # Sorting
    if sort_order == 'asc':
        df = df.sort_values(by='total_sum', ascending=True).reset_index(drop=True)
    elif sort_order == 'desc':
        df = df.sort_values(by='total_sum', ascending=False).reset_index(drop=True)

    stats = {
        'mean': df['total_sum'].mean(),
        'median': df['total_sum'].median(),
        'min': df['total_sum'].min(),
        'max': df['total_sum'].max()
    }

    fig = go.Figure()
    if not df.empty:
        fig.add_trace(
            go.Bar(
                x=df['customer_name'],
                y=df['total_sum'],
                marker=dict(color="green"),
                name="Total Order Sum",
            )
        )
    else:
        fig.add_annotation(
            text="Немає даних для відображення",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )

    fig.update_layout(
        title="Загальна сума замовлень по клієнтах",
        xaxis=dict(title="Клієнт", tickangle=-45),
        yaxis=dict(title="Загальна сума замовлень"),
        template="plotly_white",
    )

    return render(request, 'plotly_total_order_sum_by_customers.html', {
        'plot': fig.to_html(full_html=False),
        'form': form,
        'data': df.to_dict(orient='records'),
        **stats,
    })