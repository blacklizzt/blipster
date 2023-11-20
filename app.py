import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import (
    Flask, 
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
)
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from werkzeug.utils import secure_filename

# Load environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = os.environ.get("UPLOAD_FOLDER", './static/profile_pics')

# MongoDB connection setup
SECRET_KEY = os.environ.get("SECRET_KEY")
TOKEN_KEY = os.environ.get("TOKEN_KEY")
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

MONGODB_CONNECTION_STRING = f"mongodb+srv://{MONGODB_URI}/{DB_NAME}?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[DB_NAME]

# Routes

@app.route('/', methods=['GET'])
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('index.html', user_info=user_info)

    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)

# (Other routes...)

# Run the app if this script is executed
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
