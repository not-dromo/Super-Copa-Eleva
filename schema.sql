CREATE TABLE "players" (
  "id" SERIAL PRIMARY KEY,
  "name" TEXT NOT NULL,
  "nickname" TEXT,
  "team_id" INTEGER,
  "captain" BOOLEAN NOT NULL DEFAULT false,
  "matches_played" INTEGER NOT NULL DEFAULT 0 CHECK (matches_played >= 0),
  --"goals" INTEGER NOT NULL DEFAULT 0 CHECK (goals >= 0),
  --"assists" INTEGER NOT NULL DEFAULT 0 CHECK (assists >= 0),
  --"yellow_cards" INTEGER NOT NULL DEFAULT 0 CHECK (yellow_cards >= 0),
  --"red_cards" INTEGER NOT NULL DEFAULT 0 CHECK (red_cards >= 0),
  --"player_of_the_match_awards" INTEGER NOT NULL DEFAULT 0 CHECK (player_of_the_match_awards >= 0),
  --"player_of_the_round_awards" INTEGER NOT NULL DEFAULT 0 CHECK (player_of_the_round_awards >= 0),
  --"team_of_the_round_awards" INTEGER NOT NULL DEFAULT 0 CHECK (team_of_the_round_awards >= 0),
  "championship_titles" INTEGER NOT NULL DEFAULT 0 CHECK (championship_titles >= 0)
);

CREATE TABLE "teams" (
  "id" SERIAL PRIMARY KEY,
  "name" TEXT NOT NULL,
  "graduation_year" INTEGER NOT NULL CHECK (graduation_year >= 2019),
  --"championship_titles" INTEGER NOT NULL DEFAULT 0 CHECK (championship_titles >= 0),
  "active" BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE "championships" (
  "championship_year" INTEGER PRIMARY KEY
);

CREATE TABLE "standings" (
  "championship_year" INTEGER NOT NULL,
  "team_id" INTEGER NOT NULL,
  --"matches_played" INTEGER NOT NULL DEFAULT 0 CHECK (matches_played >= 0),
  --"wins" INTEGER NOT NULL DEFAULT 0 CHECK (wins >= 0),
  --"draws" INTEGER NOT NULL DEFAULT 0 CHECK (draws >= 0),
  --"losses" INTEGER NOT NULL DEFAULT 0 CHECK (losses >= 0),
  --"goals_for" INTEGER NOT NULL DEFAULT 0 CHECK (goals_for >= 0),
  --"goals_against" INTEGER NOT NULL DEFAULT 0 CHECK (goals_against >= 0),
  --"goal_difference" INTEGER GENERATED ALWAYS AS (goals_for - goals_against) STORED,
  --"yellow_cards" INTEGER NOT NULL DEFAULT 0 CHECK (yellow_cards >= 0),
  --"red_cards" INTEGER NOT NULL DEFAULT 0 CHECK (red_cards >= 0),
  --"points" INTEGER GENERATED ALWAYS AS (wins * 3 + draws) STORED,
  --"team_group" TEXT NOT NULL CHECK (team_group IN ('A', 'B')),
  PRIMARY KEY ("championship_year", "team_id")
);

CREATE TABLE "rounds" (
  "id" SERIAL PRIMARY KEY,
  "round_number" INTEGER NOT NULL CHECK (round_number > 0),
  "championship_year" INTEGER NOT NULL,
  "player_of_the_round_id" INTEGER,
  "stage" TEXT NOT NULL CHECK (stage IN ('Round-Robin', 'Group Stage', 'Semi-Finals', '3rd Place Match', 'Final')),
  UNIQUE ("round_number", "championship_year", "stage")
);

CREATE TABLE "matches" (
  "id" SERIAL PRIMARY KEY,
  "round_id" INTEGER NOT NULL,
  "home_team_id" INTEGER NOT NULL,
  "away_team_id" INTEGER NOT NULL,
  "home_team_goals" INTEGER NOT NULL DEFAULT 0 CHECK (home_team_goals >= 0),
  "away_team_goals" INTEGER NOT NULL DEFAULT 0 CHECK (away_team_goals >= 0),
  "match_date" TIMESTAMPTZ,
  "location" TEXT,
  "player_of_the_match_id" INTEGER,

  CHECK (home_team_id <> away_team_id),
  UNIQUE ("round_id", "home_team_id", "away_team_id")
);

CREATE TABLE "goals" (
  "id" SERIAL PRIMARY KEY,
  "player_id" INTEGER NOT NULL,
  "match_id" INTEGER NOT NULL,
  "own_goal" BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE "assists" (
  "id" SERIAL PRIMARY KEY,
  "player_id" INTEGER NOT NULL,
  "match_id" INTEGER NOT NULL
);

CREATE TABLE "yellow_cards" (
  "id" SERIAL PRIMARY KEY,
  "player_id" INTEGER NOT NULL,
  "match_id" INTEGER NOT NULL
);

CREATE TABLE "red_cards" (
  "id" SERIAL PRIMARY KEY,
  "player_id" INTEGER NOT NULL,
  "match_id" INTEGER NOT NULL
);

CREATE TABLE "team_of_the_round" (
  "id" SERIAL PRIMARY KEY,
  "player_id" INTEGER NOT NULL,
  "round_id" INTEGER NOT NULL,
  UNIQUE ("player_id", "round_id")
);

CREATE TABLE "championship_titles" (
  "player_id" INTEGER NOT NULL,
  "championship_year" INTEGER NOT NULL,
  PRIMARY KEY ("player_id", "championship_year")
);

ALTER TABLE "standings" ADD FOREIGN KEY ("championship_year") REFERENCES "championships" ("championship_year") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "standings" ADD FOREIGN KEY ("team_id") REFERENCES "teams" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "players" ADD FOREIGN KEY ("team_id") REFERENCES "teams" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "rounds" ADD FOREIGN KEY ("championship_year") REFERENCES "championships" ("championship_year") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "rounds" ADD FOREIGN KEY ("player_of_the_round_id") REFERENCES "players" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "matches" ADD FOREIGN KEY ("round_id") REFERENCES "rounds" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "matches" ADD FOREIGN KEY ("player_of_the_match_id") REFERENCES "players" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "matches" ADD FOREIGN KEY ("home_team_id") REFERENCES "teams" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "matches" ADD FOREIGN KEY ("away_team_id") REFERENCES "teams" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "goals" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "assists" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "yellow_cards" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "red_cards" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "team_of_the_round" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "championship_titles" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "goals" ADD FOREIGN KEY ("match_id") REFERENCES "matches" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "assists" ADD FOREIGN KEY ("match_id") REFERENCES "matches" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "yellow_cards" ADD FOREIGN KEY ("match_id") REFERENCES "matches" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "red_cards" ADD FOREIGN KEY ("match_id") REFERENCES "matches" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "team_of_the_round" ADD FOREIGN KEY ("round_id") REFERENCES "rounds" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "championship_titles" ADD FOREIGN KEY ("championship_year") REFERENCES "championships" ("championship_year") DEFERRABLE INITIALLY IMMEDIATE;