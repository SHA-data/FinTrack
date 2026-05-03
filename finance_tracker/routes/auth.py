from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import create_user, get_user_by_email, verify_password

auth = Blueprint('auth', __name__)

def login_required(f):
    """
    Decorator to ensure user is logged in before accessing a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash("All fields are required", "danger")
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template('auth/register.html')
            
        try:
            create_user(username, email, password)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), "danger")
            return render_template('auth/register.html')
            
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = get_user_by_email(email)
        if not user:
            flash("Email not found", "danger")
            return render_template('auth/login.html')
            
        if not verify_password(password, user['password_hash']):
            flash("Incorrect password", "danger")
            return render_template('auth/login.html')
            
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for('dashboard.index'))
        
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('auth.login'))
