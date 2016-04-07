# functions and variables to manipulate parts of python runtime environment
import sys

# Will help with Mapper code
from sqlalchemy import\
Column, ForeignKey, Integer, String

# Used in config and class code
from sqlalchemy.ext.declarative import\
declarative_base

# for mapper ForeignKey relationships
from sqlalchemy.orm import relationship

# For configuration code at the end of the file
from sqlalchemy import create_engine

# this will let SQLAlchemy know that our classes are special SQLAlchemy classes
# that correspond to tables in our SQL database
Base = declarative_base()

class Restaurant(Base):

    __tablename__ = 'restaurant'

    name = Column(
    String(80), nullable = False)

    id = Column(
    Integer, primary_key = True)

class MenuItem(Base):

    __tablename__ = 'menu_item'

    name = Column(String(80), nullable = False)

    id = Column(Integer, primary_key = True)

    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

######## insert at end of file ############

engine = create_engine(
'sqlite:///restaurantmenu.db')

# Adds classes as new tables in our database
Base.metadata.create_all(engine)
