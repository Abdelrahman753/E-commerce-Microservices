from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

with app.app_context():
    db.create_all()

def verify_token(token):
    try:
        response = requests.post('http://auth-service:5001/verify', 
                               headers={'Authorization': f'Bearer {token}'})
        return response.status_code == 200, response.json()
    except:
        return False, {}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'user-service'})

@app.route('/profile', methods=['POST'])
def create_profile():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        data = request.get_json()
        user_id = auth_data.get('user_id')
        
        if UserProfile.query.filter_by(user_id=user_id).first():
            return jsonify({'error': 'Profile already exists'}), 400
        
        profile = UserProfile(
            user_id=user_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            country=data.get('country')
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({'message': 'Profile created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['GET'])
def get_profile():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = auth_data.get('user_id')
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify({
            'user_id': profile.user_id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'country': profile.country
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
