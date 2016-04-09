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

template_RESTAURANT = '<div>%s</div>'

template_RESTAURANT_CLOSE = '</div>'

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

    for restaurant in restaurantList:
        output += template_RESTAURANT % restaurant.name
        output += template_LINE_BREAK

    output += template_FORM
    output += template_HTML_CLOSE
    # Send a message back to the client
    env.wfile.write(output)
    print output
    return

# Handler
class webserverHandler(BaseHTTPRequestHandler):
    # Handle all GET requests that our server receives
    def do_GET(self):
        try:
            # BaseHTTPRequestHandler provides variable path that contains urls
            # sent by the client to the server as a string. Find the url that
            # ends with '/restaurant'
            if self.path.endswith('/restaurants'):
                ListAllRestaurants(self)

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
