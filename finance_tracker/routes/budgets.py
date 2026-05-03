from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from models.budget import set_budget, get_budgets
from models.transaction import get_all_categories

budgets = Blueprint('budgets', __name__, url_prefix='/budgets')

@budgets.route('/', methods=['GET'])
@login_required
def index():
    """
    Renders the budgets management page.
    """
    user_id = session['user_id']
    budget_list = get_budgets(user_id)
    categories = get_all_categories()
    return render_template('budgets.html', budgets=budget_list, categories=categories)

@budgets.route('/', methods=['POST'])
@login_required
def update():
    """
    Sets or updates a monthly budget for a category.
    """
    try:
        user_id = session['user_id']
        category_id = int(request.form.get('category_id'))
        limit_amount = float(request.form.get('limit_amount'))
        month_year = request.form.get('month_year') # Expected format: YYYY-MM
        
        if limit_amount <= 0:
            flash("Budget limit must be greater than 0", "danger")
            return redirect(url_for('budgets.index'))
            
        if not month_year:
            flash("Month and year are required", "danger")
            return redirect(url_for('budgets.index'))
            
        set_budget(user_id, category_id, limit_amount, month_year)
        flash("Budget updated successfully", "success")
        
    except (ValueError, TypeError):
        flash("Invalid input data", "danger")
        
    return redirect(url_for('budgets.index'))
