# Flask web framework
from flask import Flask
# The name of the running application is the argument we pass to the instance
# of Flask
app = Flask(__name__)

@app.route('/')
@app.route('/restaurants')
def restaurants():
    return 'Here is a list of all of our restaurants.'

@app.route('/restaurant/new')
def restaurantNew():
    return 'Here, we can create a new restaurant.'

@app.route('/restaurant/<int:restaurant_id>/edit')
def restaurantEdit(restaurant_id):
    return 'Here we can edit restaurant number %d' % restaurant_id

@app.route('/restaurant/<int:restaurant_id>/delete')
def restaurantDelete(restaurant_id):
    return 'Are you use you want to delete restaurant number %d' % restaurant_id

@app.route('/restaurant/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    return 'Here is a list of all the menu items for restaurant number %d' % restaurant_id

@app.route('/restaurant/<int:restaurant_id>/menu/new')
def menuItemNew(restaurant_id):
    return 'Here we can add a new item to restaurant %d' % restaurant_id

@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/edit')
def menuItemEdit(restaurant_id, item_id):
    return 'Here we can edit item %d in restaurant %d' % (item_id, restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/delete')
def menuItemDelete(restaurant_id, item_id):
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
