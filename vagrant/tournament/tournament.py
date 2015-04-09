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
    """Creates a new tournament whose id is automatically incremented with each call"""
    with closing(connect()) as db:
        cursor = db.cursor()
        current = getCurrentTournamentId()
        # if no tourneys have been registered yet
        if current is None:
            current = 1
        else:
            current += 1
        cursor.execute("INSERT INTO tournament_tracker (id) VALUES(%s);", (str(current),))
        db.commit()


def getCurrentTournamentId():
    """Finds the current tournament

    Returns:
        The tournament id
    """
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
      tourney_id: the tourney_id of tournament to register the player in
    """
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO players (name, tourney_id) VALUES(%s, %s);", (name, str(tourney_id)))
        db.commit()


def findPlayerOMW(player_id, tourney_id, cursor):

    opponent_match_wins = 0

    # First group of opponents
    cursor.execute(""
                   "SELECT player_one_id FROM matches "
                   "WHERE player_two_id=(%s) AND tourney_id=(%s) "
                   "AND winner_id IS NOT NULL;", (str(player_id), str(tourney_id)))
    opponents = cursor.fetchall()

    # Second group of opponents
    cursor.execute(""
                   "SELECT player_two_id FROM matches "
                   "WHERE player_one_id=(%s) AND tourney_id=(%s) "
                   "AND winner_id IS NOT NULL;", (str(player_id), str(tourney_id)))
    opponents.append(cursor.fetchall())

    for opponent in opponents:
        cursor.execute(""
                       "SELECT wins FROM standings "
                       "WHERE id=(%s);", (str(opponent[0]),))
    opponent_match_wins += cursor.fetchall()[0]

    return opponent_match_wins


def playerStandings(tourney_id):
    """Returns a list of the players and their win records, sorted by wins and
    opponent match wins.

    The first entry in the list should be the player in first place.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches, tourney_id, omw):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        tourney_id: the tournament id associated with this player
        omw: Opponent Match Wins: the number of total wins opponents of this player have
    """
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM standings WHERE tourney_id=(%s) ORDER BY wins DESC, omw DESC ;", (str(tourney_id),))
        standings = cursor.fetchall()

    return standings


def reportMatch(player_one_id, player_two_id, winner_id, tourney_id):
    """Records the outcome of a single match between two players.

        Matches that do not have a winner are recognized as a draw.

    Args:
      player_one_id:  the id number of the first player
      player_two_id:  the id number of the second player
      winner_id: the id number of the player who won
      tourney_id: the id number of the tournament
    """
    # Match is a bye, enter player as player one
    if player_one_id is None:
        player_one_id = player_two_id
        player_two_id = None
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

    When an odd number of players are registered, one player is given a bye.
    Players may not receive more than one bye in a tournament.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings(tourney_id)
    pairings = []
    length = countPlayersFromTournament(tourney_id)
    append = pairings.append

    # Odd number of players
    if length % 2 == 1:
        bye_player_index = findByePlayer(standings, tourney_id)
        # bye player not found
        if bye_player_index is None:
            raise ValueError(
                "Could not find bye player for this round"
            )
        # report bye and remove player from standings
        reportMatch(standings[bye_player_index][0], None, standings[bye_player_index][0], tourney_id)
        del standings[bye_player_index]

    # start from the highest ranked player
    for i in range(0, length - 1, 2):
        # add pair to the pairings list, (id1, name1, id2, name2)
        append((standings[i][0], standings[i][1], standings[i+1][0], standings[i+1][1]))

    return pairings


def findByePlayer(standings, tourney_id):
    """ Finds the player that deserves the Bye for the round and hasn't
    already received one.

    Returns:
        The index of the location of the player in the standings
    """

    # find the bye player for the round
    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT player_one_id FROM matches WHERE player_two_id=NULL AND tourney_id=(%s);", (str(tourney_id),))
        previous_bye_matches = cursor.fetchall()

    # check each player starting at lowest ranked until eligible player found
    for i in range(countPlayersFromTournament(tourney_id) - 1, -1, -1):
        for match in previous_bye_matches:
            if match[0] == standings[i][0]:
                break
        return i

    return None


def resetDatabase():
    """ removes current data from database and resets serial columns """
    deleteAllMatches()
    deleteAllPlayers()

    with closing(connect()) as db:
        cursor = db.cursor()
        cursor.execute("ALTER SEQUENCE matches_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE players_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE tournament_tracker_id_seq RESTART WITH 1;")