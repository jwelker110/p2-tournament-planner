#!/usr/bin/env python
#
# Test cases for tournament.py extra credit exercises

from tournament import *
import math
import random

NUMBER_OF_PLAYERS = 25

def testDeleteMatches():
    deleteMatchesFromTournament(tourney_id)
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatchesFromTournament(tourney_id)
    deletePlayersFromTournament(tourney_id)
    print "2. Player records can be deleted."


def testCount():
    deleteMatchesFromTournament(tourney_id)
    deletePlayersFromTournament(tourney_id)
    c = countPlayersFromTournament(tourney_id)
    if c == '0':
        raise TypeError(
            "countPlayersFromTournament() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayersFromTournament should return zero.")
    print "3. After deleting, countPlayersFromTournament() returns zero."


def testRegister():
    deleteMatchesFromTournament(tourney_id)
    deletePlayersFromTournament(tourney_id)
    registerPlayer("Chandra Nalaar", tourney_id)
    c = countPlayersFromTournament(tourney_id)
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayersFromTournament() should be 1.")
    print "4. After registering a player, countPlayersFromTournament() returns 1."


def testRegisterCountDelete():
    deleteMatchesFromTournament(tourney_id)
    deletePlayersFromTournament(tourney_id)
    registerPlayer("Markov Chaney", tourney_id)
    registerPlayer("Joe Malik", tourney_id)
    registerPlayer("Mao Tsu-hsi", tourney_id)
    registerPlayer("Atlanta Hope", tourney_id)
    c = countPlayersFromTournament(tourney_id)
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayersFromTournament(tourney_id)
    c = countPlayersFromTournament(tourney_id)
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatchesFromTournament(tourney_id)
    deletePlayersFromTournament(tourney_id)
    registerPlayer("Melpomene Murray", tourney_id)
    registerPlayer("Randy Schwartz", tourney_id)
    standings = playerStandings(tourney_id)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 6:
        raise ValueError("Each playerStandings row should have six columns.")
    [(id1, name1, wins1, draws1, matches1, tourney), (id2, name2, wins2, draws2, matches2, tourney)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatchesFromTournament(tourney_id)
    deletePlayersFromTournament(tourney_id)
    registerPlayer("Bruno Walton", tourney_id)
    registerPlayer("Boots O'Neal", tourney_id)
    registerPlayer("Cathy Burton", tourney_id)
    registerPlayer("Diane Grant", tourney_id)
    standings = playerStandings(tourney_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, id1, tourney_id)
    reportMatch(id3, id4, id3, tourney_id)
    standings = playerStandings(tourney_id)
    for (i, n, w, d, m, t) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatchesFromTournament(tourney_id)
    deletePlayersFromTournament(tourney_id)
    registerPlayer("Twilight Sparkle", tourney_id)
    registerPlayer("Fluttershy", tourney_id)
    registerPlayer("Applejack", tourney_id)
    registerPlayer("Pinkie Pie", tourney_id)
    standings = playerStandings(tourney_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, id1, tourney_id)
    reportMatch(id3, id4, id3, tourney_id)
    pairings = swissPairings(tourney_id)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def testRoundPairing():
    deleteMatchesFromTournament(tourney_id)
    deletePlayersFromTournament(tourney_id)

    # get number of rounds necessary
    rounds = int(math.log(NUMBER_OF_PLAYERS, 2))

    for i in range(NUMBER_OF_PLAYERS):
        registerPlayer("Player " + str(i + 1), tourney_id)

    for i in range(rounds):
        pairings = swissPairings(tourney_id)
        if len(pairings) != int(math.ceil(NUMBER_OF_PLAYERS / 2.0)):
            raise ValueError(
                "There must be %d pairings for %d players." % (int(math.ceil(NUMBER_OF_PLAYERS / 2.0)), NUMBER_OF_PLAYERS))
        for pair in pairings:
            if random.randrange(0, 2, 1) == 1:
                reportMatch(pair[0], pair[2], pair[0], tourney_id)
            else:
                reportMatch(pair[0], pair[2], pair[2], tourney_id)
        # print(pairings)

    print("9. Matches successfully found for %d players through %d rounds." % (NUMBER_OF_PLAYERS, rounds))


def testReportingBye():
    reportMatch(16, None, 16, tourney_id)

    print("10. Bye successfully reported.")


if __name__ == '__main__':
    createNewTournament()
    global tourney_id
    tourney_id = getCurrentTournamentId()
    # testDeleteMatches()
    # testDelete()
    # testCount()
    # testRegister()
    # testRegisterCountDelete()
    # testStandingsBeforeMatches()
    # testReportMatches()
    # testPairings()
    testRoundPairing()
    print "Success!  All tests pass!"


