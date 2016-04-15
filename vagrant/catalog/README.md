# Menu App

This application is an exercise in creating a Python backend using the
[Flask](http://flask.pocoo.org/) web framework.

### View

First, [log in to the virtual machine](https://github.com/AndreiCommunication/Backend-Mini-Projects#steps-to-follow)
and then do the following:

* Enter the `catalog` directory:

```
$ cd /vagrant/catalog
```

* Host the website on local host, port 8000

```
$ python finalproject.py
```

* Open the url `http://localhost:8000` in your browser to view. [Or click here.](http://localhost:8000)

### Interact

You can add restaurants to the database, edit restaurants or delete them. If
you click on a restaurant name you see the menu items that are there, you can
add, edit or delete those as well. After completing an action a message will
flash to indicate that the action was performed.

The data will all persist in the database file `restaurantmenu.db`
