from django.shortcuts import render
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from django import forms
from dashapp.queries.total_income_by_item import get_total_income_by_item

class IncomeRangeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        total_incomes = kwargs.pop('total_incomes', [0, 100])
        super().__init__(*args, **kwargs)
        min_income = int(min(total_incomes))
        max_income = int(max(total_incomes))
        extended_max_income = max_income * 2

        self.fields['min_income'] = forms.IntegerField(
            label='Мінімальний дохід',
            min_value=min_income,
            max_value=extended_max_income,
            initial=min_income,
            required=False
        )
        self.fields['max_income'] = forms.IntegerField(
            label='Максимальний дохід',
            min_value=min_income,
            max_value=extended_max_income,
            initial=max_income,
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
        df['total_income'] = df['total_income'].astype(float)
        
        if sort_order == "asc":
            df = df.sort_values(by='total_income', ascending=True)
        elif sort_order == "desc":
            df = df.sort_values(by='total_income', ascending=False)
    return df

def calculate_statistics(df):
    if df.empty:
        return {'mean': 0, 'median': 0, 'min': 0, 'max': 0}
    return {
        'mean': df['total_income'].mean(),
        'median': df['total_income'].median(),
        'min': df['total_income'].min(),
        'max': df['total_income'].max()
    }

def create_bokeh_chart(df):
    if df.empty:
        return None, "<p>Немає даних для відображення.</p>"

    source = ColumnDataSource(df)
    p = figure(
        x_range=df['item_name'].tolist(),
        title="Загальний дохід по товарах",
        x_axis_label="Товар",
        y_axis_label="Загальний дохід",
        width=900,
        height=500,
        tools="hover,pan,box_zoom,reset,save"
    )

    p.vbar(
        x='item_name',
        top='total_income',
        width=0.9,
        source=source,
        color="teal",
        legend_label="Загальний дохід"
    )

    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 1.2
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    script, div = components(p)
    return script, div

def total_income_by_item_view(request):
    total_income_data = get_total_income_by_item()
    df = prepare_dataframe(list(total_income_data), 'default')
    
    if df.empty:
        total_incomes = [0]
    else:
        total_incomes = df['total_income']
    
    form = IncomeRangeForm(request.POST or None, total_incomes=total_incomes)

    if form.is_valid():
        min_income = form.cleaned_data.get('min_income') or df['total_income'].min()
        max_income = form.cleaned_data.get('max_income') or (df['total_income'].max() * 2)
        sort_order = form.cleaned_data.get('sort_order', 'default')
    else:
        if not df.empty:
            min_income = df['total_income'].min()
            max_income = df['total_income'].max() * 2
        else:
            min_income = 0
            max_income = 0
        sort_order = 'default'

    if not df.empty:
        df = df[(df['total_income'] >= min_income) & (df['total_income'] <= max_income)]
        if sort_order in ['asc', 'desc']:
            df = prepare_dataframe(df.to_dict('records'), sort_order)

    stats = calculate_statistics(df)
    script, div = create_bokeh_chart(df)

    return render(request, 'bokeh_total_income_by_item.html', {
        'script': script,
        'div': div,
        'form': form,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })