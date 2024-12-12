from django.shortcuts import render
from django import forms
from django.db.models import Count
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from dashapp.models import Order

from django.shortcuts import render
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource

def total_order_count_by_days_view(request):  # Changed from order_count_by_days_view
    form = CustomerFilterForm(request.GET or None)
    customer_selected = None
    
    if form.is_valid():
        customer_selected = form.cleaned_data.get('customer')
    
    order_data = get_order_count_by_days(customer=customer_selected)
    df = prepare_dataframe(list(order_data), 'default')
    
    stats = calculate_statistics(df)
    script, div = create_bokeh_chart(df)

    return render(request, 'bokeh_order_count_by_days.html', {
        'script': script,
        'div': div,
        'form': form,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
    })

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

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)
    if not df.empty:
        # Create date column from year, month, day
        df['date'] = pd.to_datetime({
            'year': df['year'],
            'month': df['month'],
            'day': df['day']
        })
        
        # Drop any NaT values and sort
        df = df.dropna(subset=['date'])
        
        if sort_order == "asc":
            df = df.sort_values(by='date', ascending=True)
        elif sort_order == "desc":
            df = df.sort_values(by='date', ascending=False)
        else:
            df = df.sort_values(by='date', ascending=True)
            
        df = df.reset_index(drop=True)
    return df

def calculate_statistics(df):
    if df.empty:
        return {'mean': 0, 'median': 0, 'min': 0, 'max': 0}
    return {
        'mean': df['order_count'].mean(),
        'median': df['order_count'].median(),
        'min': df['order_count'].min(),
        'max': df['order_count'].max()
    }

def create_bokeh_chart(df):
    if df.empty:
        return None, "<p>Немає даних для відображення.</p>"

    source = ColumnDataSource(df)
    p = figure(
        x_axis_type='datetime',
        title="Кількість замовлень по днях",
        x_axis_label="Дата",
        y_axis_label="Кількість замовлень",
        width=900,
        height=500,
        tools="hover,pan,box_zoom,reset,save"
    )

    p.line('date', 'order_count', source=source, line_width=2, color="blue", legend_label="Кількість замовлень")
    p.circle('date', 'order_count', source=source, size=8, color="navy", alpha=0.5)

    p.xgrid.grid_line_color = None
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    script, div = components(p)
    return script, div

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
    
    return orders

def order_count_by_days_view(request):
    form = CustomerFilterForm(request.GET or None)
    customer_selected = None
    
    if form.is_valid():
        customer_selected = form.cleaned_data.get('customer')
    
    order_data = get_order_count_by_days(customer=customer_selected)
    df = prepare_dataframe(list(order_data), 'default')
    
    stats = calculate_statistics(df)
    script, div = create_bokeh_chart(df)

    return render(request, 'bokeh_order_count_by_days.html', {
        'script': script,
        'div': div,
        'form': form,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
    })