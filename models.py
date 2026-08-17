from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    team = db.relationship('Team', backref='players') #busca o nome do time em class Team
    captain = db.Column(db.Boolean, default=False)
    matches_played = db.Column(db.Integer, nullable=False, default=0)
    championship_titles = db.Column(db.Integer, nullable=False, default=0)
    photo_url = db.Column(db.String, nullable=True)

    __table_args__ = (
        db.CheckConstraint('matches_played >= 0', name='check_matches_played_non_negative'),
        db.CheckConstraint('championship_titles >= 0', name='check_championship_titles_non_negative'),
    )

class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    championship_titles = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (
        db.CheckConstraint('graduation_year >= 2019', name='check_graduation_year_valid'),
        db.CheckConstraint('championship_titles >= 0', name='check_championship_titles_non_negative')
    )

class Championship(db.Model):
    __tablename__ = "championships"
    championship_year = db.Column(db.Integer, primary_key=True)

class Standing(db.Model):
    __tablename__ = "standings"
    championship_year = db.Column(db.Integer, db.ForeignKey('championships.championship_year'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)

class Round(db.Model):
    __tablename__ = "rounds"
    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, nullable=False)
    championship_year = db.Column(db.Integer, db.ForeignKey('championships.championship_year'), nullable=False)
    player_of_the_round_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)
    stage = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('championship_year', 'round_number', "stage", name='unique_round_per_championship_stage'),
        db.CheckConstraint('round_number >= 1', name='check_round_number_positive'),
        db.CheckConstraint("stage IN ('Round-Robin', 'Group Stage', 'Semi-Finals', '3rd Place Match', 'Final')", name='check_stage_valid')
    )

class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    home_team_goals = db.Column(db.Integer, nullable=False, default=0)
    away_team_goals = db.Column(db.Integer, nullable=False, default=0)
    match_date = db.Column(db.DateTime(timezone=True), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    player_of_the_match_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)

    __table_args__ = (
        db.CheckConstraint('home_team_goals >= 0', name='check_home_team_goals_non_negative'),
        db.CheckConstraint('away_team_goals >= 0', name='check_away_team_goals_non_negative'),
        db.CheckConstraint('home_team_id <> away_team_id', name='check_teams_different'),
        db.UniqueConstraint('round_id', 'home_team_id', 'away_team_id', name='unique_match_per_round')
    )

class MatchAppearance(db.Model):
    __tablename__ = "matches_played"
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('match_id', 'player_id', name='unique_player_per_match'),
)

class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    own_goal = db.Column(db.Boolean, nullable=False, default=False)

class Assist(db.Model):
    __tablename__ = "assists"
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)

class YellowCard(db.Model):
    __tablename__ = "yellow_cards"
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)

class RedCard(db.Model):
    __tablename__ = "red_cards"
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)

class TeamOfTheRound(db.Model):
    __tablename__ = "team_of_the_round"
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('round_id', 'player_id', name='unique_player_per_round'),
    )

class ChampionshipTitle(db.Model):
    __tablename__ = "championship_titles"
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), primary_key=True)
    championship_year = db.Column(db.Integer, db.ForeignKey('championships.championship_year'), primary_key=True)