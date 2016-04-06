#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def deleteTournaments():
    """Remove all tournament records from the database"""
    conn = connect()
    c = conn.cursor()
    c.execute('DELETE FROM tournament;')
    conn.commit()
    conn.close()

def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute('DELETE FROM match;')
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute('DELETE FROM player;')
    conn.commit()
    conn.close()

def deletePlayer(playerid):
    """Remove player with id playerid from the database. First, Remove playerid
    from all matches and replace with NULL. Delete all matches that have two NULL
    players."""
    conn = connect()
    c = conn.cursor()
    c.execute('UPDATE match SET first_player = NULL WHERE first_player = (%s);', (bleach.clean(playerid),))
    c.execute('UPDATE match SET second_player = NULL WHERE second_player = (%s);', (bleach.clean(playerid),))
    c.execute('UPDATE match SET winner = NULL WHERE winner = (%s);', (bleach.clean(playerid),))
    c.execute('DELETE FROM match WHERE first_player IS NULL AND second_player IS NULL')
    c.execute('DELETE FROM tournament WHERE winner = (%s)', (bleach.clean(playerid),))
    c.execute('DELETE FROM player WHERE id = (%s);', (bleach.clean(playerid),))
    conn.commit()
    conn.close()

def countRows(tablename):
    """Returns the number of entries in a table."""
    conn = connect()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM %s;' % tablename)
    result = c.fetchall()[0][0]
    conn.close()
    return result

def countPlayers():
    """Returns the number of players currently registered."""
    return countRows('player')

def countMatches():
    """Return the number of matches reported to have been played."""
    return countRows('match')

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO player VALUES (%s);", (bleach.clean(name),)
    )
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute('''
    SELECT
        id,
        name,
        (SELECT COUNT(*)
            FROM match
            WHERE (winner = player.id))
        AS wins,
        (SELECT COUNT(*)
            FROM match
            WHERE (first_player = player.id OR second_player = player.id))
        AS matches
        FROM player
        ORDER BY wins DESC;
''')
    result = c.fetchall()
    conn.close()
    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO match VALUES (%s, %s, %s);", (bleach.clean(winner),
                                                    bleach.clean(loser),
                                                    bleach.clean(winner), )
    )
    conn.commit()
    conn.close()

def reportTournament():
    """
    Reports the winner of a tournament, allowing us to store this and reset the
    match data. Also stores the number of wins that player had in this
    tournament.
    """
    standings = playerStandings()
    print 'REPORT TOURNAMENT:'
    topWins = standings[0][2]
    winner = standings[0][0]
    winnerName = None
    if topWins:
        conn = connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO tournament VALUES (%s, %s);", (bleach.clean(winner),
                                                        bleach.clean(topWins),)
        )
        conn.commit()
        conn.close()
        deleteMatches()
        winnerName = standings[0][1]
    return winnerName


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    pairings = []
    n = len(standings)
    i = 0
    while i < (n - 1):
        first = standings[i]
        i += 1
        second = standings[i]
        i += 1
        pairings.append((first[0], first[1], second[0], second[1]))
    return pairings
