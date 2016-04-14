# Flask web framework
from flask import Flask, render_template, url_for, request, redirect
# The name of the running application is the argument we pass to the instance
# of Flask
app = Flask(__name__)

# SQLAlchemy to talk to database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Database tables defined in database_setup.py
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

# decorator. It warps our function in the app.route function that Flask has
# created. So if either of these routes get sent from the browser, the function
# that we defined below them, HelloWorld, gets executed. Decorators call the
# function that follows it whenever the server gets a URL request that matches
# its argument.
@app.route('/')
@app.route('/restaurants/<int:restaurant_id>')
def restaurantMenu(restaurant_id):
    # Get first restaurant in the database
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    # Get all the menu items that are in that first restaurant
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return render_template('menu.html', restaurant=restaurant, items = items)

# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'],
                            restaurant_id = restaurant_id,
                            description = request.form['description'],
                            price = request.form['price'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else: # got a GET request
        return render_template('newmenuitem.html', restaurant_id = restaurant_id)

# Task 2: Create route for editMenuItem function here


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        editedItem.name = request.form['name']
        editedItem.description = request.form['description']
        editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else: # got a GET request
        return render_template('editmenuitem.html',
                                restaurant_id = restaurant_id,
                                menu_id = menu_id,
                                i = editedItem)

# Task 3: Create a route for deleteMenuItem function here


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    deleteTargetItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(deleteTargetItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else: # got a GET request
        return render_template('deletemenuitem.html',
                                restaurant_id = restaurant_id,
                                menu_id = menu_id,
                                i = deleteTargetItem)

# The application run by the Python interpretor gets the name __main__
# Only run when this script is directly run, not imported.
if __name__ == '__main__':
    # Reload server each time there is a code change
    app.debug = True
    # By default the server is only accessible from the host machine and not
    # from any other computer. This is the default because a user running
    # debugging mode on my application can execute arbitrary python code on my
    # computer. So its a safety thing. Here, we make the server publically
    # available due to this being run on a vagrant environment
    app.run(host = '0.0.0.0', port = 5000)
