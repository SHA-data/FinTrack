from flask import Flask
from config import SECRET_KEY
from routes.auth import auth
from routes.dashboard import dashboard
from routes.transactions import transactions
from routes.budgets import budgets
from routes.insights import insights

def create_app():
    """
    Flask Application Factory.
    Registers blueprints and configures the app instance.
    """
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Add these to app.py right after app = Flask(__name__)
    @app.template_filter('currency')
    def currency_filter(value):
        """Format a number as currency."""
        try:
            return f"Rs. {float(value):,.2f}"
        except (ValueError, TypeError):
            return "Rs. 0.00"

    @app.template_filter('dateformat')
    def dateformat_filter(value):
        """Format a date object or string to 'Apr 23, 2025'."""
        from datetime import date, datetime
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                return value
        if isinstance(value, date) or isinstance(value, datetime):
            return value.strftime('%b %d, %Y')
        return value

    @app.template_filter('datetimeformat')
    def datetimeformat_filter(value):
        """Format a datetime object or string to 'Apr 23, 2025 at 3:42 PM'."""
        from datetime import datetime
        if isinstance(value, str):
            try:
                # Assuming ISO format from DB
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        if isinstance(value, datetime):
            return value.strftime('%b %d, %Y at %I:%M %p')
        return value

    # Register Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(transactions)
    app.register_blueprint(budgets)
    app.register_blueprint(insights)

    return app

if __name__ == '__main__':
    app = create_app()
    # Debug mode is loaded from environment via config if desired, 
    # but prompt specifically asks for app.run(debug=True) here.
    app.run(debug=True)
