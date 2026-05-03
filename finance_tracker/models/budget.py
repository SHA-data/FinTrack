from datetime import datetime
from db import get_client

TABLE = 'budgets'
ALERTS_TABLE = 'budget_alerts'

def set_budget(user_id, category_id, limit_amount, month_year):
    """
    Calls set_budget RPC. Appends -01 to month_year string.
    """
    client = get_client()
    # input: "2025-04" -> "2025-04-01"
    full_date = f"{month_year}-01"
    client.rpc('set_budget', {
        'p_user_id': int(user_id),
        'p_cat_id': int(category_id),
        'p_limit': float(limit_amount),
        'p_month': full_date
    }).execute()

def get_budgets(user_id):
    """
    Fetches budgets and current month's spending. 
    Merged in Python for better readability and lower complexity in SQL.
    """
    client = get_client()
    current_month_start = datetime.now().strftime('%Y-%m-01')
    
    # 1. Fetch budgets for current month
    budgets_resp = client.table(TABLE).select('*, categories(name)').eq('user_id', user_id).eq('month_year', current_month_start).execute()
    budgets = budgets_resp.data

    # 2. Fetch spending summary from view for current month
    spending_resp = client.table('transactions').select('category_id, amount').eq('user_id', user_id).eq('tx_type', 'expense').gte('transaction_date', current_month_start).execute()
    
    spending_map = {}
    for tx in spending_resp.data:
        cat_id = tx['category_id']
        spending_map[cat_id] = spending_map.get(cat_id, 0) + float(tx['amount'])
    
    # 3. Merge
    for b in budgets:
        b['spent'] = spending_map.get(b['category_id'], 0.0)
    
    return budgets

def get_budget_alerts(user_id):
    """
    Returns latest 5 budget alerts for the user.
    """
    client = get_client()
    response = client.table(ALERTS_TABLE).select('*, categories(name)').eq('user_id', user_id).order('alerted_at', desc=True).limit(5).execute()
    return response.data
