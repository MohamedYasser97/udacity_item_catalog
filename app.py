#!/usr/bin/env python

import json
import random
import string
import requests
import httplib2

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

import helpers
from db_setup import Base, User, Category, Item

app = Flask(__name__)

# Getting the client id used for 3rd-party login
CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

# Connecting to the existing database
engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine

# Creating session for future queries (NOT THE SAME AS login_session!)
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Route for the homepage
@app.route('/')
@app.route('/catalog')
def home():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc('id')).limit(10).all()  # Only get the latest 10 results

    return render_template('index.html', categories=categories, items=items)


# Both login routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':  # Generate unique session token and rendering login prompt
        state_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(32))
        login_session['state'] = state_token  # Keeping a copy for later comparison to ensure no forgery happens

        return render_template('login.html', state=state_token, client_id=CLIENT_ID)

    else:  # Testing the 1-time auth code the user got from Google to login user
        if request.args.get('state') != login_session['state']:  # Request was forged
            return helpers.build_response('Unauthorized request source.', 401)

        one_time_auth = request.data  # This one-time code will be exchanged for an access token from Google

        # Exchanging the one-time auth with user's Google credentials
        try:
            oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            creds = oauth_flow.step2_exchange(one_time_auth)
        except FlowExchangeError:
            return helpers.build_response('Token exchange error.', 401)

        # Testing exchanged credentials
        access_token = creds.access_token
        target_url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        req = httplib2.Http()
        result = json.loads(req.request(target_url, 'GET')[1])

        if result.get('error'):
            return helpers.build_response(result.get('error'), 500)

        google_id = creds.id_token['sub']
        if result['user_id'] != google_id:
            return helpers.build_response(result.get('User and token IDs are not matching.'), 401)

        if result['issued_to'] != CLIENT_ID:
            return helpers.build_response(result.get('Token\'s target client ID doesn\'t match this client.'), 401)

        # If we got here then the OAuth process is successful
        valid_access_token = login_session.get('access_token')
        valid_google_id = login_session.get('gplus_id')

        # Checking if user is already logged in
        if valid_access_token and google_id == valid_google_id:
            return helpers.build_response('User already logged in.', 200)

        login_session['access_token'] = creds.access_token
        login_session['gplus_id'] = google_id

        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        userinfo_res = requests.get(userinfo_url, params={'access_token': creds.access_token, 'alt': 'json'})

        user_data = userinfo_res.json()

        login_session['email'] = user_data['email']
        login_session['name'] = user_data['name']
        login_session['pic'] = user_data['picture']

        # Creating user if hasn't logged in before
        user_id = helpers.get_uid(user_data['email'])
        if not user_id:
            user_id = helpers.create_user(login_session)

        login_session['user_id'] = user_id

        flash('Welcome back, %s!' % login_session['username'])

        return redirect((url_for('home')))


# Disconnects from google before logging out
def google_disconnect():
    access_token = login_session.get('access_token')

    if not access_token:
        return helpers.build_response('User already logged out.', 401)

    target_url = ('https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token)
    req = httplib2.Http()
    result = req.request(target_url, 'GET')[0]

    if result['status'] == '200':
        return helpers.build_response('User successfully logged out.', 200)
    else:
        return helpers.build_response('Failed to log out user.', 400)


# Logs out of website
@app.route('/logout', methods=['POST'])
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


if __name__ == '__main__':
    app.secret_key = 'Life only makes sense if you force it to.'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
