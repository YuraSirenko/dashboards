from django.shortcuts import render
from django import forms
import pandas as pd
import plotly.graph_objects as go
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

def calculate_statistics(df):
    if df.empty:
        return {'mean': 0, 'median': 0, 'min': 0, 'max': 0}
    return {
        'mean': df['total_quantity'].mean(),
        'median': df['total_quantity'].median(),
        'min': df['total_quantity'].min(),
        'max': df['total_quantity'].max()
    }

def create_plotly_chart(df):
    if df.empty:
        return "<p>Немає даних для відображення графіку.</p>"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['item_name'],
            y=df['total_quantity'],
            marker=dict(color="purple"),
            name="Кількість проданих товарів",
        )
    )

    fig.update_layout(
        title="Кількість проданих товарів",
        xaxis=dict(title="Товар", tickangle=-45),
        yaxis=dict(title="Кількість"),
        height=500,
        width=900,
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

def total_items_sold_by_item(request):
    items_sold_data = get_total_items_sold_by_item()
    df = prepare_dataframe(list(items_sold_data), 'default')
    
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
    plot = create_plotly_chart(df)

    return render(request, 'plotly_total_items_sold_by_item.html', {
        'plot': plot,
        'form': form,
        'data': df.to_dict(orient='records'),
        **stats,
    })