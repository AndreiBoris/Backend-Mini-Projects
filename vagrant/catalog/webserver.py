from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# Handler
class webserverHandler(BaseHTTPRequestHandler):
    # Handle all GET requests that our server receives
    def do_GET(self):
        try:
            # BaseHTTPRequestHandler provides variable path that contains urls
            # sent by the client to the server as a string. Find the url that
            # ends with '/hello'
            if self.path.endswith('/hello'):
                # Indicate successful GET request
                self.send_response(200)
                # Indicate that the reply is in the form of HTML to the client
                self.send_header('Content-type', 'text/html')
                # We are done sending headers
                self.end_headers()


                output = ''
                output += '<html><body>Hello!</body></html>'
                # Send a message back to the client
                self.wfile.write(output)
                print output
                return
        except IOError:
            # If path points to something we can't find, we talk about it.
            self.send_error(404, 'File Not Found %s', self.path)

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
