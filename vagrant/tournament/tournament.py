#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    cursor = db.cursor()
    query = "DELETE FROM matches;"
    cursor.execute(query)
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    cursor = db.cursor()
    query = "DELETE FROM players;"
    cursor.execute(query)
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    cursor = db.cursor()
    query = "SELECT count(id) FROM players;"
    cursor.execute(query)
    players = cursor.fetchone()[0]
    db.close()
    return players


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    cursor = db.cursor()
    cursor.execute("INSERT INTO players (name) VALUES(%s);", (name,))
    db.commit()
    db.close()


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
    db = connect()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM standings ORDER BY wins DESC, id;")
    standings = cursor.fetchall()
    db.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    cursor = DB.cursor()
    cursor.execute("INSERT INTO matches (win_id, lose_id) VALUES(%s, %s);", (winner, loser))
    DB.commit()
    DB.close()
 
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

    db = connect()
    cursor = db.cursor()
    cursor.execute("SELECT win_id, lose_id FROM matches;")
    matches = cursor.fetchall()
    db.close()

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