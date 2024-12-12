from django.shortcuts import render
from django import forms
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from dashapp.queries.total_items_sold_by_item import get_total_items_sold_by_item

class QuantityRangeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        total_quantities = kwargs.pop('total_quantities', [0, 100])
        super().__init__(*args, **kwargs)
        min_qty = int(min(total_quantities))
        max_qty = int(max(total_quantities))
        extended_max_qty = max_qty * 2

        self.fields['min_quantity'] = forms.IntegerField(
            label='Мінімальна кількість',
            min_value=min_qty,
            max_value=extended_max_qty,
            initial=min_qty,
            required=False
        )
        self.fields['max_quantity'] = forms.IntegerField(
            label='Максимальна кількість',
            min_value=min_qty,
            max_value=extended_max_qty,
            initial=max_qty,
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
def calculate_statistics(df):
    if df.empty:
        return {
            'mean': 0,
            'median': 0,
            'min': 0,
            'max': 0
        }
    return {
        'mean': df['total_quantity'].mean(),
        'median': df['total_quantity'].median(),
        'min': df['total_quantity'].min(),
        'max': df['total_quantity'].max()
    }

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)
    if not df.empty:
        df['item_name'] = df['item__name']
        df['total_quantity'] = df['total_quantity'].astype(float)
        
        if sort_order == "asc":
            df = df.sort_values(by='total_quantity', ascending=True)
        elif sort_order == "desc":
            df = df.sort_values(by='total_quantity', ascending=False)
    return df

def create_bokeh_chart(df):
    if df.empty:
        return None, "<p>Немає даних для відображення.</p>"

    source = ColumnDataSource(df)
    p = figure(
        x_range=df['item_name'].tolist(),
        title="Кількість проданих товарів",
        x_axis_label="Товар",
        y_axis_label="Кількість",
        width=900,
        height=500,
        tools="hover,pan,box_zoom,reset,save"
    )

    p.vbar(
        x='item_name',
        top='total_quantity',
        width=0.9,
        source=source,
        color="purple",
        legend_label="Кількість проданих товарів"
    )

    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 1.2
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    script, div = components(p)
    return script, div

def total_items_sold_view(request):
    total_items_data = get_total_items_sold_by_item()
    df = prepare_dataframe(list(total_items_data), 'default')
    
    if df.empty:
        total_quantities = [0]
    else:
        total_quantities = df['total_quantity']
    
    form = QuantityRangeForm(request.POST or None, total_quantities=total_quantities)

    if form.is_valid():
        min_qty = form.cleaned_data.get('min_quantity') or df['total_quantity'].min()
        max_qty = form.cleaned_data.get('max_quantity') or (df['total_quantity'].max() * 2)
        sort_order = form.cleaned_data.get('sort_order', 'default')
    else:
        if not df.empty:
            min_qty = df['total_quantity'].min()
            max_qty = df['total_quantity'].max() * 2
        else:
            min_qty = 0
            max_qty = 0
        sort_order = 'default'

    if not df.empty:
        df = df[(df['total_quantity'] >= min_qty) & (df['total_quantity'] <= max_qty)]
        if sort_order in ['asc', 'desc']:
            df = prepare_dataframe(df.to_dict('records'), sort_order)

    stats = calculate_statistics(df)
    script, div = create_bokeh_chart(df)

    return render(request, 'bokeh_total_items_sold_by_item.html', {
        'script': script,
        'div': div,
        'form': form,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })