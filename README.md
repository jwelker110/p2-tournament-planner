# p2-tournament-planner
Tournament Planner for the Udacity Full Stack Web Development Course.

# Overview
`tournament.py` provides functions to interact with the database created by running `tournament.sql`. The database structure is based on a Swiss-Pairings Tournament. To clarify the use of available functions, `tournament_test.py` provides tests for each function contained in the project that provides minimal feedback on the purpose of each.

*Contrary to a typical Swiss-Pairings Tournament, this implementation does not prevent players from playing each other more than once.*

# Instructions
1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](http://www.vagrantup.com/downloads).
2. [Clone](https://github.com/jwelker110/p2-tournament-planner.git) or [download](https://github.com/jwelker110/p2-tournament-planner/archive/master.zip) the repository.
3. Run the Vagrant VM using *vagrant up* followed by *vagrant ssh*.
4. [Navigate](http://askubuntu.com/questions/232442/how-do-i-navigate-between-directories-in-terminal) to */vagrant/tournament/* and type *psql*.
5. Run tournament.sql by typing *\i tournament.sql*.
6. *\q* out of psql and type *python tournament_test.py* to see the tests executed. 
7. If you become stuck at any point, please refer to the [documentation](https://docs.google.com/document/u/0/d/16IgOm4XprTaKxAa8w02y028oBECOoB1EI1ReddADEeY/pub?embedded=true) provided for this project.

If you would like to run the tests for a larger group of players, simply edit the value of *NUMBER_OF_PLAYERS* in `tournament_test.py`. Please note that **increasing the player count will increase the amount of time it takes to run the tests**.
