from datetime import datetime
from db import get_client

def get_summary(user_id):
    """
    Returns summary stats (income, expense, net) for current month.
    """
    client = get_client()
    current_month_str = datetime.now().strftime('%Y-%m')
    
    response = client.table('monthly_summary').select('*').eq('user_id', user_id).eq('month', current_month_str).execute()
    
    if not response.data:
        return {
            'total_income': 0.0,
            'total_expense': 0.0,
            'net_balance': 0.0
        }
    
    data = response.data[0]
    income = float(data.get('income') or 0.0)
    expense = float(data.get('expense') or 0.0)
    
    return {
        'total_income': income,
        'total_expense': expense,
        'net_balance': income - expense
    }

def get_category_breakdown(user_id):
    """
    Returns expense totals per category for charts.
    """
    client = get_client()
    response = client.table('category_totals').select('category, total').eq('user_id', user_id).eq('tx_type', 'expense').execute()
    return response.data
