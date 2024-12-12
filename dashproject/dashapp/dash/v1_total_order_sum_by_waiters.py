from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
from django import forms
from django.db.models import Sum
from dashapp.models import Order


def prepare_dataframe(data):
    df = pd.DataFrame(data)
    if not df.empty:
        df['waiter_name'] = df['waiters__first_name'] + ' ' + df['waiters__last_name']
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
        return "<p>Немає даних для відображення графіку.</p>"

    fig = go.Figure(
        data=[go.Pie(
            labels=df['waiter_name'],
            values=df['total_sum'],
            hole=0.3,
            hoverinfo="label+percent",
            textinfo="label+percent"
        )]
    )

    fig.update_layout(
        title_text="Загальна сума замовлень по офіціантах",
        template="plotly_white",
    )

    return fig.to_html(full_html=False)


class OrderSumForm(forms.Form):
    def __init__(self, *args, **kwargs):
        total_sums = kwargs.pop('total_sums', [0, 100])
        super().__init__(*args, **kwargs)
        min_sum = int(min(total_sums))
        max_sum = int(max(total_sums))
        extended_max_sum = max_sum * 2  # Increase the max sum to 2x

        self.fields['min_sum'] = forms.IntegerField(
            label='Мінімальна сума замовлень',
            min_value=min_sum,
            max_value=extended_max_sum,  # Use the extended max sum
            initial=min_sum,
            required=False
        )
        self.fields['max_sum'] = forms.IntegerField(
            label='Максимальна сума замовлень',
            min_value=min_sum,
            max_value=extended_max_sum,  # Use the extended max sum
            initial=max_sum,
            required=False
        )
        self.fields['sort_order'] = forms.ChoiceField(
            choices=[
                ('default', 'За замовчуванням'),
                ('asc', 'Зростання'),
                ('desc', 'Спадання')
            ],
            label="Сортування",
            required=False
        )


def get_total_order_sum_by_waiters():
    orders = Order.objects.values(
        'waiters__first_name',
        'waiters__last_name'
    ).annotate(total_sum=Sum('total_sum')).distinct()
    df = pd.DataFrame(list(orders))
    if not df.empty:
        df['waiter_name'] = df['waiters__first_name'] + ' ' + df['waiters__last_name']
    return df


def total_order_sum_by_waiters(request):
    df = get_total_order_sum_by_waiters()
    if df.empty:
        total_sums = [0]
    else:
        total_sums = df['total_sum']
    form = OrderSumForm(request.POST or None, total_sums=total_sums)

    if form.is_valid():
        min_sum = form.cleaned_data.get('min_sum') or df['total_sum'].min()
        max_sum = form.cleaned_data.get('max_sum') or (df['total_sum'].max() * 2)  # Use extended max sum
        sort_order = form.cleaned_data.get('sort_order', 'default')
    else:
        if not df.empty:
            min_sum = df['total_sum'].min()
            max_sum = df['total_sum'].max() * 2  # Use extended max sum
        else:
            min_sum = 0
            max_sum = 0
        sort_order = 'default'

    # Filtering based on sum
    if not df.empty:
        df = df[(df['total_sum'] >= min_sum) & (df['total_sum'] <= max_sum)]

        # Sorting
        if sort_order == 'asc':
            df = df.sort_values(by='total_sum', ascending=True).reset_index(drop=True)
        elif sort_order == 'desc':
            df = df.sort_values(by='total_sum', ascending=False).reset_index(drop=True)
        # 'default' maintains the current order

        stats = calculate_statistics(df)
    else:
        stats = {'mean': 0, 'median': 0, 'min': 0, 'max': 0}

    # Create Pie Chart
    plot = create_plotly_pie_chart(df)

    return render(request, 'plotly_total_order_sum_by_waiters.html', {
        'plot': plot,
        'form': form,
        'data': df.to_dict(orient='records'),
        **stats,
    })