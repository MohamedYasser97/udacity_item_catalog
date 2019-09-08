#!/usr/bin/env python

import json

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from flask import make_response

from db_setup import Base, User, Category, Item

# Connecting to the existing database
engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine


# Creating session for future queries (NOT THE SAME AS login_session!)
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Returns user id given their email
def get_uid(email):
    try:
        user = session.query(User).filter_by(email=email).one()
    except NoResultFound:
        user = None

    return user


# Creates a user instance in the database and returns their id
def create_user(session_data):
    new_user = User(name=session_data['name'], email=session_data['email'], pic=session_data['pic'])
    session.add(new_user)
    session.commit()

    user = session.query(User).filter_by(email=session_data['email']).one()

    return user.id


# Builds and returns a custom HTTP response
def build_response(message, status, content_type='application/json'):
    res = make_response(json.dumps(message), status)
    res.headers['Content-Type'] = content_type
    return res
