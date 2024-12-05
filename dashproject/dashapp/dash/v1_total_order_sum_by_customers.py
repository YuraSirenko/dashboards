from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
from dashapp.queries.total_order_sum_by_customers import get_total_order_sum_by_customers

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)

    if not df.empty:
        df['customer_name'] = df['customer__first_name'] + ' ' + df['customer__last_name']

        if sort_order == "asc":
            df = df.sort_values(by='total_sum', ascending=True).reset_index(drop=True)
        elif sort_order == "desc":
            df = df.sort_values(by='total_sum', ascending=False).reset_index(drop=True)

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
        'mean': df['total_sum'].mean(),
        'median': df['total_sum'].median(),
        'min': df['total_sum'].min(),
        'max': df['total_sum'].max()
    }

def create_plotly_chart(df):
    if df.empty:
        return "<p>No data available for the chart.</p>"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['customer_name'],
            y=df['total_sum'],
            marker=dict(color="green"),
            name="Total Order Sum",
        )
    )

    fig.update_layout(
        title="Total Order Sum by Customers",
        xaxis=dict(title="Customer", tickangle=-45),
        yaxis=dict(title="Total Order Sum"),
        height=500,
        width=900,
        template="plotly_white",
    )

    return fig.to_html(full_html=False)

def total_order_sum_by_customers(request):
    sort_order = request.GET.get('sort', 'default')

    total_order_data = get_total_order_sum_by_customers()
    data = list(total_order_data)

    if sort_order == "default":
        df = pd.DataFrame(data)
        if not df.empty:
            df['customer_name'] = df['customer__first_name'] + ' ' + df['customer__last_name']
    else:
        df = prepare_dataframe(data, sort_order)

    stats = calculate_statistics(df)
    chart_html = create_plotly_chart(df)

    return render(request, 'plotly_total_order_sum_by_customers.html', {
        'chart_html': chart_html,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })