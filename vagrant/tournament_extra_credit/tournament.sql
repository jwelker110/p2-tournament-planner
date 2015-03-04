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

CREATE TABLE players(
  id serial PRIMARY KEY ,
  name text,
  tourney_id INT NOT NULL
);

CREATE TABLE matches(
  id serial PRIMARY KEY,
  win_id INT REFERENCES players (id),
  lose_id INT REFERENCES players (id),
  tourney_id INT NOT NULL REFERENCES players,
  CHECK (win_id != lose_id),
  UNIQUE (win_id, lose_id)

);

CREATE VIEW standings (id, name, wins, matches, tourney_id) AS
  SELECT p.id, p.name, count(m.win_id), player_matches.num_matches, p.tourney_id
  FROM players as p
    LEFT JOIN matches as m
  ON p.id=m.win_id
    LEFT JOIN
    (SELECT p.id, count(m) as num_matches FROM players as p
      LEFT JOIN matches as m
      ON p.id=m.win_id OR p.id = m.lose_id GROUP BY p.id) as player_matches
      ON p.id=player_matches.id
  GROUP BY p.id, player_matches.num_matches;

-- Ensure DB is empty by displaying tables and views
SELECT * FROM standings;
SELECT * FROM matches;
SELECT * FROM players;