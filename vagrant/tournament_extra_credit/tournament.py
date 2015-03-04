#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
# Extra Credit Exercises
#

import psycopg2
from contextlib import closing


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament_ec")


def deleteAllMatches():
    """Remove all the match records from the database."""
    with closing(connect()) as db:
        with db.cursor() as cursor:
            query = "DELETE FROM matches;"
            cursor.execute(query)


def deleteMatchesFromTournament(tourney_id):
    """Remove all the match records from the database for the current tournament."""
    with closing(connect()) as db:
        with db.cursor() as cursor:
            query = "DELETE FROM matches WHERE tourney_id=(%d);", (tourney_id,)
            cursor.execute(query)


def deleteAllPlayers():
    """Remove all the player records from the database."""
    with closing(connect()) as db:
        with db.cursor() as cursor:
            query = "DELETE FROM players;"
            cursor.execute(query)


def deletePlayersFromTournament(tourney_id):
    """Remove all the player records from the database for the current tournament."""
    with closing(connect()) as db:
        with db.cursor() as cursor:
            query = "DELETE FROM players WHERE tourney_id=(%d);", (tourney_id,)
            cursor.execute(query)


def countPlayers():
    """Returns the number of players currently registered."""
    with closing(connect()) as db:
        with db.cursor() as cursor:
            query = "SELECT count(id) FROM players;"
            cursor.execute(query)
            players = cursor.fetchone()[0]

    return players

def countPlayersFromTournament(tourney_id):
    """Returns the number of players currently registered for the current tournament."""
    with closing(connect()) as db:
        with db.cursor() as cursor:
            query = "SELECT count(id) FROM players WHERE tourney_id=(%d);", (tourney_id,)
            cursor.execute(query)
            players = cursor.fetchone()[0]

    return players


def registerPlayer(name, tourney_id):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    with closing(connect()) as db:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO players (name, tourney_id) VALUES(%s, %d);", (name, tourney_id))


def playerStandings(tourney_id):
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
    with closing(connect()) as db:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM standings WHERE tourney_id=(%d) ORDER BY wins DESC, id;", (tourney_id,))
            standings = cursor.fetchall()

    return standings


def reportMatch(winner, loser, tourney_id):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    with closing(connect()) as db:
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO matches (win_id, lose_id, tourney_id) VALUES(%s, %s, %d);", (winner, loser, tourney_id))

def swissPairings(tourney_id):
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

    with closing(connect()) as db:
        with db.cursor() as cursor:
            cursor.execute("SELECT win_id, lose_id FROM matches WHERE tourney_id=(%d);", (tourney_id,))
            matches = cursor.fetchall()

    standings = playerStandings()
    pairings = []
    length = len(standings)

    # start from the highest ranked player
    for i in range(length - 1):
        if standings[i] is None:
            continue
        # set first opponent of pair, (id, name)
        first_opponent = [standings[i][0], standings[i][1]]
        # removing opponent from list of possible opponents
        standings[i] = None

        # start from player adjacent in rank to first opponent
        for j in range(i + 1, length, 1):
            # make sure an opponent is at this index
            if standings[j] is None:
                continue
            # set second opponent of pair, (id, name)
            second_opponent = [standings[j][0], standings[j][1]]

            # if players haven't played together yet, pair is accepted
            if not playersAlreadyMatched([first_opponent, second_opponent], matches):
                # print("i = (%d) j = (%d)" % (i, j))
                # add pair to the pairings list, (id1, name1, id2, name2)
                pairings.append((first_opponent[0], first_opponent[1], second_opponent[0], second_opponent[1]))
                # remove second opponent from list of possible opponents
                standings[j] = None
                break

    return pairings


def playersAlreadyMatched(pairing, matches):
    for match in matches:
        # check for previous match with these players
        if (match[0] == pairing[0][0] and match[1] == pairing[1][0]) or \
                (match[0] == pairing[1][0] and match[1] == pairing[0][0]):
            return True
    return False