from django.shortcuts import render
from concurrent.futures import ThreadPoolExecutor
import time
import random
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

def simulate_database_query():
    time.sleep(random.uniform(0.1, 0.5))
    return [('fake_data', random.randint(1, 100))]

def threaded_query_execution(queries, max_threads=12):
    results = []
    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(simulate_database_query) for _ in queries]
        for future in futures:
            results.append(future.result())
    return results

def measure_performance(queries, mode='thread', params_range=range(1,16)):
    results = []
    for param in params_range:
        start_time = time.time()
        if mode == 'thread':
            threaded_query_execution(queries, max_threads=param)
        end_time = time.time()
        results.append({
            'parameter': param,
            'execution_time': end_time - start_time
        })
    return results

def performance_chart(request):
        # Create list of simulated queries
    queries = [simulate_database_query for _ in range(10)]
        
        # Measure performance
    thread_results = measure_performance(queries, mode='thread')
        
        # Create DataFrame
    results_df = pd.DataFrame(thread_results)
        
        # Create figure using graph_objects
    fig = go.Figure()
        
        # Add scatter trace
    fig.add_trace(
        go.Scatter(
            x=results_df['parameter'].tolist(),
            y=results_df['execution_time'].tolist(),
            mode='lines+markers',
            name='Execution Time'
        )
    )
        
        # Update layout
    fig.update_layout(
        title='Thread Pool Performance Analysis',
        xaxis_title='Number of Threads',
        yaxis_title='Execution Time (s)',
        showlegend=True
    )
        
        # Convert to HTML
    graph_html = plot(fig, output_type='div', include_plotlyjs=True)
        
    return render(request, 'performance.html', {'graph_html': graph_html})
        
