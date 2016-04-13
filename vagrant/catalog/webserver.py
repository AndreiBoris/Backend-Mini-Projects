import re

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

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
# Common gateway interface library to decipher messages sent from server
import cgi

template_FORM = '<form method="POST" enctype="multipart/form-data" action="\
    /hello"><h2>What would you like me to say?</h2><input name="message"\
    type="text"><input type="submit" value="Submit"></form>'

template_HTML_OPEN = '<body><html>'

template_HTML_CLOSE = '</body></html>'

template_RESTAURANT_OPEN = '<div>'

template_LINE_BREAK = '<br />'

template_RESTAURANT = '''\
<div>
    %(name)s
    <br />
    <a href="/restaurants/%(id)s/edit">Edit</a>
    <br />
    <a href="#">Delete</a>
</div>
'''

template_NEW_RESTAURANT_LINK = '<a href="/restaurants/new">Add Restaurant</a>'

template_NEW_RESTAURANT_FORM = '''\
<form method="POST" enctype="multipart/form-data" action="/restaurants/new">
    <input name="new-restaurant"  type="text">
    <br />
    <button type="submit">Add Restaurant</button>
</form>
'''

template_RESTAURANT_CLOSE = '</div>'

template_LIST_RESTAURANTS_LINK = '<a href="/restaurants">Back to Restaurants</a>'

template_RESTAURANT_TITLE = '''\
<h2>%(name)s</h2>
'''

template_RESTAURANT_EDIT = '''\
<form method="POST" enctype="multipart/form-data" action="/restaurants/%(id)s/edit">

    <input name="new-name"  type="text" placeholder="Type new name here">
    <br />
    <button type="submit">Edit Restaurant</button>
</form>
'''

def ListAllRestaurants(env):
    # Indicate successful GET request
    env.send_response(200)
    # Indicate that the reply is in the form of HTML to the client
    env.send_header('Content-type', 'text/html')
    # We are done sending headers
    env.end_headers()

    restaurantList = session.query(Restaurant).all()
    output = ''
    output += template_HTML_OPEN
    output += template_NEW_RESTAURANT_LINK
    output += template_LINE_BREAK
    output += template_LINE_BREAK

    for restaurant in restaurantList:
        output += template_RESTAURANT % {
                                        'name': restaurant.name,
                                        'id': restaurant.id}
        output += template_LINE_BREAK

    output += template_FORM
    output += template_HTML_CLOSE
    # Send a message back to the client
    env.wfile.write(output)
    # print output
    return

def CreateNewRestaurant(env):
    # Indicate successful GET request
    env.send_response(200)
    # Indicate that the reply is in the form of HTML to the client
    env.send_header('Content-type', 'text/html')
    # We are done sending headers
    env.end_headers()

    output = ''
    output += template_HTML_OPEN
    output += template_LIST_RESTAURANTS_LINK
    output += template_LINE_BREAK
    output += template_LINE_BREAK
    output += template_NEW_RESTAURANT_FORM
    output += template_HTML_CLOSE
    # Send a message back to the client
    env.wfile.write(output)
    print output
    return

def InsertRestaurant(env):
    # cgi.parse_header parses an HTML header such as 'content-type' into
    # a main value, and a dictionary of parameters
    ctype, pdict = cgi.parse_header(env.headers.getheader('content-type'))
    # Is this form data being received?
    if ctype == 'multipart/form-data':
        # cgi.parse_multipart collects all the fields in a form
        fields = cgi.parse_multipart(env.rfile, pdict)
        # Get the value from the specific field called 'new-restaurant'
        restaurantFields = fields.get('new-restaurant')
        restaurantName = restaurantFields[0]
        if restaurantName: # if a restaurant name was entered
            print restaurantName
            newRestaurant = Restaurant(name = restaurantName)
            session.add(newRestaurant)
            session.commit()
        else:
            print 'No restaurant name was entered.'
    else:
        print 'ctype was not \'multipart/form-data\''

def EditRestaurant(env, number):
    # Indicate successful GET request
    env.send_response(200)
    # Indicate that the reply is in the form of HTML to the client
    env.send_header('Content-type', 'text/html')
    # We are done sending headers
    env.end_headers()

    selectedRestaurant = session.query(Restaurant).filter_by(id = number).one()
    print selectedRestaurant.name
    print selectedRestaurant.id
    output = ''
    output += template_HTML_OPEN
    output += template_LIST_RESTAURANTS_LINK
    output += template_LINE_BREAK
    output += template_RESTAURANT_TITLE % {'name': selectedRestaurant.name }
    output += template_LINE_BREAK
    output += template_RESTAURANT_EDIT % {'id': selectedRestaurant.id }
    output += template_LINE_BREAK
    output += template_HTML_CLOSE
    # Send a message back to the client
    env.wfile.write(output)
    # print output
    print output
    return

# Handler
class webserverHandler(BaseHTTPRequestHandler):
    # Handle all GET requests that our server receives
    def do_GET(self):
        try:
            # BaseHTTPRequestHandler provides variable path that contains urls
            # sent by the client to the server as a string. Find the url that
            # ends with '/restaurants'
            if self.path.endswith('/restaurants'):
                ListAllRestaurants(self)

            elif self.path.endswith('/restaurants/new'):
                CreateNewRestaurant(self)

            elif self.path.endswith('/edit'):
                matchObj = re.match( r'\D*(\d*)\D*', self.path)
                number = int(matchObj.group(1))
                EditRestaurant(self, number)



            elif self.path.endswith('/hola'):
                # Indicate successful GET request
                self.send_response(200)
                # Indicate that the reply is in the form of HTML to the client
                self.send_header('Content-type', 'text/html')
                # We are done sending headers
                self.end_headers()


                output = ''
                output += template_HTML_OPEN
                output += '&#161Hola! <a href="/hello">Back to Hello</a>'
                output += template_FORM
                output += template_HTML_CLOSE
                # Send a message back to the client
                self.wfile.write(output)
                print output
                return
        except IOError:
            # If path points to something we can't find, we talk about it.
            self.send_error(404, 'File Not Found %s', self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'):
                InsertRestaurant(self)
                # redirect to the restaurant list
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            else:
                # incicate successful POST
                self.send_response(301)
                self.end_headers()

                # cgi.parse_header parses an HTML header such as 'content-type' into
                # a main value, and a dictionary of parameters
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                # Is this form data being received?
                if ctype == 'multipart/form-data':
                    # cgi.parse_multipart collects all the fields in a form
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    # Get the value from the specific field called 'message'
                    messagecontent = fields.get('message')

                output = ''
                output += '<html><body>'
                output += '<h2> Okay, how about this: </h2>'
                output += '<h1> %s </h1>' % messagecontent[0]

                output += template_FORM
                output += template_HTML_CLOSE
                self.wfile.write(output)
                print output
                return
        except:
            pass



def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print 'Web server running on port %s' % port
        server.serve_forever()

    # builtin exception
    except KeyboardInterrupt:
        print '^C entered, stopping web server...'
        server.socket.close()


if __name__ == '__main__':
    main()
