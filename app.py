from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from auth import auth_bp
from wallet import wallet_bp
from admin import admin_bp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'priyalgupta2004'  
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(wallet_bp, url_prefix='/wallet')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def home():
    return jsonify({"message": "Digital Wallet System API"}), 200

if __name__ == '__main__':
    app.run(debug=True)
