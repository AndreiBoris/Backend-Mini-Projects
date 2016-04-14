# Flask web framework
from flask import Flask
# The name of the running application is the argument we pass to the instance
# of Flask
app = Flask(__name__)

# List all the restaurants
@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    return 'Here is a list of all of our restaurants.'

# Add a new restaurant
@app.route('/restaurant/new')
def newRestaurant():
    return 'Here, we can create a new restaurant.'

# Edit existing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
    return 'Here we can edit restaurant number %d' % restaurant_id

# Delete existing restaurant
@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    return 'Are you use you want to delete restaurant number %d' % restaurant_id

# List all menu items in a particular restaurant
@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    return 'Here is a list of all the menu items for restaurant number %d' % restaurant_id

# Add a new menu item for a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/new')
def newMenuItem(restaurant_id):
    return 'Here we can add a new item to restaurant %d' % restaurant_id

# Edit existing menu item in a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/edit')
def editMenuItem(restaurant_id, item_id):
    return 'Here we can edit item %d in restaurant %d' % (item_id, restaurant_id)

# Delete existing menu item in a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/delete')
def deleteMenuItem(restaurant_id, item_id):
    return 'Are you sure you want to delete item %d in restaurant %d' % (item_id, restaurant_id)


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
