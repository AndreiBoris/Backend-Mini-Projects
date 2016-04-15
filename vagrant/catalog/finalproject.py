# Flask web framework
from flask import Flask, url_for, render_template
# The name of the running application is the argument we pass to the instance
# of Flask
app = Flask(__name__)

#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]

#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree', 'id':'1'}



# List all the restaurants
@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    # TODO: Get the restaurans actually being asked for, not placeholders
    return render_template('restaurants.html', restaurants=restaurants )

# Add a new restaurant
@app.route('/restaurant/new')
def newRestaurant():
    return render_template('newrestaurant.html')

# Edit existing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
    # TODO: Get the restaurant that is actually being asked for, not placeholder
    return render_template('editrestaurant.html', r=restaurant)

# Delete existing restaurant
@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    # TODO: Get the restaurant that is actually being asked for, not placeholder
    return render_template('deleterestaurant.html', r=restaurant)

# List all menu items in a particular restaurant
@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    # TODO: Replace placeholders with an actual restaurant and items
    return render_template('menu.html', r=restaurant, items=items)

# Add a new menu item for a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/new')
def newMenuItem(restaurant_id):
    # TODO: Replace placeholder
    return render_template('newmenuitem.html', r=restaurant)

# Edit existing menu item in a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/edit')
def editMenuItem(restaurant_id, item_id):
    # TODO: Replace placeholders
    return render_template('editmenuitem.html', r=restaurant, i=item)

# Delete existing menu item in a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/delete')
def deleteMenuItem(restaurant_id, item_id):
    # TODO: Replace placeholders
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
