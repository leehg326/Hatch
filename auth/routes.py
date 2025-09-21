from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt,
    set_refresh_cookies, unset_jwt_cookies
)
from db import db
from models import User
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('name', 'email', 'password')):
            return jsonify({'message': 'Missing required fields'}), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'User already exists'}), 409
        
        # Create new user
        user = User(
            name=name,
            email=email,
            role='agent'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('email', 'password')):
            return jsonify({'message': 'Missing email or password'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"tv": user.token_version}
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            additional_claims={"tv": user.token_version}
        )
        
        # Set refresh token as HttpOnly cookie
        response = jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        })
        
        set_refresh_cookies(response, refresh_token)
        return response, 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
        
        # Verify refresh token
        verify_jwt_in_request(refresh=True)
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Get user and check token version
        user = User.query.get(user_id)
        if not user or claims.get('tv') != user.token_version:
            return jsonify({'message': 'Invalid token'}), 401
        
        # Create new access token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"tv": user.token_version}
        )
        
        return jsonify({'access_token': access_token}), 200
        
    except Exception as e:
        return jsonify({'message': 'Token refresh failed'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        
        # Verify access token
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        # Increment token version to invalidate all tokens
        user = User.query.get(user_id)
        if user:
            user.token_version += 1
            db.session.commit()
        
        # Clear refresh cookie
        response = jsonify({'message': 'Logged out successfully'})
        unset_jwt_cookies(response)
        return response, 200
        
    except Exception as e:
        # Even if token is invalid, clear cookies
        response = jsonify({'message': 'Logged out'})
        unset_jwt_cookies(response)
        return response, 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get user info'}), 500