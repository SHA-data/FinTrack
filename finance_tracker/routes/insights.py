from flask import Blueprint, render_template, session, redirect, url_for, flash
from routes.auth import login_required
from models.dashboard import get_summary, get_category_breakdown
from models.insight import save_insight, get_insights_for_user
from services.ai import build_prompt, call_groq

insights = Blueprint('insights', __name__, url_prefix='/insights')

@insights.route('/generate', methods=['POST'])
@login_required
def generate():
    """
    Generates a new AI insight based on spending data.
    """
    user_id = session['user_id']
    
    # 1. Gather data
    summary = get_summary(user_id)
    breakdown = get_category_breakdown(user_id)
    
    # 2. Build prompt
    prompt = build_prompt(summary, breakdown)
    
    # 3. Call AI service
    try:
        insight_text = call_groq(prompt)
        
        # 4. Save result
        save_insight(user_id, prompt, insight_text)
        flash("AI insight generated successfully!", "success")
        
    except RuntimeError as e:
        flash(f"Error generating insight: {str(e)}", "danger")
        
    return redirect(url_for('insights.history'))

@insights.route('/history', methods=['GET'])
@login_required
def history():
    """
    Renders the AI insights history page.
    """
    user_id = session['user_id']
    insight_list = get_insights_for_user(user_id)
    return render_template('insights.html', insights=insight_list)
