from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
from dashapp.queries.total_items_sold_by_item import get_total_items_sold_by_item

def prepare_dataframe(data):
    df = pd.DataFrame(data)
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

def create_plotly_bar_chart(df):
    if df.empty:
        return "<p>No data available for the chart.</p>"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['item__name'],
            y=df['total_quantity'],
            marker=dict(color="purple"),
            name="Total Items Sold",
        )
    )

    fig.update_layout(
        title="Total Items Sold by Item",
        xaxis=dict(title="Item"),
        yaxis=dict(title="Quantity Sold"),
        height=500,
        width=900,
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

def total_items_sold_by_item(request):
    items_sold_data = get_total_items_sold_by_item()
    data = list(items_sold_data)
    df = prepare_dataframe(data)
    stats = calculate_statistics(df)
    chart_html = create_plotly_bar_chart(df)

    return render(request, 'plotly_total_items_sold_by_item.html', {
        'chart_html': chart_html,
        'data_table': df.to_dict(orient='records'),
        'stats': stats
    })