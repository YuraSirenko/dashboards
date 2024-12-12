from django.shortcuts import render
from django import forms
from django.db.models import Sum
from django.db.models.functions import ExtractYear, ExtractMonth
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from dashapp.models import Order

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
        self.fields['sort_order'] = forms.ChoiceField(
            choices=[
                ('default', 'За замовчуванням'),
                ('asc', 'Зростання'),
                ('desc', 'Спадання')
            ],
            label="Сортування",
            required=False
        )

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)
    if not df.empty:
        # Map month number to month name in Ukrainian
        month_mapping = {
            1: 'Січень', 2: 'Лютий', 3: 'Березень', 4: 'Квітень',
            5: 'Травень', 6: 'Червень', 7: 'Липень', 8: 'Серпень',
            9: 'Вересень', 10: 'Жовтень', 11: 'Листопад', 12: 'Грудень'
        }
        
        # Ensure month is integer and handle NaN values
        df['month'] = pd.to_numeric(df['month'], errors='coerce').fillna(0).astype(int)
        
        # Create month name and handle invalid months
        df['month_name'] = df['month'].map(lambda x: month_mapping.get(x, 'Невідомий'))
        
        # Convert total_sum to float and handle NaN
        df['total_sum'] = pd.to_numeric(df['total_sum'], errors='coerce').fillna(0)

        # Sort based on year and month
        if sort_order == "asc":
            df = df.sort_values(by=['year', 'month'], ascending=True)
        elif sort_order == "desc":
            df = df.sort_values(by=['year', 'month'], ascending=False)
        
        # Reset index after sorting
        df = df.reset_index(drop=True)
        
        # Drop rows with invalid months
        df = df[df['month'] > 0]

    return df

def create_bokeh_chart(df):
    if df.empty:
        return None, "<p>Немає даних для відображення.</p>"

    # Create valid month list for x_range
    valid_months = df['month_name'].dropna().unique().tolist()
    
    source = ColumnDataSource(df)
    p = figure(
        x_range=valid_months,  # Use clean month list
        title="Загальна сума замовлень по місяцях",
        x_axis_label="Місяць",
        y_axis_label="Загальна сума замовлень",
        width=900,
        height=500,
        tools="hover,pan,box_zoom,reset,save"
    )

    p.line('month_name', 'total_sum', source=source, line_width=2, color="blue", legend_label="Загальна сума")
    p.circle('month_name', 'total_sum', source=source, size=8, color="navy", alpha=0.5)

    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 1.2
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    script, div = components(p)
    return script, div

def calculate_statistics(df):
    if df.empty:
        return {'mean': 0, 'median': 0, 'min': 0, 'max': 0}
    return {
        'mean': df['total_sum'].mean(),
        'median': df['total_sum'].median(),
        'min': df['total_sum'].min(),
        'max': df['total_sum'].max()
    }


def get_total_order_sum_by_months(customer=None):
    orders = Order.objects.annotate(
        year=ExtractYear('event_started'),
        month=ExtractMonth('event_started')
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

    orders = orders.values('year', 'month').annotate(
        total_sum=Sum('total_sum')
    ).order_by('year', 'month')
    
    return orders

def total_order_sum_by_months_view(request):
    # Get customer filter form
    form = CustomerFilterForm(request.GET or None)
    customer_selected = None
    
    if form.is_valid():
        customer_selected = form.cleaned_data.get('customer')
        sort_order = form.cleaned_data.get('sort_order', 'default')
    else:
        sort_order = 'default'

    # Get data filtered by customer if selected
    total_order_data = get_total_order_sum_by_months(customer=customer_selected)
    data = list(total_order_data)
    
    # Prepare DataFrame and calculate statistics
    df = prepare_dataframe(data, sort_order)
    stats = calculate_statistics(df)
    
    # Create chart
    script, div = create_bokeh_chart(df)

    return render(request, 'bokeh_total_order_sum_by_months.html', {
        'script': script,
        'div': div,
        'form': form,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })