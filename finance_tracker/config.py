import os
from dotenv import load_dotenv

# Load .env values at module level
load_dotenv()

# Expose constants for use across the application
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
