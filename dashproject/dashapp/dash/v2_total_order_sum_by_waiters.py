from django.db.models import Sum
from django.shortcuts import render
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from django import forms
from dashapp.models import Order

class OrderSumFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        total_sums = kwargs.pop('total_sums', [0, 100])
        super().__init__(*args, **kwargs)
        min_sum = int(min(total_sums))
        max_sum = int(max(total_sums))
        extended_max_sum = max_sum * 2

        self.fields['min_sum'] = forms.IntegerField(
            label='Мінімальна сума замовлень',
            min_value=min_sum,
            max_value=extended_max_sum,
            initial=min_sum,
            required=False
        )
        self.fields['max_sum'] = forms.IntegerField(
            label='Максимальна сума замовлень',
            min_value=min_sum,
            max_value=extended_max_sum,
            initial=max_sum,
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
        df['waiter_name'] = df['waiters__first_name'] + ' ' + df['waiters__last_name']
        df['total_sum'] = df['total_sum'].astype(float)
        
        # Group by waiter_name and sum the total_sum
        df = df.groupby('waiter_name')['total_sum'].sum().reset_index()
        
        if sort_order == "asc":
            df = df.sort_values(by='total_sum', ascending=True)
        elif sort_order == "desc":
            df = df.sort_values(by='total_sum', ascending=False)
    return df

def calculate_statistics(df):
    if df.empty:
        return {'mean': 0, 'median': 0, 'min': 0, 'max': 0}
    return {
        'mean': df['total_sum'].mean(),
        'median': df['total_sum'].median(),
        'min': df['total_sum'].min(),
        'max': df['total_sum'].max()
    }

from bokeh.palettes import Category20c  # Add at top of file

def create_bokeh_pie_chart(df):
    if df.empty:
        return None, "<p>Немає даних для відображення.</p>"

    # Calculate angles for pie chart
    total = df['total_sum'].sum()
    df['angle'] = df['total_sum'] / total * 2 * np.pi
    df['percentage'] = df['total_sum'] / total * 100
    df['start_angle'] = df['angle'].cumsum().shift(1).fillna(0)
    df['end_angle'] = df['angle'].cumsum()
    
    # Create color palette
    num_colors_needed = len(df)
    colors = list(Category20c[20]) * (num_colors_needed // 20 + 1)  # Repeat colors if needed
    df['color'] = colors[:num_colors_needed]
    
    source = ColumnDataSource(df)

    p = figure(
        height=500, 
        width=500,
        title="Загальна сума замовлень по офіціантах",
        tools="hover",
        tooltips=[
            ('Офіціант', '@waiter_name'),
            ('Сума', '@total_sum{0,0.00}'),
            ('Відсоток', '@percentage{0.0}%')
        ],
        x_range=(-1.1, 1.1),
        y_range=(-1.1, 1.1)
    )

    p.wedge(
        x=0, y=0,
        radius=0.9,
        start_angle='start_angle',
        end_angle='end_angle',
        line_color="white",
        fill_color='color',  # Use color column instead of fixed color
        legend_field='waiter_name',
        source=source
    )

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    script, div = components(p)
    return script, div

def total_order_sum_by_waiters_view(request):
    # Get initial data with aggregation
    total_order_data = Order.objects.values(
        'waiters__first_name', 
        'waiters__last_name'
    ).annotate(
        total_sum=Sum('total_sum')
    ).distinct()
    
    df = prepare_dataframe(list(total_order_data), 'default')

    # Rest of the view remains the same
    if df.empty:
        total_sums = [0]
    else:
        total_sums = df['total_sum']
    
    form = OrderSumFilterForm(request.POST or None, total_sums=total_sums)

    if form.is_valid():
        min_sum = form.cleaned_data.get('min_sum') or df['total_sum'].min()
        max_sum = form.cleaned_data.get('max_sum') or (df['total_sum'].max() * 2)
        sort_order = form.cleaned_data.get('sort_order', 'default')
    else:
        min_sum = df['total_sum'].min() if not df.empty else 0
        max_sum = df['total_sum'].max() * 2 if not df.empty else 0
        sort_order = 'default'

    if not df.empty:
        df = df[(df['total_sum'] >= min_sum) & (df['total_sum'] <= max_sum)]
        if sort_order in ['asc', 'desc']:
            df = prepare_dataframe(df.to_dict('records'), sort_order)

    stats = calculate_statistics(df)
    script, div = create_bokeh_pie_chart(df)

    return render(request, 'bokeh_total_order_sum_by_waiters.html', {
        'script': script,
        'div': div,
        'form': form,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })