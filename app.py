#!/usr/bin/env python

import json
import random
import string

import httplib2
import requests
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

import helpers
from db_setup import Base, User, Category, Item

app = Flask(__name__)

# Getting the client id used for 3rd-party login
CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web'][
    'client_id']

# Connecting to the existing database
engine = create_engine('sqlite:///item_catalog.db', pool_pre_ping=True,
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

# Creating session for future queries (NOT THE SAME AS login_session!)
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Route for the homepage
@app.route('/')
@app.route('/catalog')
def home():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc('id')).limit(
        10).all()  # Only get the latest 10 results

    return render_template('index.html', categories=categories, items=items)


# Both login routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Generate unique session token and rendering login prompt
        state_token = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for i in
            range(32))

        # Keeping a copy for later comparison to ensure no forgery happens
        login_session['state'] = state_token

        return render_template('login.html', state=state_token,
                               client_id=CLIENT_ID)

    else:
        # Testing the 1-time auth code the user got from Google to login user

        # Request was forged
        if request.args.get('state') != login_session['state']:
            return helpers.build_response('Unauthorized request source.', 401)

        # This one-time code will be exchanged for an access token from Google
        one_time_auth = request.data

        # Exchanging the one-time auth with user's Google credentials
        try:
            oauth_flow = flow_from_clientsecrets('client_secret.json',
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            creds = oauth_flow.step2_exchange(one_time_auth)
        except FlowExchangeError:
            return helpers.build_response('Token exchange error.', 401)

        # Testing exchanged credentials
        access_token = creds.access_token
        target_url = (
                'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token'
                '=%s' % access_token)
        req = httplib2.Http()
        result = json.loads(req.request(target_url, 'GET')[1])

        if result.get('error') is not None:
            return helpers.build_response(result.get('error'), 500)

        google_id = creds.id_token['sub']
        if result['user_id'] != google_id:
            return helpers.build_response(
                result.get('User and token IDs are not matching.'), 401)

        if result['issued_to'] != CLIENT_ID:
            return helpers.build_response(result.get(
                'Token\'s target client ID doesn\'t match this client.'), 401)

        # If we got here then the OAuth process is successful
        valid_access_token = login_session.get('access_token')
        valid_google_id = login_session.get('gplus_id')

        # Checking if user is already logged in
        if valid_access_token and google_id == valid_google_id:
            return helpers.build_response('User already logged in.', 200)

        login_session['access_token'] = creds.access_token
        login_session['gplus_id'] = google_id

        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        userinfo_res = requests.get(userinfo_url,
                                    params={'access_token': creds.access_token,
                                            'alt': 'json'})

        user_data = userinfo_res.json()

        login_session['email'] = user_data['email']
        login_session['name'] = user_data['name']
        login_session['pic'] = user_data['picture']

        # Creating user if hasn't logged in before
        user_id = helpers.get_uid(user_data['email'])
        if not user_id:
            user_id = helpers.create_user(login_session)

        login_session['user_id'] = user_id

        flash('Welcome back, %s!' % login_session['name'])

        return redirect((url_for('home')))


# Disconnects from google before logging out
def google_disconnect():
    access_token = login_session.get('access_token')

    if not access_token:
        return helpers.build_response('User already logged out.', 401)

    target_url = (
            'https://accounts.google.com/o/oauth2/revoke?\
            token=%s' % access_token)
    req = httplib2.Http()
    result = req.request(target_url, 'GET')[0]

    if result['status'] == '200':
        return helpers.build_response('User successfully logged out.', 200)
    else:
        return helpers.build_response('Failed to log out user.', 400)


# Logs out of website
@app.route('/logout')
def logout():
    if 'name' in login_session:
        google_disconnect()

        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['email']
        del login_session['name']
        del login_session['pic']
        del login_session['user_id']

        flash('Successfully logged out!')

        return redirect(url_for('home'))

    else:
        flash('You are already logged out!')

        return redirect(url_for('home'))


# Route for creating categories
@app.route('/catalog/category/new', methods=['GET', 'POST'])
def create_category():
    if 'name' not in login_session:
        flash('You must be logged in to do that!')
        return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('new_cat.html')
    else:
        if request.form['cat_name'] == '':
            flash('Invalid category name!')
            return redirect(url_for('create_category'))

    # A valid category name was inserted but need to check if already exists
    category = session.query(Category).filter_by(
        name=request.form['cat_name'].lower()).first()
    if category:
        flash('This category already exists!')
        return redirect(url_for('show_category', category_name=category.name))

    # Creating new category
    new_cat = Category(name=request.form['cat_name'].lower(),
                       user_id=login_session['user_id'])
    session.add(new_cat)
    session.commit()

    flash('Category successfully created!')
    return redirect(url_for('show_category', category_name=new_cat.name))


# Route for creating items
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def create_item():
    if 'name' not in login_session:
        flash('You must be logged in to do that!')
        return redirect(url_for('login'))
    elif request.method == 'GET':
        categories = session.query(Category).all()
        return render_template('new_item.html', categories=categories)
    else:
        if request.form['name'] == '' or request.form['desc'] == '' or \
                request.form['cat'] == '':
            flash('Invalid item name or description!')
            return redirect(url_for('create_item'))

        # Check if item already exists
        item = session.query(Item).filter_by(
            name=request.form['name'].lower()).first()
        if item:
            flash('Item already exists!')
            return redirect(url_for('show_item', item_name=item.name))

        new_item = Item(name=request.form['name'].lower(),
                        category_id=request.form['cat'],
                        description=request.form['desc'],
                        user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        flash('Item successfully created!')
        return redirect(url_for('show_item', item_name=new_item.name))


# Route for showing a category
@app.route('/catalog/category/<category_name>')
def show_category(category_name):
    if helpers.category_exists(category_name):
        category = session.query(Category).filter_by(
            name=category_name).first()
        items = session.query(Item).filter_by(category_id=category.id).all()

        owners = []
        for item in items:
            item_owner = session.query(User).filter_by(id=item.user_id).first()
            owners.append(item_owner)

        return render_template('view_cat.html', category=category, items=items,
                               owners=owners, len=len(items))

    else:
        flash('This category doesn\'t exist!')
        return redirect(url_for('home'))


# Route for showing an item
@app.route('/catalog/item/<item_name>')
def show_item(item_name):
    if helpers.item_exists(item_name):
        item = session.query(Item).filter_by(name=item_name).first()
        owner = session.query(User).filter_by(id=item.user_id).first()
        category = session.query(Category).filter_by(
            id=item.category_id).first()
        return render_template('view_item.html', item=item, owner=owner,
                               category=category)
    else:
        flash('This item doesn\'t exist!')
        return redirect(url_for('home'))


# Route for showing a user's profile
@app.route('/user/<int:user_id>')
def show_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        categories = session.query(Category).filter_by(user_id=user.id).all()
        items = session.query(Item).filter_by(user_id=user.id).all()
        return render_template('view_user.html', user=user,
                               categories=categories, items=items)
    else:
        flash('This user doesn\'t exist!')
        return redirect(url_for('home'))


# Route for updating an item
@app.route('/catalog/item/<item_name>/edit', methods=['GET', 'POST'])
def edit_item(item_name):
    # Checks if logged in
    if 'name' not in login_session:
        flash('You must be logged in to do that!')
        return redirect(url_for('login'))

    # Checks if item exists
    if not helpers.item_exists(item_name):
        flash('This item doesn\'t exist!')
        return redirect(url_for('home'))

    item = session.query(Item).filter_by(name=item_name).first()

    # Checks user authority
    if login_session['user_id'] != item.user_id:
        flash('You are not authorized to do that!')
        return redirect(url_for('home'))

    if request.method == 'GET':
        categories = session.query(Category).all()
        return render_template('edit_item.html', item=item,
                               categories=categories)
    else:
        if request.form['name']:
            item.name = request.form['name'].lower()
        if request.form['desc']:
            item.description = request.form['desc']
        if request.form['cat_id']:
            item.category_id = request.form['cat_id']

        session.add(item)
        session.commit()

        flash('Item was successfully updated!')
        return redirect(url_for('show_item', item_name=item.name))


# Route for deleting an item
@app.route('/catalog/item/<item_name>/delete', methods=['GET', 'POST'])
def delete_item(item_name):
    # Checks if logged in
    if 'name' not in login_session:
        flash('You must be logged in to do that!')
        return redirect(url_for('login'))

    # Checks if item exists
    if not helpers.item_exists(item_name):
        flash('This item doesn\'t exist!')
        return redirect(url_for('home'))

    item = session.query(Item).filter_by(name=item_name).first()

    # Checks user authority
    if login_session['user_id'] != item.user_id:
        flash('You are not authorized to do that!')
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('delete_item.html', item=item)
    else:
        session.delete(item)
        session.commit()

        flash('Item successfully deleted!')
        return redirect(url_for('home'))


# Route for deleting a category (can't delete a category unless it's empty)
@app.route('/catalog/category/<category_name>/delete', methods=['GET', 'POST'])
def delete_category(category_name):
    # Checks if logged in
    if 'name' not in login_session:
        flash('You must be logged in to do that!')
        return redirect(url_for('login'))

    # Checks if category exists
    if not helpers.category_exists(category_name):
        flash('This category doesn\'t exist!')
        return redirect(url_for('home'))

    category = session.query(Category).filter_by(name=category_name).first()

    # Checks user authority
    if login_session['user_id'] != category.user_id:
        flash('You are not authorized to do that!')
        return redirect(url_for('home'))

    # Checks if category is ready for deletion (empty)
    items = session.query(Item).filter_by(category_id=category.id).all()
    if items:
        flash('You can\'t delete a category that has items!')
        return redirect(url_for('show_category', category_name=category.name))

    # Category is ready for deletion
    if request.method == 'GET':
        return render_template('delete_cat.html', category=category)
    else:
        session.delete(category)
        session.commit()

        flash('Category successfully deleted!')
        return redirect(url_for('home'))


# Route for Creating item with specified category (empty category scenario)
@app.route('/catalog/category/<category_name>/item/new',
           methods=['GET', 'POST'])
def create_item_precat(category_name):
    if 'name' not in login_session:
        flash('You must be logged in to do that!')
        return redirect(url_for('login'))

    if request.method == 'GET':
        predetermined_category = session.query(Category).filter_by(
            name=category_name).first()
        return render_template('new_item.html',
                               predetermined_cat=predetermined_category)
    else:
        if request.form['name'] == '' or request.form['desc'] == '':
            flash('Invalid item name or description!')
            return redirect(url_for('create_item_precat'))

        if helpers.item_exists(request.form['name'].lower()):
            flash('Item already exists!')
            return redirect(
                url_for('show_item', item_name=request.form['name'].lower()))

        new_item = Item(name=request.form['name'].lower(),
                        description=request.form['desc'],
                        category_id=request.form['cat'],
                        user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()

        flash('Item successfully created!')
        return redirect(url_for('show_item', item_name=new_item.name))


# JSON equivalent of the home route
@app.route('/.json')
@app.route('/catalog.json')
def home_json():
    items = session.query(Item).order_by(desc('id')).all()
    categories = session.query(Category).order_by(desc('id')).all()
    return jsonify(items=[item.serialize for item in items],
                   categories=[category.serialize for category in categories])


# JSON equivalent of the show_category route
@app.route('/catalog/category/<category_name>.json')
def show_category_json(category_name):
    if helpers.category_exists(category_name):
        category = session.query(Category).filter_by(
            name=category_name).first()
        items = session.query(Item).filter_by(
            category_id=helpers.get_category_id(category_name)).all()

        return jsonify(category=category.serialize,
                       items=[item.serialize for item in items])

    else:
        return jsonify('Category doesn\'t exist!')


if __name__ == '__main__':
    app.secret_key = 'Life only makes sense if you force it to.'
    app.debug = False
    app.run(host='0.0.0.0', port=8000)
