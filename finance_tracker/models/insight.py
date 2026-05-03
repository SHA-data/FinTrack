from db import get_client

TABLE = 'ai_insights'

def save_insight(user_id, prompt_sent, insight_text):
    """
    Saves a generated AI insight. Trigger handles history limit.
    """
    client = get_client()
    response = client.table(TABLE).insert({
        'user_id': user_id,
        'prompt_sent': prompt_sent,
        'insight_text': insight_text
    }).execute()
    return response.data[0]

def get_insights_for_user(user_id):
    """
    Returns last 10 insights for the user.
    """
    client = get_client()
    response = client.table(TABLE).select('*').eq('user_id', user_id).order('generated_at', desc=True).execute()
    return response.data
