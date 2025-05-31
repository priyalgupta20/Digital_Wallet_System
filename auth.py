from flask import Blueprint, request, jsonify
from storage import add_user, get_user
from models import User
import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    pin = data.get('pin')
    is_admin = data.get('is_admin', False)

    if not username or not pin:
        return jsonify({"msg": "Missing username or PIN"}), 400

    if get_user(username):
        return jsonify({"msg": "Username already taken"}), 400

    hashed_pin = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())
    user = User(username, hashed_pin, is_admin)
    add_user(user)
    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    pin = data.get('pin')

    user = get_user(username)
    if not user or user.deleted or user.blocked:
        return jsonify({"msg": "User not found or blocked"}), 404

    if not bcrypt.checkpw(pin.encode('utf-8'), user.hashed_pin):
        return jsonify({"msg": "Invalid PIN"}), 401

    access_token = create_access_token(identity=username, expires_delta=timedelta(hours=1))
    return jsonify(access_token=access_token), 200
