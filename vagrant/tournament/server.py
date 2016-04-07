#
# Tournament - A simplistic swiss pairing tournament that doesn't perform well
#              with more than 8 players.
#

# Interface with SQL database
import tournament

# HTML templates
import templates

# Other modules used to run a web server.
import cgi
from wsgiref.simple_server import make_server
from wsgiref import util

# Here we track the number of matches still to be played in the current
# round of the swiss pairings tournament. This ensures that all matches of a
# single round are played before new pairings are made for the second round
matchesToPlay = 0
# Matches in the current round of the tournament being played
currentMatches = []
# All previous rounds in the current tournament being played.
previousRounds = []
# Rounds left to play in the current tournament before a winner is decided
roundsLeft = 0
# If tournament has not begun, we need to run init code
tournamentBegan = False
# If tournament is not over we continue to prompt for match results
tournamentOver = False
# If the tournament is over, store the round info for review.
lastTournamentResult = ''

## Helper function to get at the fields inside submitted forms
def getFields(env):
    input = env['wsgi.input']
    length = int(env.get('CONTENT_LENGTH', 0))
    postdata = input.read(length)
    return cgi.parse_qs(postdata)


## Delete all information regarding the current tournament to make room for the
## next tournament.
def clearTournament():
    '''
    We call this whenever we want to start a new tournament to be displayed on
    the view.
    '''
    global matchesToPlay, currentMatches, previousRounds
    matchesToPlay = 0
    # The following variables track the current tournament. Clear them
    del currentMatches[:]
    del previousRounds[:]
    # Clear the match table in the database, as it tracks matches for one
    # tournament only.
    tournament.deleteMatches()

## Clean matches not connected to a tournament
def cleanUp():
    '''
    Clear all matches stored in the database if there are no matches stored in
    the python code. This means that the tournament was closed before it was
    stored and the matches cannot be recorded.
    '''
    standings = tournament.playerStandings()
    # There are some players registered
    if standings:
        # There are matches currently stored in the database but not in the code
        if standings[0][3] and not (previousRounds or lastTournamentResult):
            clearTournament()

## Request handler for main page
def Main(env, resp):
    '''
    This the main page that shows basically nothing.
    '''
    cleanUp() # Remove matches if not stored in python (due to unsubmitted tournament)
    headers = [('Content-type', 'text/html')]
    resp('200 OK', headers)
    return templates.HTML_WRAP % ''

## Request handler for adding a player
def AddPlayer(env, resp):
    '''
    Add a player into the SQL database.
    '''
    # Get fields from the submitted form
    fields = getFields(env)

    # Use a try and except to avoid KeyError if the input field is empty
    try:
        player = fields['new-player'][0]
    except KeyError:
        print 'No input string for new player.'
        player = ''

    # If the name is just whitespace, don't save it.
    player = player.strip()

    # Cut down to 9 characters to avoid names leaking over buttons
    if len(player) > 9:
        player = player[:9]

    if player: # player is not an empty string
        # Save it in the database
        clearTournament() # need to reset tournament, otherwise new player confuses it
        tournament.registerPlayer(player)

    # 302 redirect back to the player standings
    headers = [('Location', '/ShowPlayers'),
               ('Content-type', 'text/plain')]
    resp('302 REDIRECT', headers)
    return ['Redirecting']



## Request handler for viewing all registered players
def ShowPlayers(env, resp):
    '''
    Gets the current list of registered players.
    '''
    cleanUp() # Remove matches if not stored in python (due to unsubmitted tournament)

    # get list of tuples (playerid, name, wins, matches, tourny_wins)
    players = tournament.playerStandings()
    playerList = '' # this will hold HTML content to format into templates.HTML_WRAP
    for player in players:
        # Use tuples to create HTML markup to organize each player's info and
        # store all of this in playerList
        playerList += templates.PLAYER % {'name': player[1],
                                'wins': player[2],
                                'matches': player[3],
                                'playerid': player[0],
                                'tournyWins': player[4] or 0}
    # playerList needs to be inside <ul> tags as each player is a <li> element
    formattedList = '<ul>%s</ul>' % playerList

    headers = [('Content-type', 'text/html')]
    resp('200 OK', headers)
    # Fill the main template with the list of players
    return templates.HTML_WRAP % formattedList

## Removes all players from database
def DeletePlayers(env, resp):
    '''
    **DANGER**
    DELETES all the players and matches from the database.
    '''
    # Need to delete tournaments and matches as those tables depend on players
    tournament.deleteTournaments()
    tournament.deleteMatches()
    tournament.deletePlayers()
    # Clear the variables stored in python for the current tournament as it now
    # depends on non-existant players.
    clearTournament()
    # 302 redirect back to the page displaying the players, showing the user
    # that this list is now empty.
    headers = [('Location', '/ShowPlayers'),
               ('Content-type', 'text/plain')]
    resp('302 REDIRECT', headers)
    return ['Redirecting']

## Remove one player from database
def DeleteOnePlayer(env, resp):
    '''
    DELETE one player from the database. Set all matches with this player in
    them to show a NULL id for this player now. Delete all matches that now
    have two null players.
    '''
    # Get fields from the submitted form
    fields = getFields(env)

    # Make sure there is a playerid associated with the delete form sent
    try:
        playerid = fields['playerid'][0]
    except KeyError:
        print 'There is no player id present.'
        playerid = ''
    # If the player id is just white space, delete nothing.
    playerid = playerid.strip()
    if playerid:
        # Delete the player from the database
        tournament.deletePlayer(playerid)
        clearTournament() # Drop current tournament since player roster has changed
    else:
        print 'No playerid to delete.'

    # 302 redirect back to the player standings
    headers = [('Location', '/ShowPlayers'),
               ('Content-type', 'text/plain')]
    resp('302 REDIRECT', headers)
    return ['Redirecting']

def loadPreviousRounds(formattedList):
    '''Return formattedList except with all previousRounds appended to it'''
    global previousRounds
    for round in previousRounds:
        matchList = ''
        for match in round:
            matchList = addCompletedMatch(matchList, match)
        formattedList += templates.TOURNAMENTROUND % matchList
    return formattedList

def addPendingMatch(matchList, match):
    '''Return matchList except with a unplayed match template holding the
    information in match attached to it.'''
    matchList += templates.PENDINGMATCH % {'first_player_id': match['firstPlayerId'],
                                'first_player': match['firstPlayerName'],
                                'second_player_id': match['secondPlayerId'],
                                'second_player': match['secondPlayerName'],
                                'match_index': match['index']}
    return matchList

def addCompletedMatch(matchList, match):
    '''Return matchList except with a reported match template holding the
    information inside match attached to it.'''
    if match['winner'] == match['firstPlayerId']:
        firstPlayerStatus, secondPlayerStatus = 'success', 'default'
    else:
        secondPlayerStatus, firstPlayerStatus = 'success', 'default'
    matchList += templates.PLAYEDMATCH % {'first_player': match['firstPlayerName'],
                                'first_player_status': firstPlayerStatus,
                                'second_player': match['secondPlayerName'],
                                'second_player_status': secondPlayerStatus}
    return matchList

def blankMatch(pairing, i):
    '''Return a dictionary with appropriate fields filled in using the
    information from pairing and the index i

    NOTE: index is used ReportMatch to change the alreadyPlayed attribute of the
    correct match.'''
    return {
        'firstPlayerId': pairing[0],
        'firstPlayerName': pairing[1],
        'secondPlayerId': pairing[2],
        'secondPlayerName': pairing[3],
        'winner': None,
        'alreadyPlayed': False,
        'index': i
    }

## Push completed rounds to the database and clear currentMatches
def prepareForNextRound():
    '''Walk through each match in the currentMatches list and report each of
    these matches, entering them into the database.'''
    global previousRounds, currentMatches
    for match in currentMatches:
        # grab ids of the first player, second player, and the winner to
        # determine the winner and the loser
        a, b, w = int(match['firstPlayerId']), int(match['secondPlayerId']), int(match['winner'])
        winner = a if a == w else b
        loser = b if a == w else a
        tournament.reportMatch(winner, loser)
    # Append the currentMatches list to the previousRounds list, creating a list
    # of lists inside previousRounds
    previousRounds.append(list(currentMatches))
    # Empty the currentMatches to hold the matches for the next round.
    del currentMatches[:]

# Helper function
def determineRoundsNeeded(pairs):
    '''Use the number of pairs of players in the tournament to determine the
    number of rounds that need to be played before a champion can be decided.
    The number is one (1) smaller than might be expected due to the way rounds
    are decremented inside SwissPairings()'''
    n = 0
    while pairs > 2**n:
        n += 1
    return n

## Get tournament winner
def getWinner():
    '''Return a bool signifying whether a winner could be determined, and, if
    True, the string of the winner's name'''
    standings = tournament.playerStandings()
    length = len(standings)
    topScore = standings[0][2]
    if standings[1][2] == topScore:
        return False, ''
    else:
        return True, standings[0][1]

goAgain = False

import pdb

## View the tournament mode
def SwissPairings(env, resp):
    '''
    Display Swiss pairings for current player set. Works only for 8 people
    currently.
    '''
    cleanUp() # Remove matches if not stored in python (due to unsubmitted tournament)
    matchList = ''
    formattedList = ''
    global goAgain
    global matchesToPlay, currentMatches, previousRounds, roundsLeft
    global tournamentBegan, tournamentOver, lastTournamentResult
    if not tournamentBegan:
        tournamentBegan = True
        pairs = len(tournament.swissPairings())
        roundsLeft = determineRoundsNeeded(pairs)
    if not tournamentOver:
        if roundsLeft and matchesToPlay == 0: # new round
            if currentMatches: # We already have a round saved
                prepareForNextRound() # Clear matches and insert into database
                roundsLeft -= 1
            if goAgain:
                goAgain = False
                roundsLeft -= 1
            i = 0 # index for the matches for the current round
            pairings = tournament.swissPairings()
            matchesToPlay = len(pairings)
            for pairing in pairings:
                currentMatches.append(blankMatch(pairing, i))
                i += 1
            formattedList = loadPreviousRounds(formattedList)
            for match in currentMatches:
                matchList = addPendingMatch(matchList, match)
        elif matchesToPlay > 0:
            formattedList = loadPreviousRounds(formattedList)
            for match in currentMatches:
                if match['alreadyPlayed']:
                    matchList = addCompletedMatch(matchList, match)
                else:
                    matchList = addPendingMatch(matchList, match)
        else:
            prepareForNextRound()
            winnerExists, winner = getWinner()
            if winnerExists:
                tournamentOver = True
                lastTournamentResult = loadPreviousRounds('')
                del previousRounds[:]
                lastTournamentResult += templates.TOURNAMENTCONCLUSION % (winner)
            else:
                formattedList = loadPreviousRounds(formattedList)
                roundsLeft += 1
                goAgain = True

    formattedList += templates.TOURNAMENTROUND % matchList

    if tournamentOver:
        formattedList = lastTournamentResult

    if goAgain:
        # 302 redirect back to the player standings
        headers = [('Location', '/SwissPairings'),
                   ('Content-type', 'text/plain')]
        resp('302 REDIRECT', headers)
        return ['Redirecting']
    else:
        headers = [('Content-type', 'text/html')]
        resp('200 OK', headers)
        return templates.HTML_WRAP % formattedList

## Report a winner and loser and store it in the global currentMatches
def ReportMatch(env, resp):
    '''
    Report a match and store it in the global currentMatches
    '''
    # Get fields from the submitted form
    fields = getFields(env)
    global currentMatches, matchesToPlay

    matchesToPlay -= 1

    winnerid = int(fields['winnerid'][0])
    index = int(fields['matchindex'][0])

    currentMatches[index]['winner'] = winnerid
    currentMatches[index]['alreadyPlayed'] = True

    # 302 redirect back to the swiss pairings
    headers = [('Location', '/SwissPairings'),
               ('Content-type', 'text/plain')]
    resp('302 REDIRECT', headers)
    return ['Redirecting']

## Report the tournament that had just played out
def ReportTournament(env, resp):
    '''
    Report a tournament and clear matches for a next tournament.
    '''
    # Get fields from the submitted form
    fields = getFields(env)
    choice = fields['storeTournament'][0]

    global tournamentBegan, tournamentOver, lastTournamentResult
    tournamentOver = False
    tournamentBegan = False
    lastTournamentResult = ''

    # if the user chose to store the tournament we report it
    if choice == 'store':
        tournament.reportTournament()

    # 302 redirect back to the swiss pairings
    headers = [('Location', '/ShowPlayers'),
               ('Content-type', 'text/plain')]
    resp('302 REDIRECT', headers)
    return ['Redirecting']

## Dispatch table - maps URL prefixes to request handlers
DISPATCH = {'': Main,
            'AddPlayer': AddPlayer,
            'ShowPlayers': ShowPlayers,
            'DeletePlayers': DeletePlayers,
            'DeleteOnePlayer': DeleteOnePlayer,
            'SwissPairings': SwissPairings,
            'ReportMatch': ReportMatch,
            'ReportTournament': ReportTournament
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

httpd = make_server('', 8000, Dispatcher)
print "Serving HTTP on port 8000..."
httpd.serve_forever()
