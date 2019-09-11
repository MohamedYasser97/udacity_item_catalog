#!/usr/bin/env python

from sqlalchemy import create_engine, Column, ForeignKey, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):  # Defining the user entity
    """Defines the User entity in the database with all its properties and
    methods."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    pic = Column(String(500))

    # Preparing output for json endpoint
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'pic': self.pic
        }


class Category(Base):  # Defining category entity
    """Defines the Category entity in the database with all its properties and
    methods."""

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    # Setting up relation with (user) table
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Preparing output for json endpoint
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Item(Base):  # Defining item entity
    """Defines the Item entity in the database with all its properties and
    methods."""

    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500))

    # Setting up relation with both category and user tables
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Preparing output for json endpoint
    @property
    def serialize(self):
        return {
            'cat_id': self.category_id,
            'description': self.description,
            'id': self.id,
            'name': self.name
        }


engine = create_engine('sqlite:///item_catalog.db', pool_pre_ping=True,
                       connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
