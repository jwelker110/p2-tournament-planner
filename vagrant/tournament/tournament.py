#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from itertools import izip


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
    db = connect()
    cursor = db.cursor()
    cursor.execute("INSERT INTO matches (win_id, lose_id) VALUES(%s, %s);", (winner, loser))
    db.commit()
    db.close()
 
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
    length = len(standings)

    # this needs to be declared outside function
    # tracks which players are paired
    global paired_players_one, paired_players_two, pairings
    paired_players_one = []
    paired_players_two = []
    pairings = []

    print "start"
    if findPairings(standings, matches, length, 0):
        print "end"
        return pairings
    else:
        raise ValueError(
            "Pairings could not be found"
        )
    # # start from the highest ranked player
    # for i in range(length - 1):
    #     if standings[i] is None:
    #         continue
    #     # set first opponent of pair, (id, name)
    #     first_opponent = [standings[i][0], standings[i][1]]
    #     # removing opponent from list of possible opponents
    #     standings[i] = None
    #
    #     # start from player adjacent in rank to first opponent
    #     for j in range(i + 1, length, 1):
    #         # make sure an opponent is at this index
    #         if standings[j] is None:
    #             continue
    #         # set second opponent of pair, (id, name)
    #         second_opponent = [standings[j][0], standings[j][1]]
    #
    #         # if players haven't played together yet, pair is accepted
    #         if not playersAlreadyMatched([first_opponent, second_opponent], matches):
    #             # print("i = (%d) j = (%d)" % (i, j))
    #             # add pair to the pairings list, (id1, name1, id2, name2)
    #             pairings.append((first_opponent[0], first_opponent[1], second_opponent[0], second_opponent[1]))
    #             # remove second opponent from list of possible opponents
    #             standings[j] = None
    #             break


def findPairings(standings, matches, length, index):
    # Base case, this function is being called when all pairs have been found
    if len(paired_players_two) + len(paired_players_one) == len(standings):
        return True

    first_opponent = standings[index]
    # find first opponent
    for i in range(index, length, 1):
        already_paired = False
        first_opponent = standings[i]
        for one, two in izip(paired_players_one, paired_players_two):
            if first_opponent[0] == one or first_opponent[0] == two:
                already_paired = True
                break
        if already_paired:
            continue

        paired_players_one.append(first_opponent[0])
        # print "Paired One ", paired_players_one

        # find second opponent
        for j in range(index, length, 1):
            already_paired = False
            # print "Finding second"
            second_opponent = standings[j]
            if second_opponent[0] == first_opponent[0]:
                continue

            for one, two in izip(paired_players_one, paired_players_two):
                # check if player has been paired
                # if they have, find a new player
                if second_opponent[0] == one or second_opponent[0] == two:
                    already_paired = True
                    break

            if already_paired:
                continue
            if playersAlreadyMatched([first_opponent[0], second_opponent[0]], matches) is True:
                # print "players already matched."
                continue

            # since players can be paired, add to them if the other players get paired
            paired_players_two.append(second_opponent[0])
            # print "Paired Two ", paired_players_two

            if findPairings(standings, matches, length, index + 1) is True:
                pairings.append((first_opponent[0], first_opponent[1], second_opponent[0], second_opponent[1]))
                return True
            else:
                paired_players_two.remove(second_opponent[0])

        paired_players_one.remove(first_opponent[0])

    return False

    # if all players are paired, add the pair to pairings and return true
    # if returned false, find another pair.
    # if no more pairs available, return false


def playersAlreadyMatched(pairing, matches):
    for match in matches:
        # check for previous match with these players
        if (match[0] == pairing[0] and match[1] == pairing[1]) or \
                (match[0] == pairing[1] and match[1] == pairing[0]):
            return True
    return False