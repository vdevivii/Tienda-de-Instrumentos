from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime
from app import db

def add_user(username, password, role):
    password_hash = generate_password_hash(password)
    user = {'username': username, 'password': password_hash, 'role': 'user', 'role': role}
    db.users.insert_one(user)

def validate_user(username, password):
    user = db.users.find_one({'username': username})
    if check_password_hash(user['password'], password):
        return user
    else:
        return None

def get_user(username):
    return db.users.find_one({'username': username})

def get_all_instruments():
    return db.instruments.find()

def add_instrument(instrument):
    db.instruments.insert_one(instrument)

def get_instrument_by_id(instrument_id):
    instrument = db.instruments.find_one({'_id': ObjectId(instrument_id)})
    if instrument:
        instrument['_id'] = str(instrument['_id'])
    return instrument

def update_instrument(instrument_id, updated_instrument):
    db.instruments.update_one({'_id': ObjectId(instrument_id)}, {'$set': updated_instrument})

def delete_instrument(instrument_id):
    db.instruments.delete_one({'_id': ObjectId(instrument_id)})

def add_card(username, card_number, expiration_date, cvv):
    card = {'username': username, 'card_number': card_number, 'expiration_date': expiration_date, 'cvv': cvv}
    db.cards.insert_one(card)

def get_card(username):
    return db.cards.find_one({'username': username})

def add_order(username, items, total):
    order = {'username': username, 'items': items, 'total': total, 'status': 'Pendiente', 'date': datetime.now()}
    db.orders.insert_one(order)

def get_orders(username):
    return db.orders.find({'username': username})

def add_review(instrument_id, username, rating, comment):
    review = {'instrument_id': ObjectId(instrument_id), 'username': username, 'rating': rating, 'comment': comment}
    db.reviews.insert_one(review)

def get_reviews(instrument_id):
    return db.reviews.find({'instrument_id': ObjectId(instrument_id)})
