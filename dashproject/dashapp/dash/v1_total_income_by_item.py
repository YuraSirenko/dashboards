from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
from dashapp.queries.total_income_by_item import get_total_income_by_item

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)

    if not df.empty:
        df['item_name'] = df['item__name']

        if sort_order == "asc":
            df = df.sort_values(by='total_income', ascending=True).reset_index(drop=True)
        elif sort_order == "desc":
            df = df.sort_values(by='total_income', ascending=False).reset_index(drop=True)

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
        'mean': df['total_income'].mean(),
        'median': df['total_income'].median(),
        'min': df['total_income'].min(),
        'max': df['total_income'].max()
    }

def create_plotly_chart(df):
    if df.empty:
        return "<p>No data available for the chart.</p>"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['item_name'],
            y=df['total_income'],
            marker=dict(color="blue"),
            name="Total Income",
        )
    )

    fig.update_layout(
        title="Total Income by Item",
        xaxis=dict(title="Item", tickangle=-45),
        yaxis=dict(title="Total Income"),
        height=500,
        width=900,
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

def total_income_by_item(request):
    sort_order = request.GET.get('sort', 'default')

    total_income_data = get_total_income_by_item()
    data = list(total_income_data)

    if sort_order == "default":
        df = pd.DataFrame(data)
        if not df.empty:
            df['item_name'] = df['item__name']
    else:
        df = prepare_dataframe(data, sort_order)

    stats = calculate_statistics(df)
    chart_html = create_plotly_chart(df)

    return render(request, 'plotly_total_income_by_item.html', {
        'chart_html': chart_html,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })