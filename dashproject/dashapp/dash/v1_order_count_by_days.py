from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
from dashapp.queries.order_count_by_days import get_order_count_by_days

def prepare_dataframe(data):
    df = pd.DataFrame(data)
    if not df.empty:
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
        df = df.sort_values('date')
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

def create_plotly_line_chart(df):
    if df.empty:
        return "<p>No data available for the chart.</p>"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['order_count'],
            mode='lines+markers',
            line=dict(color='orange'),
            name='Order Count'
        )
    )

    fig.update_layout(
        title="Order Count by Days",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Number of Orders"),
        height=500,
        width=900,
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

def order_count_by_days(request):
    order_data = get_order_count_by_days()
    data = list(order_data)
    df = prepare_dataframe(data)
    stats = calculate_statistics(df)
    chart_html = create_plotly_line_chart(df)

    return render(request, 'plotly_order_count_by_days.html', {
        'chart_html': chart_html,
        'data_table': df.to_dict(orient='records'),
        'stats': stats
    })