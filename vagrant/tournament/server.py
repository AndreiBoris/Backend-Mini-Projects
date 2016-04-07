#
# Tournament - A simplistic swiss pairing tournament that doesn't perform well
#              with more than 8 players. Tournament acts badly when there is not
#               an even number of players (players will be pushed in and out at
#               the bottom)
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
    roundList = '<ul>%s</ul>' % playerList

    headers = [('Content-type', 'text/html')]
    resp('200 OK', headers)
    # Fill the main template with the list of players
    return templates.HTML_WRAP % roundList

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

## Append all previous tournament rounds to a formatted HTML list
def loadPreviousRounds(roundList=''):
    '''Return roundList except with all previousRounds appended to it'''
    global previousRounds # rounds already played in this tournament
    for round in previousRounds: # each round is a list containing objects
        matchList = '' # string containing HTML for all arounds in a round
        for match in round:
            # previous rounds already completed, so we concatenate the string
            # matchList with the HTML for each match appropraitely formatted
            matchList = addCompletedMatch(matchList, match)
        # Put all the matches for a given round inside <ul> tags
        roundList += templates.TOURNAMENTROUND % matchList
    # All rounds (<ul>s) in one string
    return roundList

## Attach the formatted HTML of the information in match to the matchList
def addPendingMatch(matchList, match):
    '''Return matchList except with a unplayed match template holding the
    information in match attached to it.

    Parameters
    -----------
    matchList : string
                Empty string or a string containing formatted HTML with previous
                matches in the current tournament round.
    match : dictionary
                A dictionary with attributes describing the players of a match
                and the index of the match in the given tournament round. See
                createMatch()
    '''
    matchList += templates.PENDINGMATCH % {'first_player_id': match['firstPlayerId'],
                                'first_player': match['firstPlayerName'],
                                'second_player_id': match['secondPlayerId'],
                                'second_player': match['secondPlayerName'],
                                'match_index': match['index']}
    return matchList

## Attach the formatted HTML of the information in match to the matchList, such
## that it displays the winner and loser of the match.
def addCompletedMatch(matchList, match):
    '''Return matchList except with a reported match template holding the
    information inside match attached to it.

    Parameters
    -----------
    matchList : string
                Empty string or a string containing formatted HTML with previous
                matches in the current tournament round.
    match : dictionary
                A dictionary with attributes describing the players of a match
                and the id of the winner. See createMatch()
    '''
    # If the firstPlayer is the winner, give them the winner graphic. Otherwise,
    # give it to the secondPlayer
    if match['winner'] == match['firstPlayerId']:
        firstPlayerStatus, secondPlayerStatus = 'success', 'default'
    else:
        secondPlayerStatus, firstPlayerStatus = 'success', 'default'
    # Add the formatted HTML of the match to the matchList
    matchList += templates.PLAYEDMATCH % {'first_player': match['firstPlayerName'],
                                'first_player_status': firstPlayerStatus,
                                'second_player': match['secondPlayerName'],
                                'second_player_status': secondPlayerStatus}
    return matchList

## Use a pairing result from tournament.playerStandings() and an index specific
## only to the round that this match is in to form a match object.
def createMatch(pairing, i):
    '''Return a dictionary with appropriate fields filled in using the
    information from pairing and the index i

    NOTE: index is used ReportMatch to change the alreadyPlayed attribute of the
    correct match.

    Parameters
    -----------
    pairing : tuple
                holds information about the players facing each other in a match
    i : integer
                index value used to refer to the match through an interface that
                does not see the list
    '''
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

    More than 2 pairs require 3 rounds, more than 4 pairs require 4 rounds,
    more than 8 pairs require 5 rounds, etc.

    Parameters
    -----------
    pairs : integer
                number of matches per round (pairs of players facing each other)
    '''
    n = 1
    while pairs > 2**n:
        n += 1
    return n + 1

## Determine whether there is a winner currently, and if so, the name of that
## winner.
def getWinner():
    '''Return a bool signifying whether a winner could be determined, and, if
    True, the string of the winner's name'''
    standings = tournament.playerStandings()
    topScore = standings[0][2]
    # If the second best score is equal to the top score, we don't have a winner
    if standings[1][2] == topScore:
        return False, 'undetermined'
    else:
        # Return the name of the person with the top score
        return True, standings[0][1]

## Set up initial conditions of the tournament
def initTournament():
    '''Set up a tournament with a correct number of rounds'''
    global tournamentBegan, roundsLeft
    tournamentBegan = True
    # Determine the number of rounds that need to be played based on the number
    # of swiss pairings.
    roundsLeft = determineRoundsNeeded(len(tournament.swissPairings()))

## Handle the first match of a round with appropraite set up for the rest of the
## round
def handleFirstRound():
    '''Return matchList for the current set of matches at the beginning of a new
    round.
    '''
    global roundsLeft, matchesToPlay, currentMatches
    matchList = ''

    prepareForNextRound() # Clear currentMatches and insert into database

    # A match must be played for every swiss pairing
    pairings = tournament.swissPairings()
    matchesToPlay = len(pairings)

    i = 0 # index for the matches for the current round
    # use the information in pairings to create a currentMatches list of
    # dictionaries holding information about each match
    for pairing in pairings:
        currentMatches.append(createMatch(pairing, i))
        # Keep track of index to determine which round users are interacting
        # with.
        i += 1
    # Append all previous match results to roundList
    # Add all current matches to the match list
    for match in currentMatches:
        matchList = addPendingMatch(matchList, match)
    # We've now handled the round, all that is left is to play matchesToPlay
    # matches
    roundsLeft -= 1
    return matchList

def handleOtherRounds():
    '''Return matchList for the current set of matches at any point of an
    ongoing round.'''
    global currentMatches
    matchList = ''
    for match in currentMatches:
        if match['alreadyPlayed']:
            matchList = addCompletedMatch(matchList, match)
        else:
            matchList = addPendingMatch(matchList, match)
    return matchList

def handleEndOfTourny(needTieBreakerRound):
    ''''''
    global tournamentOver, lastTournamentResult, roundsLeft
    prepareForNextRound() # submit currently pending match
    winnerExists, winner = getWinner()
    if winnerExists: # We can end the tournament
        tournamentOver = True
        # Load all already-played rounds to be displayed
        lastTournamentResult = loadPreviousRounds()
        # Clear previous rounds for the next tournament
        del previousRounds[:]
        # Add the tournament winner and user buttons to be displayed with rounds
        lastTournamentResult += templates.TOURNAMENTCONCLUSION % (winner)
    else: # We need to play another round
        roundsLeft += 1
        needTieBreakerRound = True
    # Allow caller to determine correct action
    return needTieBreakerRound

## View the tournament mode
def SwissPairings(env, resp):
    '''
    Display Swiss pairings and tournament progress (if applicable) for the
    current player set.
    '''
    # The list of matches to be placed inside roundList
    matchList = ''
    # The list of all rounds, played previously and currently being played
    roundList = ''
    # matchestToPlay: integer - number of matches we will have to play in this round
    # currentMatches: list - the matches that are part of the current round
    # previousRounds: list - each previous round was previously the list of
    #                         currentMatches
    # roundsLeft: integer - number of rounds we will have to play to determine winner
    global matchesToPlay, currentMatches, previousRounds, roundsLeft
    # tournamentBegan: bool - if false, need to init tournament
    # tournamentOver: bool - if false, keep playing rounds, else display result
    # lastTournamentResult: string - if tournamentOver, display this
    global tournamentBegan, tournamentOver, lastTournamentResult
    # If a winner is not determined after roundsLeft and matchestToPlay has reached
    # 0, a tie breaker round will need to be played
    needTieBreakerRound = False

    # Remove matches in database if not stored in python (due to unsubmitted
    # tournament)
    cleanUp()

    if not tournamentBegan: # new tournament
        initTournament() # calculate rounds needed to determine chamption

    if not tournamentOver:
        if roundsLeft and matchesToPlay == 0: # new round
            matchList = handleFirstRound() # get string display new round
        elif matchesToPlay > 0: # not a new round
            matchList = handleOtherRounds() # get string display current round
        else: # no rounds or matches left to play
            # handleEndOfTourny adds an extra round if we needTieBreakerRound,
            # and if not, it sets tournamentOver and lastTournamentResult
            needTieBreakerRound = handleEndOfTourny(needTieBreakerRound)
        # Add previous rounds to roundList
        roundList = loadPreviousRounds(roundList)
        # Add current round to roundList
        roundList += templates.TOURNAMENTROUND % matchList

    if tournamentOver:
        # we'll just be display previous rounds from this tournament
        roundList = lastTournamentResult

    # If we need a tiebreaker round, we have to reload SwissPairings() to get
    # back into the 'if not tournamentOver' handler (since we added 1 to roundsLeft)
    if needTieBreakerRound:
        needTieBreakerRound = False
        # 302 redirect back to the player standings
        headers = [('Location', '/SwissPairings'),
                   ('Content-type', 'text/plain')]
        resp('302 REDIRECT', headers)
        return ['Redirecting']
    else: # display the current tournament
        headers = [('Content-type', 'text/html')]
        resp('200 OK', headers)
        # Format previous and current rounds into HTML_WRAP
        return templates.HTML_WRAP % roundList

## Report a winner and loser and store it in the global currentMatches
def ReportMatch(env, resp):
    '''
    Report a match and store it in the global currentMatches
    '''
    global currentMatches, matchesToPlay
    # Get fields from the submitted form
    fields = getFields(env)
    # A reported match means one less match to play before submitting the whole
    # round of matches and moving onto the next one
    matchesToPlay -= 1
    # the sql player id of the winner
    winnerid = int(fields['winnerid'][0])
    # the index attribute of the match inside currentMatches taken from the form
    index = int(fields['matchindex'][0])
    # Access match at index and set the winner of the match to be the chosen
    # winner from the form submission
    currentMatches[index]['winner'] = winnerid
    # Match is played, so display it differently from pending matches.
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
    global tournamentBegan, tournamentOver, lastTournamentResult
    # Get fields from the submitted form
    fields = getFields(env)
    # The choice is either to store or discard a tournament
    choice = fields['storeTournament'][0]

    # if the user chose to store the tournament we report it
    if choice == 'store':
        tournament.reportTournament()
    else: # if the use choice is to discard a tournament, do nothing
        pass

    # Reset values to make way for a new tournament
    tournamentOver = False
    tournamentBegan = False
    lastTournamentResult = ''

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
