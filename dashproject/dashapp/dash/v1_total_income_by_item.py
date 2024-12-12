from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
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

def create_plotly_pie_chart(df):
    if df.empty:
        return "<p>Немає даних для відображення графіку.</p>"

    fig = go.Figure(
        data=[go.Pie(
            labels=df['item_name'],
            values=df['total_income'],
            hole=0.3,
            hoverinfo="label+percent",
            textinfo="label+percent"
        )]
    )

    fig.update_layout(
        title_text="Загальний дохід по товарах",
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

def total_income_by_item(request):
    total_income_data = get_total_income_by_item()
    data = list(total_income_data)
    df = prepare_dataframe(data, 'default')

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
    plot = create_plotly_pie_chart(df)

    return render(request, 'plotly_total_income_by_item.html', {
        'plot': plot,
        'form': form,
        'data': df.to_dict(orient='records'),
        **stats,
    })