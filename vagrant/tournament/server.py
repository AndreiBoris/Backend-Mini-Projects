#
# DB Forum - a buggy web forum server backed by a good database
#

# The forumdb module is where the database interface code goes.
import tournament

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
  <style>
    .player-listing {
      display: flex;
      font-size: 1.2rem;
    }
    .player-listing + .player-listing {
        border-top: 1px solid #999;
        }
    .player-listing__name {
      width: 15em;
    }
    .player-listing__wins {
      width: 6em;
    }
    .player-listing__losses {
      width: 6em;
    }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.2/jquery.min.js"></script>
</head>
<body>
  <div class="container">
    <div class="row" style="height: 5vh"></div>
    <div class="row" style="margin-bottom: 1em">
      <div class="col-xs-3">
        <button class="btn btn-default" id="add-player">Add Player</button>
      </div>
      <div class="col-xs-3">
        <form method="post" action="/ShowPlayers">
          <button class="btn btn-default" type="submit">Show Players</button>
        </form>
      </div>
      <div class="col-xs-3">
        <button class="btn btn-default" id="swiss-pairings">Swiss Pairings</button>
      </div>
      <div class="col-xs-3">
        <form method="post" action="/DeletePlayers">
          <button class="btn btn-danger" type="submit">Delete All</button>
        </form>
      </div>
    </div>
    <div class="row">
      <div class="col-xs-12">
        <form id="new-player-form" method="post" action="/AddPlayer">
          <input name="new-player"  type="text">
          <button class="btn btn-primary" type="submit">Add</button>
        </form>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        %s
      </div>
    </div>
  </div>
  <script>
    var $newPlayerForm = $('#new-player-form');
    $newPlayerForm.hide();
    $('#add-player').on('click', function() {
      $newPlayerForm.toggle();
    });
  </script>
</body>
</html>
'''

## Request handler for main page
def Main(env, resp):
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
    return HTML_WRAP % ''

## Request handler for posting
def AddPlayer(env, resp):
    '''Post handles a submission of the forum's form.

    The message the user posted is saved in the database, then it sends a 302
    Redirect back to the main page so the user can see their new post.
    '''
    # Get post content
    input = env['wsgi.input']
    length = int(env.get('CONTENT_LENGTH', 0))


    # If length is zero, post is empty - don't save it.
    if length > 0:
        postdata = input.read(length)
        fields = cgi.parse_qs(postdata)
        player = fields['new-player'][0]
        # If the post is just whitespace, don't save it.
        player = player.strip()
        if player:
            # Save it in the database
            tournament.registerPlayer(player)

    # 302 redirect back to the player standings
    headers = [('Location', '/ShowPlayers'),
               ('Content-type', 'text/plain')]
    resp('302 REDIRECT', headers)
    return ['Redirecting']

# # HTML template for an individual player
PLAYER = '''\
    <li class="player-listing">
        <div class="player-listing__name">
            Name: <b>%(name)s</b>
        </div>
        <div class="player-listing__wins">
            Wins: <b>%(wins)s</b>
        </div>
        <div class="player-listing__losses">
            Losses: <b>%(losses)s</b>
        </div>
    </li>
'''

## Request handler for viewing all registered players
def ShowPlayers(env, resp):
    '''
    GETs the current list of registered players.
    '''
    # Get post content
    # get posts from database
    players = tournament.playerStandings()
    playerList = ''
    for player in players:
        playerList += PLAYER % {'name': player[1],
                                'wins': player[2],
                                'losses': player[3]}
    print playerList
    formattedList = '<ul>%s</ul>' % playerList

    headers = [('Content-type', 'text/html')]
    resp('200 OK', headers)
    return HTML_WRAP % formattedList

def DeletePlayers(env, resp):
    '''
    **DANGER**
    DELETES all the players and matches from the database.
    '''
    tournament.deleteMatches()
    tournament.deletePlayers()
    # 302 redirect back to the main page
    headers = [('Location', '/ShowPlayers'),
               ('Content-type', 'text/plain')]
    resp('302 REDIRECT', headers)
    return ['Redirecting']

## Dispatch table - maps URL prefixes to request handlers
DISPATCH = {'': Main,
            'AddPlayer': AddPlayer,
            'ShowPlayers': ShowPlayers,
            'DeletePlayers': DeletePlayers
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
