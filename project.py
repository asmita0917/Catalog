import sys
from flask import (Flask, render_template, request, redirect,
                   make_response, url_for, flash, jsonify)
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database_setup import Base, Category, Item, User
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from functools import wraps

app = Flask(__name__)

engine = create_engine('sqlite:///catalogapp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


''' Util functions for db operations'''


def db_categories():
    return session.query(Category).order_by('name')


def db_category(category_id):
    return session.query(Category).filter_by(id=category_id).one()


def db_item(item_id):
    try:
        result = session.query(Item, Category)\
                        .filter_by(id=item_id).join(Category).one()
        return result[0]
    except Exception as e:
        return None


def db_itemsLatestFirst():
        return session.query(Item).order_by('id DESC').limit(10).all()


def db_items(category_id):
    return session.query(Item).filter_by(category_id=category_id).all()


def db_addToDatabase(item):
    session.add(item)
    session.commit()
    return


def db_deleteFromDatabase(item):
    session.delete(item)
    session.commit()
    return


def db_addUser(login_session):
        newUser = User(name=login_session['name'],
                       email=login_session['email'],
                       picture=login_session['picture'])
        session.add(newUser)
        session.commit()
        return


def db_getUserBy(login_session):
    try:
        return session.query(User)\
                      .filter_by(email=login_session['email']).one()
    except:
        db_addUser(login_session)
        return session.query(User)\
                      .filter_by(email=login_session['email']).one()


def createState():
    if login_session.get('state') is None:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state



''' routes for web app'''


@app.route('/login')
def login():
    createState()
    return render_template('login.html', user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'))


@app.route('/')
@app.route('/category/')
def category():
    createState()
    return render_template('category_list.html',
                           categories=db_categories(),
                           items=db_itemsLatestFirst(),
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state')
                           )


@app.route('/category/<int:category_id>/')
def showItems(category_id):
    createState()
    return render_template('category.html',
                           main_category=db_category(category_id),
                           categories=db_categories(),
                           items=db_items(category_id),
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'))


@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
    createState()
    return render_template('item.html',
                           categories=db_categories(),
                           item=db_item(item_id),
                           main_category=category_id,
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'))


def user_allowed_to_modify(entity):
    return ('user_id' in login_session and
            entity.user_id == login_session['user_id'])



''' Decorator function to check authorization '''



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


@app.route('/category/<int:category_id>/addItem', methods=['GET', 'POST'])
@login_required
def addItem(category_id):
    if request.method == 'POST':
        item = Item(name=request.form['name'],
                    description=request.form['description'],
                    category_id=category_id,
                    user_id=login_session['user_id'])
        db_addToDatabase(item)
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('addItem.html',
                               category=db_category(category_id))


@app.route('/category/<int:category_id>/editItem/<int:item_id>/',
           methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
    item = db_item(item_id)
    if not user_allowed_to_modify(item):
            flash("You are not authorized to edit this item")
            return redirect('/')
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.category_id = category_id
        db_addToDatabase(item)
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('editItem.html',
                               category=db_category(category_id),
                               item=item)


@app.route('/category/<int:category_id>/deleteItem/<int:item_id>/',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_id, item_id):
    item = db_item(item_id)
    if not user_allowed_to_modify(item):
        flash("You are not authorized to delete this item")
        return redirect('/')
    if request.method == 'POST':
        db_deleteFromDatabase(item)
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('deleteItem.html',
                               category=db_category(category_id),
                               item=item)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    ''' Validate state token '''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    ''' Obtain authorization code '''
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object'''
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Check that the access token is valid.'''
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    ''' If there was an error in the access token info, abort.'''
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Verify that the access token is used for the intended user.'''
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Verify that the access token is valid for this app.'''
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Store the access token in the session for later use.'''
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    ''' Get user info'''
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['name'] = data['name']
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['user_id'] = db_getUserBy(login_session).id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:' +\
              '150px;-webkit-border-radius: 150px;-moz-border-radius:' +\
              ' 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    ''' Invalidate the access_token '''
    try:
        access_token = login_session['access_token']
    except Exception:
        response = make_response(json.dumps('Current user not conected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if access_token is None:
        response = make_response(json.dumps('Current user not conected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    ''' Once the token is revoked, invalidate login_session '''
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['name']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('category'))

    else:
        response = make_response(json.dumps('Failed to revoke token' +
                                            ' for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API
@app.route('/category/JSON/')
def categoryJSON():
    categories = db_categories()
    return jsonify(categories=[category.serialize for category in categories])


@app.route('/category/<int:category_id>/items/JSON/')
def itemsJSON(category_id):
    items = db_items(category_id)
    return jsonify(items=[item.serialize for item in items])


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON/')
def itemJSON(category_id, item_id):
    item = db_item(item_id)
    return jsonify(CategoryItem=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
