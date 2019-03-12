#!/usr/bin/env python

# Import needed functions / modules
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import Base, User, CatalogCategory, CatalogItem

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import random
import string
import httplib2
import json
import requests

# Create the flask app
app = Flask(__name__)

# Connect to the database and create a session
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Setup some variables needed for Google Sign In
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APP_NAME = "School Catalog App"

##################
# Begin Auth Code
# This code is copied from the course code with minor alterations.
# Setup a session state so we can verify the info is from us.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Authenticate the user with Google Sign In
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Does the session token match what we have?
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Get the  authorization code from the data
    code = request.data

    # Try to get the credentials object
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])

    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # output  = '<h1>Welcome, '
    # output += login_session['username']
    # output += '!</h1>'
    # output += '<img src="'
    # output += login_session['picture']
    # output += ' "> '
    # print "done!"
    return "Success"


# Disconnect
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        # We're not logged in...send back home.
        return redirect(url_for('showHome'))
    url = 'https://accounts.google.com/o/oauth2/revoke?token='
    url += login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # If success set a flash msg and redirect to home.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("you are now logged out")
        return redirect(url_for('showHome'))
    else:
        # If not successful stop and kick back an error.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
# End Auth Code


# Define local user mgmt functions
# This code is copied from the course code with minor alterations.
def createUser(login_session):
    """Function - User Mgmt - Accept login session object and query DB for
    User ID based on session email value."""
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Function - User Mgmt -
    Accept ID for user info in DB return user object."""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Function - User Mgmt - Accept email address and check DB for user data.
    Return User ID if found else return None"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None
# End Local user functions
##################

# Home page - shows the categories
@app.route('/')
@app.route('/home')
def showHome():
    categoryList = session.query(CatalogCategory).all()
    # Pass login_session so we can show the correct login/logout
    return render_template('home.html', login_session=login_session,
                           categoryList=categoryList)


# Category page.
#   Shows the items in the category and if logged in show an add link.
@app.route('/<string:category_name>')
def showItems(category_name):
    category = \
        session.query(CatalogCategory).filter_by(name=category_name).first()
    itemList = \
        session.query(CatalogItem).filter_by(category_id=category.id).all()
    # Pass login_session so we can show the correct login/logout
    return render_template('category.html', login_session=login_session,
                           category=category, itemList=itemList)


# CRUD: C
# Show the form to add an item or add it if we get a post.
# Must be logged in for this function.
@app.route('/<string:category_name>/newItem', methods=['GET', 'POST'])
def addItem(category_name):
    category = \
        session.query(CatalogCategory).filter_by(name=category_name).first()
    if 'user_id' in login_session:
        if request.method == 'POST':
            newItem = CatalogItem(name=request.form['ItemName'],
                                  description=request.form['ItemDescription'],
                                  category_id=category.id,
                                  user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            flash('New Item Added: %s' % newItem.name)
            return redirect(url_for('showItems', category_name=category.name))
        else:
            return render_template('item_add.html',
                                   login_session=login_session,
                                   category=category)
    else:
        response = jsonify({'message': 'Shoundn\'t you be logged in?'})
        return response, 401


# CRUD: R
# Show the details for the selected item.
#   If logged in as the item owner show edit/delete links.
@app.route('/<string:category_name>/<int:item_id>')
def showItem(category_name, item_id):
    category = \
        session.query(CatalogCategory).filter_by(name=category_name).first()
    item = session.query(CatalogItem).filter_by(id=item_id).first()
    # Pass login_session so we can show the correct login/logout
    return render_template('item.html', login_session=login_session,
                           category=category, item=item)

# CRUD: U
# Show the form to edit an item or edit it if we get a post.
# Must be logged in as the item owner for this function.
@app.route('/<string:category_name>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_name, item_id):
    category = \
        session.query(CatalogCategory).filter_by(name=category_name).first()
    item = session.query(CatalogItem).filter_by(id=item_id).first()
    if item.user_id == login_session['user_id']:
        if request.method == 'POST':
            if request.form['ItemName']:
                item.name = request.form['ItemName']
            if request.form['ItemDescription']:
                item.description = request.form['ItemDescription']
            session.add(item)
            session.commit
            flash('%s has been updated.' % item.name)
            return redirect(url_for('showItem', category_name=category.name,
                                    item_id=item_id))
        else:
            return render_template('item_edit.html',
                                   login_session=login_session,
                                   category=category, item=item)
    else:
        response = jsonify({'message': 'Are you lost?'})
        return response, 401


# CRUD: D
# Show the form to delete an item or delete it if we get a post.
# Must be logged in as the item owner for this function.
@app.route('/<string:category_name>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    category = \
        session.query(CatalogCategory).filter_by(name=category_name).first()
    item = session.query(CatalogItem).filter_by(id=item_id).first()
    if item.user_id == login_session['user_id']:
        if request.method == 'POST':
            temp_item_name = item.name
            session.delete(item)
            session.commit
            flash('%s has been deleted.' % temp_item_name)
            return redirect(url_for('showItems', category_name=category.name))
        else:
            return render_template('item_delete.html',
                                   login_session=login_session,
                                   category=category,
                                   item=item)
    else:
        response = jsonify({'message': 'You\'re not supposed to be here...'})
        return response, 401


# JSON API Endpoints
# Show the categories
@app.route('/catagory.json')
def jsonCategoryDump():
    categories = session.query(CatalogCategory).all()
    return jsonify(Category=[c.serialize for c in categories])

# Show the items in the specified category
@app.route('/<string:category_name>/items.json')
def jsonCatagoryItemsDump(category_name):
    category = \
        session.query(CatalogCategory).filter_by(name=category_name).first()
    items = session.query(CatalogItem).filter_by(category_id=category.id).all()
    return jsonify(CatalogItems=[i.serialize for i in items])

# Show the details of the selected item
# Currently addressing an item by id does not require the
#  category id/name so we don't need to look up the
#  category first
@app.route('/<string:category_name>/<int:item_id>/item.json')
def jsonItem(category_name, item_id):
    item = session.query(CatalogItem).filter_by(id=item_id).first()
    return jsonify(CatalogItem=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
