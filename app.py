#!/usr/bin/env python

import json
import random
import string
import requests

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

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
@app.route('/catalog/')
def show_all():
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
            res = make_response(json.dumps('Unauthorized request source.'), 401)
            res.headers['Content-Type'] = 'application/json'
            return res

        one_time_auth = request.data  # This one-time code will be exchanged for an access token from Google
        # TODO continue login logic
