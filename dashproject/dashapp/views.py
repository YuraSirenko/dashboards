
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')


from django.shortcuts import render
from .perfomance_test import simulate_database_query, measure_performance
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

# Import your custom query functions
from dashapp.queries.total_order_sum_by_customers import get_total_order_sum_by_customers
from dashapp.queries.total_order_sum_by_waiters import get_total_order_sum_by_waiters
from dashapp.queries.total_income_by_item import get_total_income_by_item
from dashapp.queries.total_items_sold_by_item import get_total_items_sold_by_item
from dashapp.queries.order_count_by_days import get_order_count_by_days
from dashapp.queries.total_order_sum_by_months import get_total_order_sum_by_months

def create_bar_chart(x, y, title, x_title, y_title, color='blue'):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x,
            y=y,
            marker=dict(color=color),
            name=title
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=False
    )
    return plot(fig, output_type='div', include_plotlyjs=False)

def create_scatter_chart(x, y, title, x_title, y_title, color='green'):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines+markers',
            name='Execution Time',
            line=dict(color=color)
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=True
    )
    return plot(fig, output_type='div', include_plotlyjs=False)


def dashboard_v1(request):
    version = 'v1'
    graphs = []

    # === Chart 1: Total Order Sum by Customers (v1) ===
    total_order_customers = get_total_order_sum_by_customers()
    df1 = pd.DataFrame(total_order_customers)

    # Combine first and last names into 'customer_name'
    if not df1.empty:
        df1['customer_name'] = df1['customer__first_name'] + ' ' + df1['customer__last_name']

    try:
        fig1_html = create_bar_chart(
            x=df1['customer_name'].tolist(),
            y=df1['total_sum'].tolist(),
            title='Total Order Sum by Customers (v1)',
            x_title='Customer',
            y_title='Total Order Sum',
            color='teal'
        )
        graphs.append(fig1_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 1")
        graphs.append(f"<p>Error: Missing column {e} in Chart 1 data.</p>")

    # === Chart 2: Fix waiter_name error ===
    total_order_waiters = get_total_order_sum_by_waiters()
    df2 = pd.DataFrame(total_order_waiters)
    if not df2.empty:
        # Add waiter_name column by combining first and last names
        df2['waiter_name'] = df2['waiter__first_name'] + ' ' + df2['waiter__last_name']
        df2['total_order_sum'] = df2['total_sum']  # Match column name with query result
    try:
        fig2_html = create_bar_chart(
            x=df2['waiter_name'].tolist(),
            y=df2['total_order_sum'].tolist(),
            title='Total Order Sum by Waiters (v1)',
            x_title='Waiter', 
            y_title='Total Order Sum',
            color='orange'
        )
        graphs.append(fig2_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 2")
        graphs.append(f"<p>Error: Missing column {e} in Chart 2 data.</p>")

    # === Chart 3: Fix item_name error ===
    total_income_item = get_total_income_by_item()
    df3 = pd.DataFrame(total_income_item)
    if not df3.empty:
        df3['item_name'] = df3['item__name']  # Match column name from query
    try:
        fig3_html = create_bar_chart(
            x=df3['item_name'].tolist(),
            y=df3['total_income'].tolist(),
            title='Total Income by Item (v1)',
            x_title='Item',
            y_title='Total Income', 
            color='purple'
        )
        graphs.append(fig3_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 3")
        graphs.append(f"<p>Error: Missing column {e} in Chart 3 data.</p>")

    # === Chart 4: Fix item_name error ===
    total_items_sold = get_total_items_sold_by_item() 
    df4 = pd.DataFrame(total_items_sold)
    if not df4.empty:
        df4['item_name'] = df4['item__name']  # Match column name from query
    try:
        fig4_html = create_bar_chart(
            x=df4['item_name'].tolist(),
            y=df4['total_quantity'].tolist(),
            title='Total Items Sold by Item (v1)',
            x_title='Item',
            y_title='Quantity Sold',
            color='green'
        )
        graphs.append(fig4_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 4")
        graphs.append(f"<p>Error: Missing column {e} in Chart 4 data.</p>")

    # === Chart 5: Order Count by Days (v1) ===
    order_count_days = get_order_count_by_days()
    df5 = pd.DataFrame(order_count_days)
    try:
        fig5_html = create_scatter_chart(
            x=df5['day'].tolist(),
            y=df5['order_count'].tolist(),
            title='Order Count by Days (v1)',
            x_title='Day',
            y_title='Number of Orders',
            color='red'
        )
        graphs.append(fig5_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 5")
        graphs.append(f"<p>Error: Missing column {e} in Chart 5 data.</p>")

    # === Chart 6: Fix total_order_sum error === 
    total_order_months = get_total_order_sum_by_months()
    df6 = pd.DataFrame(total_order_months)
    if not df6.empty:
        df6['total_order_sum'] = df6['total_sum']  # Match column name from query
    try:
        fig6_html = create_bar_chart(
            x=df6['month'].tolist(),
            y=df6['total_order_sum'].tolist(),
            title='Total Order Sum by Months (v1)',
            x_title='Month',
            y_title='Total Order Sum',
            color='blue'
        )
        graphs.append(fig6_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 6")
        graphs.append(f"<p>Error: Missing column {e} in Chart 6 data.</p>")

    # === Chart 7: Performance Chart ===
    # This chart measures the performance of thread execution
    performance_queries = [simulate_database_query for _ in range(33)]
    performance_results = measure_performance(performance_queries, mode='thread')
    df7 = pd.DataFrame(performance_results)
    if not df7.empty:
        try:
            fig7_html = create_scatter_chart(
                x=df7['parameter'].tolist(),
                y=df7['execution_time'].tolist(),
                title='Thread Pool Performance Analysis (v1)',
                x_title='Number of Threads',
                y_title='Execution Time (s)',
                color='black'
            )
            graphs.append(fig7_html)
        except KeyError as e:
            print(f"KeyError: {e} in Chart 7")
            graphs.append(f"<p>Error: Missing column {e} in Chart 7 data.</p>")
    else:
        graphs.append("<p>No performance data available.</p>")

    return render(request, 'dashboard.html', {'graphs': graphs, 'version': version})

def dashboard_v2(request):
    version = 'v2'
    graphs = []

    # === Chart 1: Total Order Sum by Customers (v2) ===
    total_order_customers = get_total_order_sum_by_customers()
    df1 = pd.DataFrame(total_order_customers)
    if not df1.empty:
        df1['customer_name'] = df1['customer__first_name'] + ' ' + df1['customer__last_name']
    try:
        fig1_html = create_bar_chart(
            x=df1['customer_name'].tolist(),
            y=df1['total_sum'].tolist(),
            title='Total Order Sum by Customers (v2)',
            x_title='Customer',
            y_title='Total Order Sum',
            color='teal'
        )
        graphs.append(fig1_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 1")
        graphs.append(f"<p>Error: Missing column {e} in Chart 1 data.</p>")

    # === Chart 2: Total Order Sum by Waiters (v2) ===
    total_order_waiters = get_total_order_sum_by_waiters()
    df2 = pd.DataFrame(total_order_waiters)
    if not df2.empty:
        df2['waiter_name'] = df2['waiter__first_name'] + ' ' + df2['waiter__last_name']
        df2['total_order_sum'] = df2['total_sum']
    try:
        fig2_html = create_bar_chart(
            x=df2['waiter_name'].tolist(),
            y=df2['total_order_sum'].tolist(),
            title='Total Order Sum by Waiters (v2)',
            x_title='Waiter',
            y_title='Total Order Sum',
            color='orange'
        )
        graphs.append(fig2_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 2")
        graphs.append(f"<p>Error: Missing column {e} in Chart 2 data.</p>")

    # === Chart 3: Total Income by Item (v2) ===
    total_income_item = get_total_income_by_item()
    df3 = pd.DataFrame(total_income_item)
    if not df3.empty:
        df3['item_name'] = df3['item__name']
    try:
        fig3_html = create_bar_chart(
            x=df3['item_name'].tolist(),
            y=df3['total_income'].tolist(),
            title='Total Income by Item (v2)',
            x_title='Item',
            y_title='Total Income',
            color='purple'
        )
        graphs.append(fig3_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 3")
        graphs.append(f"<p>Error: Missing column {e} in Chart 3 data.</p>")

    # === Chart 4: Total Items Sold by Item (v2) ===
    total_items_sold = get_total_items_sold_by_item()
    df4 = pd.DataFrame(total_items_sold)
    if not df4.empty:
        df4['item_name'] = df4['item__name']
    try:
        fig4_html = create_bar_chart(
            x=df4['item_name'].tolist(),
            y=df4['total_quantity'].tolist(),
            title='Total Items Sold by Item (v2)',
            x_title='Item',
            y_title='Quantity Sold',
            color='green'
        )
        graphs.append(fig4_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 4")
        graphs.append(f"<p>Error: Missing column {e} in Chart 4 data.</p>")

    # === Chart 5: Order Count by Days (v2) ===
    order_count_days = get_order_count_by_days()
    df5 = pd.DataFrame(order_count_days)
    try:
        fig5_html = create_scatter_chart(
            x=df5['day'].tolist(),
            y=df5['order_count'].tolist(),
            title='Order Count by Days (v2)',
            x_title='Day',
            y_title='Number of Orders',
            color='red'
        )
        graphs.append(fig5_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 5")
        graphs.append(f"<p>Error: Missing column {e} in Chart 5 data.</p>")

    # === Chart 6: Total Order Sum by Months (v2) ===
    total_order_months = get_total_order_sum_by_months()
    df6 = pd.DataFrame(total_order_months)
    if not df6.empty:
        df6['total_order_sum'] = df6['total_sum']
    try:
        fig6_html = create_bar_chart(
            x=df6['month'].tolist(),
            y=df6['total_order_sum'].tolist(),
            title='Total Order Sum by Months (v2)',
            x_title='Month',
            y_title='Total Order Sum',
            color='blue'
        )
        graphs.append(fig6_html)
    except KeyError as e:
        print(f"KeyError: {e} in Chart 6")
        graphs.append(f"<p>Error: Missing column {e} in Chart 6 data.</p>")

    # === Chart 7: Performance Chart ===
    performance_queries = [simulate_database_query for _ in range(33)]
    performance_results = measure_performance(performance_queries, mode='thread')
    df7 = pd.DataFrame(performance_results)
    if not df7.empty:
        try:
            fig7_html = create_scatter_chart(
                x=df7['parameter'].tolist(),
                y=df7['execution_time'].tolist(),
                title='Thread Pool Performance Analysis (v2)',
                x_title='Number of Threads',
                y_title='Execution Time (s)',
                color='black'
            )
            graphs.append(fig7_html)
        except KeyError as e:
            print(f"KeyError: {e} in Chart 7")
            graphs.append(f"<p>Error: Missing column {e} in Chart 7 data.</p>")
    else:
        graphs.append("<p>No performance data available.</p>")

    return render(request, 'dashboard.html', {'graphs': graphs, 'version': version})