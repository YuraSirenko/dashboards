from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
from dashapp.queries.total_order_sum_by_waiters import get_total_order_sum_by_waiters

def prepare_dataframe(data):
    df = pd.DataFrame(data)
    if not df.empty:
        df['waiter_name'] = df['waiter__first_name'] + ' ' + df['waiter__last_name']
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

def create_plotly_pie_chart(df):
    if df.empty:
        return "<p>No data available for the chart.</p>"

    fig = go.Figure(
        data=[go.Pie(
            labels=df['waiter_name'],
            values=df['total_sum'],
            hole=0.3
        )]
    )

    fig.update_layout(
        title_text="Total Order Sum by Waiters",
        height=500,
        width=900
    )

    return fig.to_html(full_html=False)

def total_order_sum_by_waiters(request):
    total_order_data = get_total_order_sum_by_waiters()
    data = list(total_order_data)
    df = prepare_dataframe(data)
    stats = calculate_statistics(df)
    chart_html = create_plotly_pie_chart(df)

    return render(request, 'plotly_total_order_sum_by_waiters.html', {
        'chart_html': chart_html,
        'data_table': df.to_dict(orient='records'),
        'stats': stats
    })