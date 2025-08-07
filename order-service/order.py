from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///orders.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

def verify_token(token):
    try:
        response = requests.post('http://auth-service:5001/verify', 
                               headers={'Authorization': f'Bearer {token}'})
        return response.status_code == 200, response.json()
    except:
        return False, {}

def get_cart_items(token):
    try:
        response = requests.get('http://cart-service:5004/cart',
                              headers={'Authorization': f'Bearer {token}'})
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'order-service'})

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = auth_data.get('user_id')
        
        # Get cart items
        cart_data = get_cart_items(f'Bearer {token}')
        if not cart_data or not cart_data.get('cart_items'):
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=cart_data['total_amount'],
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add order items
        for item in cart_data['cart_items']:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order_id': order.id,
            'total_amount': order.total_amount
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = auth_data.get('user_id')
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in orders:
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            
            orders_data.append({
                'id': order.id,
                'total_amount': order.total_amount,
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'items': [{
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'price': item.price
                } for item in order_items]
            })
        
        return jsonify({'orders': orders_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        data = request.get_json()
        new_status = data.get('status')
        
        user_id = auth_data.get('user_id')
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order.status = new_status
        db.session.commit()
        
        return jsonify({'message': 'Order status updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
