from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///itemlist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Connect using google account
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Disconnect from google, revoke a current user's token, reset login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API to view all Categories
@app.route('/api/categories/')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories = [c.serialize for c in categories])


# JSON API to view Category information
@app.route('/api/categories/<string:category_name>/')
def categoryJSON(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = category.id).all()
    return jsonify(Items = [i.serialize for i in items])


# JSON API to view Item information
@app.route('/api/categories/<string:category_name>/<string:item_name>/')
def itemJSON(category_name, item_name):
    item = session.query(Item).filter_by(name = item_name).one()
    return jsonify(Item = item.serialize)


@app.route('/')
@app.route('/categories/')
def show_categories():
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('categories.html', categories = categories)

@app.route('/categories/new/', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        new_category = Category(name = request.form['name'])
        session.add(new_category)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('new_category.html')

@app.route('/categories/<string:category_name>/edit/', methods=['GET', 'POST'])
def edit_category(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
        session.add(category)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('edit_category.html', category = category)

@app.route('/categories/<string:category_name>/delete/', methods=['GET', 'POST'])
def delete_category(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('delete_category.html', category = category)

@app.route('/categories/<string:category_name>/')
def show_items(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = category.id)
    return render_template('categories.html', categories = categories, category = category, items = items)

@app.route('/categories/<string:category_name>/new/', methods=['GET', 'POST'])
def new_item(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        item = Item(name = request.form['name'], category_id = category.id)
        session.add(item)
        session.commit()
        return redirect(url_for('show_items', category_name = category_name))
    else:
        return render_template('new_item.html', category_name = category_name)

@app.route('/categories/<string:category_name>/<string:item_name>/edit/', methods=['GET', 'POST'])
def edit_item(category_name, item_name):
    item = session.query(Item).filter_by(name = item_name).one()
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        session.add(item)
        session.commit()
        return redirect(url_for('show_items', category_name = category_name))
    else:
        return render_template('edit_item.html', category_name = category_name, item = item)

@app.route('/categories/<string:category_name>/<string:item_name>/delete/', methods=['GET', 'POST'])
def delete_item(category_name, item_name):
    item = session.query(Item).filter_by(name = item_name).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('show_items', category_name = category_name))
    else:
        return render_template('delete_item.html', category_name = category_name, item = item)

if __name__ == '__main__':
    app.secret_key = '7)o!a(k)wmgv)bxd)x44cvm0v=pc2&pfdwu45&3lrgp!p^+'
    app.debug = True
    app.run(host='0.0.0.0', port = 8000)
