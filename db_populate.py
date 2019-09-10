#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, User, Category, Item

# Connecting to the existing database
engine = create_engine('sqlite:///item_catalog.db', pool_pre_ping=True,
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

# Creating session for future queries
DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(name='Tyler Durden(the cool one)', email='tylerdurden@mail.com',
             pic='https://vignette.wikia.nocookie.net/fightclub/images/d/d3'
                 '/Tyler-Durden.jpg/revision/latest?cb=20140513065629')
session.add(user1)
session.commit()

user2 = User(name='Marla Singer', email='highcat420@rocketmail.com',
             pic='https://data.whicdn.com/images/58991808/large.jpg')
session.add(user2)
session.commit()

user3 = User(name='Tyler Durden', email='tylerdurdenx@hotmail.com',
             pic='https://cumuloquoise.files.wordpress.com/2014/04/'
                 'fight_club_norton_5.jpg')
session.add(user3)
session.commit()

category1 = Category(name='sports', user=user1)
session.add(category1)
session.commit()

category2 = Category(name='clothes', user=user2)
session.add(category2)
session.commit()

category3 = Category(name='books', user=user3)
session.add(category3)
session.commit()

item1 = Item(name='football', description='Y\'know..just kick it man.',
             user=user1, category=category1)
session.add(item1)
session.commit()

item2 = Item(name='bat', description='Great for kicking baseballs!',
             user=user3, category=category1)
session.add(item2)
session.commit()

item3 = Item(name='dress', description='It looks great on me!',
             user=user2, category=category2)
session.add(item3)
session.commit()

item4 = Item(name='trousers', description='We all need them.',
             user=user3, category=category2)
session.add(item4)
session.commit()

item5 = Item(name='shirt', description='Comes in many colours and shapes.',
             user=user3, category=category2)
session.add(item5)
session.commit()

item6 = Item(name='cap', description='Protects from the sun',
             user=user1, category=category2)
session.add(item6)
session.commit()

item7 = Item(name='war and peace', description='Tolstoy said War and Peace '
                                               'is "not a novel, even less '
                                               'is it a poem, and still less '
                                               'a historical chronicle." '
                                               'Large sections, especially '
                                               'the later chapters, '
                                               'are philosophical discussion '
                                               'rather than narrative. '
                                               'Tolstoy also said that the '
                                               'best Russian literature does '
                                               'not conform to standards and '
                                               'hence hesitated to call War '
                                               'and Peace a novel. Instead, '
                                               'he regarded Anna Karenina as '
                                               'his first true novel. The '
                                               'Encyclopedia Britannica '
                                               'states: "It can be argued '
                                               'that no single English novel '
                                               'attains the universality of '
                                               'the Russian writer Leo '
                                               'Tolstoy\'s War and Peace"',
             user=user3, category=category3)
session.add(item7)
session.commit()

item8 = Item(name='men at war', description='"Men at War" edited by Ernest '
                                            'Hemingway is an imposing '
                                            'anthology (over 1000 pages and '
                                            'over 80 stories) of men in '
                                            'battle conditions. The range of '
                                            'time is from Biblical to the '
                                            'middle of World War II, when it '
                                            'was published. The bulk of the '
                                            'conflicts described come from '
                                            'the Napoleonic wars and World '
                                            'War I. Most are true, '
                                            'first person accounts, but some '
                                            'fiction is included.',
             user=user1, category=category3)
session.add(item8)
session.commit()

item9 = Item(name='art of war', description='The Art of War is an ancient '
                                            'Chinese military treatise '
                                            'dating from the Late Spring and '
                                            'Autumn Period. The work, '
                                            'which is attributed to the '
                                            'ancient Chinese military '
                                            'strategist Sun Tzu, is composed '
                                            'of 13 chapters. Each one is '
                                            'devoted to an aspect of warfare '
                                            'and how it applies to military '
                                            'strategy and tactics.',
             user=user3, category=category3)
session.add(item9)
session.commit()

item10 = Item(name='boxing gloves', description='They\re used to play boxing',
              user=user2, category=category1)
session.add(item10)
session.commit()
