from django.shortcuts import render
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from dashapp.queries.total_income_by_item import get_total_income_by_item

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)
    if not df.empty:
        if sort_order == "asc":
            df = df.sort_values(by='total_income', ascending=True).reset_index(drop=True)
        elif sort_order == "desc":
            df = df.sort_values(by='total_income', ascending=False).reset_index(drop=True)
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

def create_bokeh_chart(df):
    if df.empty:
        return None, "<p>No data available for the chart.</p>"
    
    # Create a unique label by combining item ID and name
    df['item_label'] = df['item__id'].astype(str) + ' - ' + df['item__name']
    
    source = ColumnDataSource(df)
    p = figure(
        x_range=df['item_label'].tolist(),
        title="Total Income by Item",
        x_axis_label="Item",
        y_axis_label="Total Income",
        width=900,
        height=500,
        tools="hover,pan,box_zoom,reset,save"
    )
    
    p.vbar(
        x='item_label',
        top='total_income',
        width=0.9,
        source=source,
        color="teal",
        legend_label="Total Income"
    )
    
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 1.2
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"
    
    script, div = components(p)
    return script, div

def total_income_by_item_view(request):
    sort_order = request.GET.get('sort', 'desc')
    total_income_data = get_total_income_by_item()
    
    data = list(total_income_data.values('item__id', 'item__name', 'total_income'))
    
    df = prepare_dataframe(data, sort_order)
    stats = calculate_statistics(df)
    script, div = create_bokeh_chart(df)
    
    return render(request, 'bokeh_total_income_by_item.html', {
        'script': script,
        'div': div,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })