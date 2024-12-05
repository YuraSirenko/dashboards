from django.shortcuts import render
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from dashapp.queries.total_order_sum_by_customers import get_total_order_sum_by_customers

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)
    if not df.empty:
        # Combine first and last names into a single column
        df['customer_name'] = df['customer__first_name'] + ' ' + df['customer__last_name']
        
        # Convert 'total_sum' from Decimal to float
        df['total_sum'] = df['total_sum'].astype(float)
        
        # Sort the DataFrame based on the sort_order
        if sort_order == "asc":
            df = df.sort_values(by='total_sum', ascending=True).reset_index(drop=True)
        elif sort_order == "desc":
            df = df.sort_values(by='total_sum', ascending=False).reset_index(drop=True)
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

def create_bokeh_chart(df):
    if df.empty:
        return None, "<p>No data available for the chart.</p>"
    
    source = ColumnDataSource(df)
    p = figure(
        x_range=df['customer_name'].tolist(),
        title="Total Order Sum by Customers",
        x_axis_label="Customer",
        y_axis_label="Total Order Sum",
        width=900,
        height=500,
        tools="hover,pan,box_zoom,reset,save"
    )
    
    p.vbar(
        x='customer_name',
        top='total_sum',
        width=0.9,
        source=source,
        color="green",
        legend_label="Total Sum"
    )
    
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 1.2
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"
    
    script, div = components(p)
    return script, div

def total_order_sum_by_customers_view(request):
    sort_order = request.GET.get('sort', 'desc')
    total_order_data = get_total_order_sum_by_customers()
    
    # Ensure you're fetching the right fields
    data = list(total_order_data.values('customer__first_name', 'customer__last_name', 'total_sum'))
    
    df = prepare_dataframe(data, sort_order)
    stats = calculate_statistics(df)
    script, div = create_bokeh_chart(df)
    
    return render(request, 'bokeh_total_order_sum_by_customers.html', {
        'script': script,
        'div': div,
        'data_table': df.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
    })