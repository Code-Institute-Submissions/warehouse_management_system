import os
import re
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Flask, render_template, redirect, request, flash, url_for, config
from os import path
if path.exists("env.py"):
    import env

app = Flask(__name__)
app.config['MONGO_URI'] = os.environ.get("MONGO_URI")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route('/')
@app.route('/manage_stock_cards')
def manage_stock_cards():
    return render_template("managestockcard.html",
                           stock_cards=mongo.db.stock_cards.find())


@app.route('/archive_stock_cards')
def archive_stock_cards():
    return render_template("archivestockcard.html",
                           stock_cards=mongo.db.stock_cards.find())


@app.route('/add_stock_cards')
def add_stock_cards():
    return render_template('addstockcard.html',
                           customer=mongo.db.customer.find())


@app.route('/insert_stock_cards', methods=['POST'])
def insert_stock_cards():
    stock_cards = mongo.db.stock_cards
    stock_cards.insert_one(request.form.to_dict())
    return redirect(url_for('manage_stock_cards'))


@app.route('/edit_stock_cards/<stock_cards_id>')
def edit_stock_cards(stock_cards_id):
    stock_cards = mongo.db.stock_cards.find_one({"_id": ObjectId
                                                (stock_cards_id)})
    customer = mongo.db.customer.find()
    return render_template('editstockcard.html',
                           stock_cards=stock_cards, customer=customer)


@app.route('/update_stock_cards/<stock_cards_id>', methods=["POST"])
def update_stock_cards(stock_cards_id):
    stock_cards = mongo.db.stock_cards
    stock_cards.update_one({'_id': ObjectId(stock_cards_id)},
                           {
        'customer': request.form.get('customer'),
        'product_code': request.form.get('product_code'),
        'product_desc': request.form.get('product_desc'),
        'unit_weight': request.form.get('unit_weight'),
        'unit_per_pallet': request.form.get('unit_per_pallet'),
        'suppler': request.form.get('supplier'),
        'packaging': request.form.get('packaging'),
    })
    return redirect(url_for('manage_stock_cards'))


@app.route('/search_stock_card')
def search_stock_card():
    """Provides logic for search bar"""
    orig_query = request.args['query']
    query = {'$regex': re.compile('.*{}.*'.format(orig_query))}
    results = mongo.db.stock_cards.find({
        '$or': [
            {'product_code': query},
            {'product_desc': query},
        ]
    })
    return render_template('stockcardsearch.html', query=orig_query, results=results)


@app.route('/delist_stock_cards/<stock_cards_id>')
def delist_stock_cards(stock_cards_id):
    stock_cards = mongo.db.stock_cards
    stock_cards.update_one({'_id': ObjectId(stock_cards_id)},
                           {
                                "$set": {
                                            "active": "off"
                                        }
                            })
    return redirect(url_for('manage_stock_cards'))


@app.route('/relist_stock_cards/<stock_cards_id>')
def relist_stock_cards(stock_cards_id):
    stock_cards = mongo.db.stock_cards
    stock_cards.update_one({'_id': ObjectId(stock_cards_id)},
                           {
                               "$set": {
                                            "active": "on"
                               }
                           })
    return redirect(url_for('manage_stock_cards'))


@app.route('/delete_stock_cards/<stock_cards_id>')
def delete_stock_cards(stock_cards_id):
    mongo.db.stock_cards.remove({'_id': ObjectId(stock_cards_id)})
    return redirect(url_for('manage_stock_cards'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
