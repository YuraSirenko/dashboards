
from django.shortcuts import render
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from dashapp.queries.order_count_by_days import get_order_count_by_days

def prepare_dataframe(data, sort_order):

    df = pd.DataFrame(data)
    if not df.empty:
        # Combine year, month, and day into a single date column
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

        # Sort the DataFrame based on the sort_order
        if sort_order == "asc":
            df = df.sort_values(by='date', ascending=True).reset_index(drop=True)
        elif sort_order == "desc":
            df = df.sort_values(by='date', ascending=False).reset_index(drop=True)
        else:
            df = df.sort_values(by='date', ascending=True).reset_index(drop=True)  # Default to ascending
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

def create_bokeh_chart(df):

    if df.empty:
        return None, "<p>No data available for the chart.</p>"

    source = ColumnDataSource(df)
    p = figure(
        x_axis_type='datetime',
        title="Order Count by Days",
        x_axis_label="Date",
        y_axis_label="Number of Orders",
        width=900,
        height=500,
        tools="hover,pan,box_zoom,reset,save"
    )

    p.line('date', 'order_count', source=source, line_width=2, color="blue", legend_label="Order Count")
    p.circle('date', 'order_count', source=source, size=8, color="navy", alpha=0.5)

    p.xgrid.grid_line_color = None
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    script, div = components(p)
    return script, div

def total_order_count_by_days_view(request):
    sort_order = request.GET.get('sort', 'asc')  # Default to ascending order
    total_order_data = get_order_count_by_days()

    # Fetch the required fields: year, month, day, and count of orders
    data = list(total_order_data.values('year', 'month', 'day', 'order_count'))

    df = prepare_dataframe(data, sort_order)
    stats = calculate_statistics(df)
    script, div = create_bokeh_chart(df)

    return render(request, 'bokeh_order_count_by_days.html', {
        'script': script,
        'div': div,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })