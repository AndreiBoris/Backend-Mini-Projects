from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')
# makes the connection between our class definitions and corresponding tables in
# the database
Base.metadata.bind = engine
# A link of communication between our code executions and the engine created above
DBSession = sessionmaker(bind = engine)
# In order to create, read, update, or delete information on our database,
# SQLAlchemy uses sessions. These are basically just transactions. WE can write
# a bunch of commands and only send them when necessary.
#
# You can call methods from within session (below) to make changes to the
# database. This provides a staging zone for all objects loaded into the
# database session object. Until we call session.commit(), no changes will be
# persisted into the database.
session = DBSession()

myFirstRestaurant = Restaurant(name = "Pizza Plaza")
# staging zone
session.add(myFirstRestaurant)
# add into database
session.commit()

# Check a database to confirm changes
session.query(Restaurant).all()
# This will give hexadecimal location of found objects
cheesepizza = MenuItem(
name = "Cheese Pizza",
description = "Made with all natural goat cheese",
course = "Entree",
price = "$14.99",
restaurant = myFirstRestaurant)

session.add(cheesepizza)
session.commit()
session.query(MenuItem).all()

# Store first result from a query into the Restaurant table
firstResult = session.query(Restaurant).first()
# Access the name column of firstResult
firstResult.name
