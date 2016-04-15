# Flask web framework
from flask import Flask, url_for, render_template, redirect, request, jsonify, flash
# The name of the running application is the argument we pass to the instance
# of Flask
app = Flask(__name__)


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
# SQLAlchemy uses sessions. These are basically just transactions. We can write
# a bunch of commands and only send them when necessary.
#
# You can call methods from within session (below) to make changes to the
# database. This provides a staging zone for all objects loaded into the
# database session object. Until we call session.commit(), no changes will be
# persisted into the database.
session = DBSession()

# List all the restaurants
@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants )

# Add a new restaurant
@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(name = request.form['name'])
        session.add(newRestaurant)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else: # GET
        return render_template('newrestaurant.html')

# Edit existing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    selectedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        newName = request.form['name']
        selectedRestaurant.name = newName
        session.add(selectedRestaurant)
        session.commit()
        flashMessage = 'Restaurant name changed to %s!' % newName
        flash(flashMessage)
        return redirect(url_for('showRestaurants'))
    else: # GET
        return render_template('editrestaurant.html', r=selectedRestaurant)

# Delete existing restaurant
@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    selectedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(selectedRestaurant)
        flashMessage = 'Deleted restaurant %s' % selectedRestaurant.name
        flash(flashMessage)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else: # GET
        return render_template('deleterestaurant.html', r=selectedRestaurant)

# List all menu items in a particular restaurant
@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    selectedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return render_template('menu.html', r=selectedRestaurant, items=items)

# Add a new menu item for a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    selectedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        newMenuItem = MenuItem(name = request.form['name'],
                               price = request.form['price'],
                               description = request.form['description'],
                               restaurant_id = restaurant_id)
        session.add(newMenuItem);
        session.commit()
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else: # GET
        return render_template('newmenuitem.html', r=selectedRestaurant)

# Edit existing menu item in a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, item_id):
    selectedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    selectedItem = session.query(MenuItem).filter_by(id = item_id).one()
    if request.method == 'POST':
        selectedItem.name = request.form['name']
        selectedItem.price = request.form['price']
        selectedItem.description = request.form['description']
        session.add(selectedItem)
        session.commit()
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else: # GET
        return render_template('editmenuitem.html', r=selectedRestaurant, i=selectedItem)

# Delete existing menu item in a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, item_id):
    selectedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    selectedItem = session.query(MenuItem).filter_by(id = item_id).one()
    if request.method == 'POST':
        session.delete(selectedItem)
        session.commit()
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else: # GET
        return render_template('deletemenuitem.html', r = selectedRestaurant, i = selectedItem)

# Get JSON of all of the restaurants
@app.route('/JSON')
@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[r.serialize for r in restaurants])

@app.route('/restaurant/<int:restaurant_id>/JSON')
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/JSON')
@app.route('/restaurant/<int:restaurant_id>/<int:item_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, item_id):
    item = session.query(MenuItem).filter_by(id = item_id).one()
    return jsonify(MenuItem = item.serialize)


# The application run by the Python interpretor gets the name __main__
# Only run when this script is directly run, not imported.
if __name__ == '__main__':
    # Flask will use this to create sessions for our users. Make sure it is
    # secure in a production environment
    app.secret_key = 'super_secret_key'
    # Reload server each time there is a code change
    app.debug = True
    # By default the server is only accessible from the host machine and not
    # from any other computer. This is the default because a user running
    # debugging mode on my application can execute arbitrary python code on my
    # computer. So its a safety thing. Here, we make the server publically
    # available due to this being run on a vagrant environment
    app.run(host = '0.0.0.0', port = 8000)
