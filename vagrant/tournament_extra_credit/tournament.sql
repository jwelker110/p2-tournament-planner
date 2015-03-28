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
DROP FUNCTION opponent_wins(player_id integer, tourney integer);
DROP FUNCTION test_opponent_wins(player_id integer, tourney integer);


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
  CHECK (player_one_id != player_two_id)
);

-- Reset the id of each table
ALTER SEQUENCE matches_id_seq RESTART WITH 1;
ALTER SEQUENCE players_id_seq RESTART WITH 1;
ALTER SEQUENCE tournament_tracker_id_seq RESTART WITH 1;

CREATE FUNCTION test_opponent_wins (player_id integer, tourney integer) RETURNS TABLE (omw BIGINT, omw_tourney_id INT)
AS $$
    DECLARE
      id INTEGER;
    BEGIN
      FOR id in (SELECT
                       CASE
                        WHEN player_one_id=player_id AND tourney_id=tourney THEN player_two_id
                        WHEN player_two_id=player_id AND tourney_id=tourney THEN player_one_id
                       END AS opponent_id
                     FROM matches GROUP BY opponent_id)
        LOOP
          RETURN QUERY
          EXECUTE format('SELECT wins, tourney_id FROM standings WHERE standings.id=%L', id);
        END LOOP ;
    END

$$ LANGUAGE plpgsql;

CREATE VIEW standings (id, name, wins, matches, tourney_id) AS
  SELECT
    p.id,
    p.name,
    player_wins.num_wins,
    player_matches.num_matches,
    p.tourney_id
  FROM players as p
    LEFT JOIN matches as m
  ON p.id=m.player_one_id
    LEFT JOIN
    (SELECT
       p.id,
       count(m) as num_matches
     FROM players as p
      LEFT JOIN matches as m
      ON p.id=m.player_one_id OR p.id = m.player_two_id GROUP BY p.id) as player_matches
      ON p.id=player_matches.id
    LEFT JOIN
    (SELECT
       p2.id,
       count(m2) as num_wins
      FROM players as p2
      LEFT JOIN matches as m2
      ON p2.id=m2.winner_id GROUP BY p2.id) as player_wins
      ON p.id=player_wins.id
  GROUP BY p.id, player_matches.num_matches, player_wins.num_wins ORDER BY p.tourney_id;

-- Ensure DB is empty by displaying tables and views
SELECT * FROM standings;
SELECT * FROM matches;
SELECT * FROM players;

CREATE FUNCTION opponent_wins (player_id integer, tourney integer) RETURNS SETOF BIGINT AS $$
    DECLARE
      id INTEGER;
    BEGIN
      FOR id in (SELECT
                       CASE WHEN player_one_id=player_id AND player_two_id IS NOT NULL AND tourney_id=tourney THEN player_two_id
                       WHEN player_two_id=player_id AND tourney_id=tourney THEN player_one_id
                       END AS opponent_id
                     FROM matches GROUP BY opponent_id)
        LOOP
          RETURN QUERY
          EXECUTE format('SELECT wins FROM standings WHERE standings.id=%L', id);
        END LOOP ;
    END

$$ LANGUAGE plpgsql;

-- CREATE FUNCTION test_opponent_wins (player_id integer, tourney integer) RETURNS TABLE (id INT, omw BIGINT, omw_tourney_id INT) AS $$
--     DECLARE
--       id INTEGER;
--     BEGIN
--       FOR id in (SELECT
--                        CASE WHEN player_one_id=player_id AND player_two_id IS NOT NULL AND tourney_id=tourney THEN player_two_id
--                        WHEN player_two_id=player_id AND tourney_id=tourney THEN player_one_id
--                        END AS opponent_id
--                      FROM matches GROUP BY opponent_id)
--         LOOP
--           RETURN QUERY
--           EXECUTE format('SELECT id, wins, tourney_id FROM standings WHERE standings.id=%L', id);
--         END LOOP ;
--     END
--
-- $$ LANGUAGE plpgsql;

-- get total amount of opponent wins --
SELECT SUM(opponent_wins) from opponent_wins(1, 1);
SELECT * FROM test_opponent_wins(1, 1);

