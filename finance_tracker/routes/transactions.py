from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from models.transaction import add_transaction, get_transactions, delete_transaction, get_all_categories

transactions = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions.route('/', methods=['GET'])
@login_required
def index():
    """
    Renders the transactions list and form.
    """
    user_id = session['user_id']
    tx_list = get_transactions(user_id)
    categories = get_all_categories()
    return render_template('transactions.html', transactions=tx_list, categories=categories)

@transactions.route('/', methods=['POST'])
@login_required
def add():
    """
    Handles adding a new transaction.
    """
    try:
        user_id = session['user_id']
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        category_id = int(request.form.get('category_id'))
        tx_type = request.form.get('tx_type')
        transaction_date = request.form.get('transaction_date')
        
        if amount <= 0:
            flash("Amount must be greater than 0", "danger")
            return redirect(url_for('transactions.index'))
            
        if not description or not transaction_date:
            flash("Description and date are required", "danger")
            return redirect(url_for('transactions.index'))
            
        add_transaction(user_id, category_id, amount, description, tx_type, transaction_date)
        flash("Transaction added successfully", "success")
        
    except (ValueError, TypeError):
        flash("Invalid input data", "danger")
        
    return redirect(url_for('transactions.index'))

@transactions.route('/delete', methods=['POST'])
@login_required
def delete():
    """
    Handles deleting a transaction.
    """
    try:
        transaction_id = int(request.form.get('transaction_id'))
        user_id = session['user_id']
        delete_transaction(transaction_id, user_id)
        flash("Transaction deleted", "info")
    except (ValueError, TypeError):
        flash("Could not delete transaction", "danger")
        
    return redirect(url_for('transactions.index'))
