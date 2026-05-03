from db import get_client

TABLE = 'transactions'
CATEGORIES_TABLE = 'categories'

def add_transaction(user_id, category_id, amount, description, tx_type, transaction_date):
    """
    Calls the add_transaction PostgreSQL function via RPC.
    """
    client = get_client()
    # Parameters must match the names in schema.sql: 
    # p_user_id, p_cat_id, p_amount, p_desc, p_type, p_date
    client.rpc('add_transaction', {
        'p_user_id': int(user_id),
        'p_cat_id': int(category_id),
        'p_amount': float(amount),
        'p_desc': description,
        'p_type': tx_type,
        'p_date': transaction_date
    }).execute()

def get_transactions(user_id):
    """
    Returns list of transactions for a user with category names joined.
    """
    client = get_client()
    response = client.table(TABLE).select('*, categories(name)').eq('user_id', user_id).order('transaction_date', desc=True).execute()
    return response.data

def delete_transaction(transaction_id, user_id):
    """
    Calls the delete_transaction PostgreSQL function via RPC.
    """
    client = get_client()
    client.rpc('delete_transaction', {
        'p_tx_id': int(transaction_id),
        'p_user_id': int(user_id)
    }).execute()

def get_all_categories():
    """
    Fetches all categories ordered by type and name.
    """
    client = get_client()
    response = client.table(CATEGORIES_TABLE).select('*').order('type').order('name').execute()
    return response.data
