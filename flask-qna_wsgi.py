import sys
import os

# Add your project directory to the sys.path
project_home = '/home/anuragmy/flask-qna'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set the Flask app's environment
os.environ['FLASK_ENV'] = 'production'

# Import your Flask app
from app import app as application  # change 'app' to your actual file/module if different
