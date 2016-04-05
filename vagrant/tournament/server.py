#
# DB Forum - a buggy web forum server backed by a good database
#

# The forumdb module is where the database interface code goes.
# import forumdb

# Other modules used to run a web server.
import cgi
from wsgiref.simple_server import make_server
from wsgiref import util

# HTML template for the forum page
HTML_WRAP = '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Swiss Tournament</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.0.0-alpha/css/bootstrap.css">
</head>
<body>
  <div class="container">
    <div class="row" style="height: 5vh"></div>
    <div class="row" style="margin-bottom: 1em">
      <div class="col-xs-4">
        <button class="btn btn-default" id="add-player">Add Player</button>
      </div>
      <div class="col-xs-4">
        <button class="btn btn-default" id="show-players">Show Players</button>
      </div>
      <div class="col-xs-4">
        <button class="btn btn-default" id="swiss-pairings">Swiss Pairings</button>
      </div>
    </div>
    <div class="row">
      <div class="col-xs-12">
        <input id="new-name" style="display: none" type="text" placeholder="Enter player name">
      </div>
    </div>
    <div class="row">
      <div class="col-md-12" style="border: 1px solid #999; height: 80vh">

      </div>
    </div>
  </div>
</body>
</html>
'''

# # HTML template for an individual comment
# POST = '''\
#     <div class=post><em class=date>%(time)s</em><br>%(content)s</div>
# '''

## Request handler for main page
def View(env, resp):
    '''
    This the main page.
    '''
    # # get posts from database
    # posts = forumdb.GetAllPosts()
    # # send results
    # headers = [('Content-type', 'text/html')]
    # resp('200 OK', headers)
    # return [HTML_WRAP % ''.join(POST % p for p in posts)]
    headers = [('Content-type', 'text/html')]
    resp('200 OK', headers)
    return [HTML_WRAP]

## Request handler for posting - inserts to database
# def Post(env, resp):
#     '''Post handles a submission of the forum's form.
#
#     The message the user posted is saved in the database, then it sends a 302
#     Redirect back to the main page so the user can see their new post.
#     '''
#     # Get post content
#     input = env['wsgi.input']
#     length = int(env.get('CONTENT_LENGTH', 0))
#     # If length is zero, post is empty - don't save it.
#     if length > 0:
#         postdata = input.read(length)
#         fields = cgi.parse_qs(postdata)
#         content = fields['content'][0]
#         # If the post is just whitespace, don't save it.
#         content = content.strip()
#         if content:
#             # Save it in the database
#             forumdb.AddPost(content)
#     # 302 redirect back to the main page
#     headers = [('Location', '/'),
#                ('Content-type', 'text/plain')]
#     resp('302 REDIRECT', headers)
#     return ['Redirecting']

## Dispatch table - maps URL prefixes to request handlers
DISPATCH = {'': View
	    }

## Dispatcher forwards requests according to the DISPATCH table.
def Dispatcher(env, resp):
    '''Send requests to handlers based on the first path component.'''
    page = util.shift_path_info(env)
    if page in DISPATCH:
        return DISPATCH[page](env, resp)
    else:
        status = '404 Not Found'
        headers = [('Content-type', 'text/plain')]
        resp(status, headers)
        return ['Not Found: ' + page]


# Run this bad server only on localhost!
httpd = make_server('', 8000, Dispatcher)
print "Serving HTTP on port 8000..."
httpd.serve_forever()
