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


def categories():
    return session.query(Category).order_by('name')

def category(category_id):
    return session.query(Category).filter_by(id=category_id).one()

def item(item_id):
        return session.query(Item, Category).filter_by(id=item_id).join(Category).one()

def itemsLatestFirst():
        return session.query(Item).order_by('id DESC').limit(10).all()

def items(category_id):
    return session.query(Item).filter_by(category_id=category_id).all()

def addToDatabase(item):
    session.add(item)
    session.commit()
    return

def deleteFromDatabase(item):
    session.delete(item)
    session.commit()
    return

@app.route('/')
@app.route('/category/')
def category():
	return render_template('category_list.html',
                           categories=categories(),
                           items=itemsLatestFirst(),
                           )

@app.route('/category/<int:category_id>/')
def showItemsForCategory(category_id):
	return sys._getframe().f_code.co_name

@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
	return render_template('item.html',
                           categories=categories(),
                           item=item(item_id),
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
