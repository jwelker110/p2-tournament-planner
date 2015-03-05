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


def createNewTournament():
    with closing(connect()) as db:
        cursor = db.cursor()
        current = getCurrentTournamentId()
        # if no tourneys have been registered yet
        if current is None:
            current = 0
        else:
            current += 1
        cursor.execute("INSERT INTO tournament_tracker (id) VALUES(%s);", (str(current),))
        db.commit()


def getCurrentTournamentId():
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT max(id) FROM tournament_tracker;")
        current_tourney = cursor.fetchone()[0]

    return current_tourney


def deleteAllMatches():
    """Remove all the match records from the database."""
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM matches;")
        db.commit()


def deleteMatchesFromTournament(tourney_id):
    """Remove all the match records from the database for the current tournament."""
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM matches WHERE tourney_id=(%s);", (str(tourney_id),))
        db.commit()


def deleteAllPlayers():
    """Remove all the player records from the database."""
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM players;")
        db.commit()


def deletePlayersFromTournament(tourney_id):
    """Remove all the player records from the database for the current tournament."""
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM players WHERE tourney_id=(%s);", (str(tourney_id),))
        db.commit()


def countTotalPlayers():
    """Returns the number of players currently registered."""
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT count(id) FROM players;")
        players = cursor.fetchone()[0]

    return players


def countPlayersFromTournament(tourney_id):
    """Returns the number of players currently registered for the current tournament."""
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT count(id) FROM players WHERE tourney_id=(%s);", (str(tourney_id),))
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
        cursor = db.cursor()
        cursor.execute("INSERT INTO players (name, tourney_id) VALUES(%s, %s);", (name, str(tourney_id)))
        db.commit()


def playerStandings(tourney_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        draws: the number of matches the player has drawn
        matches: the number of matches the player has played
    """
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM standings WHERE tourney_id=(%s) ORDER BY wins DESC, id;", (str(tourney_id),))
        standings = cursor.fetchall()

    return standings


def reportMatch(player_one_id, player_two_id, winner_id, tourney_id):
    """Records the outcome of a single match between two players.

    Args:
      player_one_id:  the id number of the first player
      player_two_id:  the id number of the second player
      winner_id: the id number of the player who won
      tourney_id: the id number of the tournament
    """
    if player_one_id is None:
        player_one_id = player_two_id
        player_two_id = None

    if player_two_id is None:
        winner_id = player_one_id

    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO matches (player_one_id, player_two_id, winner_id, tourney_id) VALUES(%s, %s, %s, %s);", (player_one_id, player_two_id, winner_id, str(tourney_id),))
        db.commit()


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
        cursor = db.cursor()
        cursor.execute("SELECT player_one_id, player_two_id FROM matches WHERE tourney_id=(%s);", (str(tourney_id),))
        matches = cursor.fetchall()
        db.commit()

    standings = playerStandings(tourney_id)
    pairings = []
    length = countPlayersFromTournament(tourney_id)

    if length % 2 == 1:
        bye_player_index = findByePlayer(standings, matches, length)
        bye_player = standings[bye_player_index]
        pairings.append((bye_player[0], bye_player[1], None, None))
        standings[bye_player_index] = None

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


def findByePlayer(standings, matches, length):
    # find the bye player for the round
    for i in range(length - 1, -1, -1):
        is_bye_player = True
        bye_player = [standings[i][0], standings[i][1]]
        for match in matches:
            if match[0] == bye_player[0] and match[1] is None:
                is_bye_player = False
                break
        if not is_bye_player:
            continue
        print "9.5. Bye Player ID: " + str(bye_player[0]) + " Name: " + bye_player[1]
        # return index of bye player
        return i
    return None


def playersAlreadyMatched(pairing, matches):
    for match in matches:
        # check for previous match with these players
        if (match[0] == pairing[0][0] and match[1] == pairing[1][0]) or \
                (match[0] == pairing[1][0] and match[1] == pairing[0][0]) or \
                (match[0] == pairing[1][0] and match[1] is None):
            return True
    return False
