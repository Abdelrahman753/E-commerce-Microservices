from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///cart.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
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

def get_product_details(product_id):
    try:
        response = requests.get(f'http://product-service:5003/products/{product_id}')
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'cart-service'})

@app.route('/cart', methods=['POST'])
def add_to_cart():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        data = request.get_json()
        user_id = auth_data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Check if product exists
        product = get_product_details(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if item already in cart
        existing_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({'message': 'Item added to cart successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cart', methods=['GET'])
def get_cart():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = auth_data.get('user_id')
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        
        cart_data = []
        total_amount = 0
        
        for item in cart_items:
            product = get_product_details(item.product_id)
            if product:
                item_total = product['price'] * item.quantity
                total_amount += item_total
                
                cart_data.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': product['name'],
                    'price': product['price'],
                    'quantity': item.quantity,
                    'total': item_total
                })
        
        return jsonify({
            'cart_items': cart_data,
            'total_amount': total_amount
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        is_valid, auth_data = verify_token(token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = auth_data.get('user_id')
        cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'message': 'Item removed from cart'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
