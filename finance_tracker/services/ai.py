from groq import Groq
from config import GROQ_API_KEY

def build_prompt(summary: dict, breakdown: list) -> str:
    """
    Constructs a structured plain-text prompt for the AI advisor.
    """
    total_income = summary.get('total_income', 0.0)
    total_expense = summary.get('total_expense', 0.0)
    net_balance = summary.get('net_balance', 0.0)
    
    breakdown_text = "\n".join([f"- {item['category']}: ${item['total']}" for item in breakdown])
    
    prompt = (
        f"User Spending Summary for this month:\n"
        f"Total Income: ${total_income}\n"
        f"Total Expenses: ${total_expense}\n"
        f"Net Balance: ${net_balance}\n\n"
        f"Breakdown of spending per category:\n"
        f"{breakdown_text}\n\n"
        "Please provide specific, actionable financial advice based on this data. "
        "Respond in plain text with 3 to 4 short paragraphs. "
        "Do not use markdown, bullet points, asterisks, or any special formatting."
    )
    return prompt

def call_groq(prompt: str) -> str:
    """
    Initialises Groq client and calls completions API with LLaMA-3.3
    """
    if not GROQ_API_KEY or GROQ_API_KEY == 'your-groq-api-key':
        raise RuntimeError("GROQ_API_KEY is not configured.")
        
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly personal finance advisor providing tailored advice. Make sure to remain to the point and preferably use bullet points instead of paragraphs to make your point."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Failed to generate AI insight: {str(e)}")
