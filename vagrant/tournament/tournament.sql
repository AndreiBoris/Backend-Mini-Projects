-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DELETE FROM match;
DELETE FROM player;
DROP TABLE IF EXISTS match;
DROP TABLE IF EXISTS player;


CREATE TABLE player (
  name TEXT,
  id SERIAL PRIMARY KEY
);

CREATE TABLE match (
  first_player INTEGER REFERENCES player(id),
  second_player INTEGER REFERENCES player(id)
    CONSTRAINT two_players CHECK (second_player != first_player),
  winner INTEGER REFERENCES player(id)
    CONSTRAINT winner_is_player CHECK (winner = first_player
                                        OR winner = second_player),
  id SERIAL PRIMARY KEY
);
