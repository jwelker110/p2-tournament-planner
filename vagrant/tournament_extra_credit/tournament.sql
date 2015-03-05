-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Clear DB to start fresh
DROP VIEW standings;
DROP TABLE matches;
DROP TABLE players;
DROP TABLE tournament_tracker;

CREATE TABLE tournament_tracker(
  id serial PRIMARY KEY
);

CREATE TABLE players(
  id serial PRIMARY KEY,
  name text,
  tourney_id INT REFERENCES tournament_tracker (id)
);

-- If player two is null, player one received a bye
-- If winner id is null, match is a tie
CREATE TABLE matches(
  id serial PRIMARY KEY,
  player_one_id INT REFERENCES players (id),
  player_two_id INT REFERENCES players (id) DEFAULT NULL,
  winner_id INT REFERENCES players (id) DEFAULT NULL,
  tourney_id INT REFERENCES tournament_tracker (id),
  CHECK (player_one_id != player_two_id),
  UNIQUE (player_one_id, player_two_id)
);

-- Reset the id of each table
ALTER SEQUENCE matches_id_seq RESTART WITH 1;
ALTER SEQUENCE players_id_seq RESTART WITH 1;
ALTER SEQUENCE tournament_tracker_id_seq RESTART WITH 1;

CREATE VIEW standings (id, name, wins, matches, tourney_id) AS
  SELECT p.id, p.name, count(m.winner_id=p.id), player_matches.num_matches, p.tourney_id
  FROM players as p
    LEFT JOIN matches as m
  ON p.id=m.player_one_id
    LEFT JOIN
    (SELECT p.id, count(m) as num_matches FROM players as p
      LEFT JOIN matches as m
      ON p.id=m.player_one_id OR p.id = m.player_two_id GROUP BY p.id) as player_matches
      ON p.id=player_matches.id
  GROUP BY p.id, player_matches.num_matches ORDER BY p.tourney_id;

-- Ensure DB is empty by displaying tables and views
SELECT * FROM standings;
SELECT * FROM matches;
SELECT * FROM players;