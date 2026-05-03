from flask import Blueprint, render_template, session
from routes.auth import login_required
from models.dashboard import get_summary, get_category_breakdown
from models.budget import get_budget_alerts

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@login_required
def index():
    """
    Renders the main dashboard with spending summaries and alerts.
    """
    user_id = session['user_id']
    summary = get_summary(user_id)
    breakdown = get_category_breakdown(user_id)
    alerts = get_budget_alerts(user_id)
    
    return render_template('dashboard.html', 
                           summary=summary, 
                           breakdown=breakdown, 
                           alerts=alerts)
