import sys
from flask import (Flask, render_template, request, redirect,
                   make_response, url_for, flash, jsonify)
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database_setup import Base, Category, Item, User

app = Flask(__name__)

engine = create_engine('sqlite:///catalogapp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/category/')
def category():
	return render_template('category_list.html',
                           categories=session.query(Category).all(),
                           items=session.query(Item).order_by('id DESC').limit(10).all(),
                           )

@app.route('/category/<int:category_id>/')
def showItemsForCategory(category_id):
	return sys._getframe().f_code.co_name

@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
	return render_template('item.html',
                           categories=session.query(Category).all(),
                           item=session.query(Item, Category).filter_by(id=item_id).join(Category).one(),
                           main_category=category_id)

@app.route('/category/<int:category_id>/addItem', methods=['GET', 'POST'])
def addItem(category_id):
	return sys._getframe().f_code.co_name

@app.route('/category/<int:category_id>/editItem/<int:item_id>/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
	return sys._getframe().f_code.co_name

@app.route('/category/<int:category_id>/deleteItem/<int:item_id>/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
	return sys._getframe().f_code.co_name

@app.route('/gconnect', methods=['POST'])
def gconnect():
	return sys._getframe().f_code.co_name


@app.route('/gdisconnect')
def gdisconnect():
	return sys._getframe().f_code.co_name


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
