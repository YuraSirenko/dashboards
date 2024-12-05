from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
from dashapp.queries.total_order_sum_by_months import get_total_order_sum_by_months

def prepare_dataframe(data):
    df = pd.DataFrame(data)
    if not df.empty:
        df['month_year'] = df['year'].astype(str) + '-' + df['month'].astype(str)
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

def create_plotly_line_chart(df):
    if df.empty:
        return "<p>No data available for the chart.</p>"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df['month_year'],
            y=df['total_sum'],
            mode='lines+markers',
            line=dict(color='blue'),
            name='Total Order Sum'
        )
    )

    fig.update_layout(
        title="Total Order Sum by Months",
        xaxis=dict(title="Month", tickangle=-45),
        yaxis=dict(title="Total Order Sum"),
        height=500,
        width=900,
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

def total_order_sum_by_months(request):
    total_order_data = get_total_order_sum_by_months()
    data = list(total_order_data)
    df = prepare_dataframe(data)
    stats = calculate_statistics(df)
    chart_html = create_plotly_line_chart(df)

    return render(request, 'plotly_total_order_sum_by_months.html', {
        'chart_html': chart_html,
        'data_table': df.to_dict(orient='records'),
        'stats': stats
    })