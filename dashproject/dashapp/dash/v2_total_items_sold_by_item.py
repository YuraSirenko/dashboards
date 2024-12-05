from django.shortcuts import render
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from dashapp.queries.total_items_sold_by_item import get_total_items_sold_by_item

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)
    if not df.empty:
        if sort_order == "asc":
            df = df.sort_values(by='total_quantity', ascending=True).reset_index(drop=True)
        elif sort_order == "desc":
            df = df.sort_values(by='total_quantity', ascending=False).reset_index(drop=True)
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

def create_bokeh_chart(df):
    if df.empty:
        return None, "<p>No data available for the chart.</p>"
    
    source = ColumnDataSource(df)
    p = figure(
        x_range=df['item__name'].tolist(),
        title="Total Items Sold by Item",
        x_axis_label="Item",
        y_axis_label="Total Quantity Sold",
        width=900,
        height=500,
        tools="hover,pan,box_zoom,reset,save"
    )
    
    p.vbar(
        x='item__name',
        top='total_quantity',
        width=0.9,
        source=source,
        color="purple",
        legend_label="Total Quantity"
    )
    
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 1.2
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"
    
    script, div = components(p)
    return script, div

def total_items_sold_view(request):
    sort_order = request.GET.get('sort', 'desc')
    total_items_data = get_total_items_sold_by_item()
    
    data = list(total_items_data.values('item__name', 'total_quantity'))
    
    df = prepare_dataframe(data, sort_order)
    stats = calculate_statistics(df)
    script, div = create_bokeh_chart(df)
    
    return render(request, 'bokeh_total_items_sold_by_item.html', {
        'script': script,
        'div': div,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })