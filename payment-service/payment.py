from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///payments.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending')
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

def update_order_status(order_id, status, token):
    try:
        response = requests.put(f'http://order-service:5005/orders/{order_id}/status',
                              json={'status': status},
                              headers={'Authorization': f'Bearer {token}'})
        return response.status_code == 200
    except:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'payment-service'})

@app.route('/payments', methods=['POST'])
def process_payment():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        data = request.get_json()
        user_id = auth_data.get('user_id')
        order_id = data.get('order_id')
        amount = data.get('amount')
        payment_method = data.get('payment_method', 'credit_card')
        
        # Generate transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Simulate payment processing
        # In real implementation, you would integrate with payment gateway
        payment_successful = True  # Simulate successful payment
        
        payment = Payment(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            status='completed' if payment_successful else 'failed'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Update order status
        if payment_successful:
            update_order_status(order_id, 'paid', token)
            
            return jsonify({
                'message': 'Payment processed successfully',
                'transaction_id': transaction_id,
                'status': 'completed'
            }), 200
        else:
            return jsonify({
                'message': 'Payment failed',
                'transaction_id': transaction_id,
                'status': 'failed'
            }), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payments/<int:order_id>', methods=['GET'])
def get_payment_status(order_id):
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = auth_data.get('user_id')
        payment = Payment.query.filter_by(order_id=order_id, user_id=user_id).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify({
            'order_id': payment.order_id,
            'amount': payment.amount,
            'payment_method': payment.payment_method,
            'transaction_id': payment.transaction_id,
            'status': payment.status,
            'created_at': payment.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
