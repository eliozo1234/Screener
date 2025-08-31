import os
from dotenv import load_dotenv  # Ajout
load_dotenv()  # Ajout

from flask import Flask, send_from_directory
from flask_cors import CORS
from api.models.user import db
from api.routes.screening import screening_bp
from api.routes.auth import auth_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '../static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///screening_actions.db')  # Ajout env
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

db.init_app(app)

app.register_blueprint(screening_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

with app.app_context():
    db.create_all()

# Route statique (code original)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
