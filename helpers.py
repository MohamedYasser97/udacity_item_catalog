#!/usr/bin/env python

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from flask import make_response

from db_setup import Base, User, Category, Item

# Connecting to the existing database
engine = create_engine('sqlite:///item_catalog.db', pool_pre_ping=True,
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine


# Creating session for future queries (NOT THE SAME AS login_session!)
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Returns user id given their email
def get_uid(email):
    """Returns a user's id given their email."""

    try:
        user = session.query(User).filter_by(email=email).one()
    except NoResultFound:
        return None

    return user.id


# Creates a user instance in the database and returns their id
def create_user(session_data):
    """Creates a new user in the database."""

    new_user = User(name=session_data['name'], email=session_data['email'],
                    pic=session_data['pic'])
    session.add(new_user)
    session.commit()

    user = session.query(User).filter_by(email=session_data['email']).first()

    return user.id


# Builds and returns a custom HTTP response
def build_response(message, status, content_type='application/json'):
    """Builds a response with its headers and content."""

    res = make_response(json.dumps(message), status)
    res.headers['Content-Type'] = content_type
    return res


# Checks if a category exists
def category_exists(cat_name):
    """Checks if a certain category exists."""

    category = session.query(Category).filter_by(name=cat_name).first()
    if category:
        return True

    return False


# Checks if an item exists
def item_exists(item_name):
    """Checks if a certain item exists."""

    item = session.query(Item).filter_by(name=item_name).first()
    if item:
        return True

    return False


# Gets the id of a category given its name
def get_category_id(name):
    """Returns the id of a category given its name."""

    category = session.query(Category).filter_by(name=name).first()
    return category.id
