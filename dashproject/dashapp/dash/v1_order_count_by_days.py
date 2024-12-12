from django.shortcuts import render
from django import forms
from django.db.models import Count
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
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
        customers = Order.objects.values('customer__first_name', 'customer__last_name').distinct()
        customer_choices = [("", "Всі клієнти")]
        for c in customers:
            full_name = f"{c['customer__first_name']} {c['customer__last_name']}"
            customer_choices.append((full_name, full_name))
        self.fields['customer'].choices = customer_choices

def calculate_statistics(df):
    if df.empty:
        return {'mean': 0, 'median': 0, 'min': 0, 'max': 0}
    return {
        'mean': df['order_count'].mean(),
        'median': df['order_count'].median(),
        'min': df['order_count'].min(),
        'max': df['order_count'].max()
    }

def create_plotly_line_chart(df):
    if df.empty:
        return "<p>Немає даних для відображення графіку.</p>"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['order_count'],
            mode='lines+markers',
            line=dict(color='orange'),
            name='Кількість замовлень'
        )
    )

    fig.update_layout(
        title="Кількість замовлень по днях",
        xaxis=dict(title="Дата"),
        yaxis=dict(title="Кількість замовлень"),
        height=500,
        width=900,
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

def get_order_count_by_days(customer=None):
    orders = Order.objects.annotate(
        year=ExtractYear('event_started'),
        month=ExtractMonth('event_started'),
        day=ExtractDay('event_started')
    )
    
    if customer:
        try:
            first_name, last_name = customer.split(' ', 1)
            orders = orders.filter(
                customer__first_name=first_name,
                customer__last_name=last_name
            )
        except ValueError:
            orders = orders.none()

    orders = orders.values('year', 'month', 'day').annotate(
        order_count=Count('id')
    ).order_by('year', 'month', 'day')
    
    df = pd.DataFrame(list(orders))
    if not df.empty:
        # Drop rows with missing date components
        df = df.dropna(subset=['year', 'month', 'day'])
        
        # Ensure date components are integers
        df['year'] = df['year'].astype(int)
        df['month'] = df['month'].astype(int)
        df['day'] = df['day'].astype(int)
        
        # Create date column safely
        try:
            df['date'] = pd.to_datetime({
                'year': df['year'],
                'month': df['month'],
                'day': df['day']
            })
            # Remove any resulting NaT values
            df = df.dropna(subset=['date'])
            df = df.sort_values('date')
        except (ValueError, TypeError):
            # If date conversion fails, return empty DataFrame
            return pd.DataFrame()
    
    return df
def order_count_by_days(request):
    form = CustomerFilterForm(request.GET or None)
    customer_selected = None
    
    if form.is_valid():
        customer_selected = form.cleaned_data.get('customer')
    
    df = get_order_count_by_days(customer=customer_selected)
    stats = calculate_statistics(df)
    chart_html = create_plotly_line_chart(df)

    return render(request, 'plotly_order_count_by_days.html', {
        'plot': chart_html,
        'form': form,
        'data': df.to_dict(orient='records'),
        **stats,
    })