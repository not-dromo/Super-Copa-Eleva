from flask import Flask, render_template, request, redirect, abort
from models import db, Player, Team, Championship, Standing, Round, Match, Goal, Assist, YellowCard, RedCard, TeamOfTheRound, ChampionshipTitle
from sqlalchemy import func
from sqlalchemy.orm import aliased
import models
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

#TODO: QUANDO TERMINAR DE CODAR TUUDO TEM QUE IR ATÉ O FINAL DESSA PAGINA E TROCAR O DEBUG PRA FALSE!!!!!

load_dotenv()

#TODO: add error message iff SQLALCHEMY_DATABASE_URL is not set in the environment variables
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configuration       
cloudinary.config( 
    cloud_name = "ccpmanza", 
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

db.init_app(app)

#consultas de SQL
def get_players_data():
    all_players_goals = db.session.query(Goal.player_id, func.count(Goal.id).label('goal_count')).filter(Goal.own_goal == False).group_by(Goal.player_id).subquery()
    all_players_assists = db.session.query(Assist.player_id, func.count(Assist.id).label('assist_count')).group_by(Assist.player_id).subquery()
    all_players_yellow_cards = db.session.query(YellowCard.player_id, func.count(YellowCard.id).label('yellow_card_count')).group_by(YellowCard.player_id).subquery()
    all_players_red_cards = db.session.query(RedCard.player_id, func.count(RedCard.id).label('red_card_count')).group_by(RedCard.player_id).subquery()
    # totr = team of the round
    all_players_poma = db.session.query(Match.player_of_the_match_id, func.count(Match.id).label('player_of_the_match_count')).group_by(Match.player_of_the_match_id).subquery()
    # poma = player of the match awards
    all_players_pora = db.session.query(Round.player_of_the_round_id, func.count(Round.id).label('player_of_the_round_count')).group_by(Round.player_of_the_round_id).subquery()
    # pora = player of the round awards
    all_players_totr = db.session.query(TeamOfTheRound.player_id, func.count(TeamOfTheRound.id).label('team_of_the_round_count')).group_by(TeamOfTheRound.player_id).subquery()

    return (all_players_goals, all_players_assists, all_players_yellow_cards, all_players_red_cards, all_players_poma, all_players_pora, all_players_totr)

def get_single_player_data(choosen_player):
    player_goals = db.session.query(func.count(Goal.id)).filter(Goal.player_id == choosen_player and Goal.own_goal == False).scalar()
    player_assists = db.session.query(func.count(Assist.id)).filter(Assist.player_id == choosen_player).scalar()
    player_yellow_cards = db.session.query(func.count(YellowCard.id)).filter(YellowCard.player_id == choosen_player).scalar()
    player_red_cards = db.session.query(func.count(RedCard.id)).filter(RedCard.player_id == choosen_player).scalar()
    # totr = team of the round
    player_poma = db.session.query(func.count(Match.id)).filter(Match.player_of_the_match_id == choosen_player).scalar()
    # poma = player of the match awards
    player_pora = db.session.query(func.count(Round.id)).filter(Round.player_of_the_round_id == choosen_player).scalar()
    # pora = player of the round awards
    player_totr = db.session.query(func.count(TeamOfTheRound.id)).filter(TeamOfTheRound.player_id == choosen_player).scalar()

    return (player_goals, player_assists, player_yellow_cards, player_red_cards, player_poma, player_pora, player_totr)

def get_players_from_a_team(choosen_team):
    all_players = db.session.query(Player).filter(Player.team_id == choosen_team).order_by(Player.name).all()
    number_of_players = len(all_players)

    return (all_players, number_of_players)

def get_teams_data():
    all_games_away = db.session.query(Match.away_team_id, func.count(Match.away_team_id).label('matches_away')).group_by(Match.away_team_id).subquery()
    all_games_home = db.session.query(Match.home_team_id, func.count(Match.home_team_id).label('matches_home')).group_by(Match.home_team_id).subquery()
    all_wins_away = db.session.query(Match.away_team_id, func.count(Match.away_team_id).label('wins_away')).filter(Match.away_team_goals > Match.home_team_goals).group_by(Match.away_team_id).subquery()
    all_wins_home = db.session.query(Match.home_team_id, func.count(Match.home_team_id).label('wins_home')).filter(Match.away_team_goals < Match.home_team_goals).group_by(Match.home_team_id).subquery()
    all_losses_away = db.session.query(Match.away_team_id, func.count(Match.away_team_id).label('losses_away')).filter(Match.away_team_goals < Match.home_team_goals).group_by(Match.away_team_id).subquery()
    all_losses_home = db.session.query(Match.home_team_id, func.count(Match.home_team_id).label('losses_home')).filter(Match.away_team_goals > Match.home_team_goals).group_by(Match.home_team_id).subquery()
    all_team_goals_away = db.session.query(Match.away_team_id, func.sum(Match.away_team_goals).label('goal_away')).group_by(Match.away_team_id).subquery()
    all_team_goals_home = db.session.query(Match.home_team_id, func.sum(Match.home_team_goals).label('goal_home')).group_by(Match.home_team_id).subquery()
    all_team_goals_against_away = db.session.query(Match.away_team_id, func.sum(Match.home_team_goals).label('goal_against_away')).group_by(Match.away_team_id).subquery()
    all_team_goals_against_home = db.session.query(Match.home_team_id, func.sum(Match.away_team_goals).label('goal_against_home')).group_by(Match.home_team_id).subquery()

    return (all_games_away, all_games_home, all_wins_away, all_wins_home, all_losses_away, all_losses_home, all_team_goals_away, all_team_goals_home, all_team_goals_against_away, all_team_goals_against_home)

def get_matches_data():
    Home_team = aliased(Team)
    Away_team = aliased(Team)

    results = db.session.query(Match, Home_team, Away_team)\
        .join(Home_team, Match.home_team_id == Home_team.id)\
        .join(Away_team, Match.away_team_id == Away_team.id)\
        .order_by(Match.match_date.desc())\
        .all()

    return results

TEAM_BADGES = {
    0: 'No_Badge.png',
    1: 'Aposendaros_2019.png',
    2: 'Botei_Tirei_2020.png',
    3: 'David_A_Williams_2021.png',
    4: 'Inter_de_Milanbe_2022.png',
    5: 'Parinha_2023.png',
    6: 'Selemanca_2024.png',
    7: 'UbiraNove_Family_2025.png',
}

DEFAULT_PLAYER_PHOTO_WHITE = "https://res.cloudinary.com/ccpmanza/image/upload/no_player_photo_white_uy3xrm.png"

#routes↓
@app.route('/')
def index():
    #empty
    return render_template('index.html')

@app.route('/main_menu')
def main_menu():
    #empty
    return render_template('main_menu.html')



@app.route('/players')
def players():
    (all_players_goals, all_players_assists, all_players_yellow_cards, all_players_red_cards, all_players_poma, all_players_pora, all_players_totr) = get_players_data()

    results = db.session.query(
        Player,
        func.coalesce(all_players_goals.c.goal_count, 0).label('goal_count'),
        func.coalesce(all_players_assists.c.assist_count, 0).label('assist_count'),
        func.coalesce(all_players_yellow_cards.c.yellow_card_count, 0).label('yellow_card_count'),
        func.coalesce(all_players_red_cards.c.red_card_count, 0).label('red_card_count'),
        func.coalesce(all_players_poma.c.player_of_the_match_count, 0).label('player_of_the_match_count'),
        func.coalesce(all_players_pora.c.player_of_the_round_count, 0).label('player_of_the_round_count'),
        func.coalesce(all_players_totr.c.team_of_the_round_count, 0).label('team_of_the_round_count')
    ).outerjoin(all_players_goals, Player.id == all_players_goals.c.player_id)\
     .outerjoin(all_players_assists, Player.id == all_players_assists.c.player_id)\
     .outerjoin(all_players_yellow_cards, Player.id == all_players_yellow_cards.c.player_id)\
     .outerjoin(all_players_red_cards, Player.id == all_players_red_cards.c.player_id)\
     .outerjoin(all_players_poma, Player.id == all_players_poma.c.player_of_the_match_id)\
     .outerjoin(all_players_pora, Player.id == all_players_pora.c.player_of_the_round_id)\
     .outerjoin(all_players_totr, Player.id == all_players_totr.c.player_id)\
     .all()

    players_data = [
        {
            "id": p.id,
            "name": p.name,
            "nickname": p.nickname,
            "team": p.team,
            "matches_played": p.matches_played,
            "championship_titles": p.championship_titles,
            "goals": goals,
            "assists": assists,
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
            "player_of_the_match": player_of_the_match,
            "player_of_the_round": player_of_the_round,
            "team_of_the_rounds": team_of_the_rounds
        }
        for p, goals, assists, yellow_cards, red_cards, player_of_the_match, player_of_the_round, team_of_the_rounds in results
    ]
    
    return render_template('players.html', players=players_data)



@app.route('/player_stats/<int:player_id>')
def player_stats(player_id):
    player = Player.query.get(player_id)

    if player is None:
        abort(404)

    badge_file = TEAM_BADGES.get(player.team_id, 'No_Badge.png')

    (player_goals, player_assists, player_yellow_cards, player_red_cards, player_poma, player_pora, player_totr) = get_single_player_data(player_id)
    
    return render_template(
        'player_stats.html', 
        player=player, 
        goals=player_goals, 
        assists=player_assists, 
        yellow_cards=player_yellow_cards, 
        red_cards=player_red_cards, 
        poma=player_poma, 
        pora=player_pora, 
        totr=player_totr,
        badge_file=badge_file,
        default_photo = DEFAULT_PLAYER_PHOTO_WHITE
    )

@app.route('/teams')
def teams():
    #empty
    return render_template('teams.html')

@app.route('/team_page/<int:team_id>')
def team_page(team_id):
    team = Team.query.get(team_id)

    if team is None:
        abort(404)

    badge_file = TEAM_BADGES.get(team.id, 'No_Badge.png')

    (players, number_of_players) = get_players_from_a_team(team_id)

    captain = next((p for p in players if p.captain == 1), players[0] if players else None)
    
    return render_template(
        'team_page.html', 
        badge_file=badge_file,
        players=players,
        number_of_players=number_of_players,
        captain=captain,
        default_photo = DEFAULT_PLAYER_PHOTO_WHITE
        )

@app.route('/standings')
def standings():
    (all_matches_away, all_matches_home, all_wins_away, all_wins_home, all_losses_away, all_losses_home, all_goals_away, all_goals_home, all_goals_against_away, all_goals_against_home) = get_teams_data()

    results = db.session.query(
        Team,
        func.coalesce(all_matches_away.c.matches_away, 0).label('matches_away'),
        func.coalesce(all_matches_home.c.matches_home, 0).label('matches_home'),
        func.coalesce(all_wins_away.c.wins_away, 0).label('wins_away'),
        func.coalesce(all_wins_home.c.wins_home, 0).label('wins_home'),
        func.coalesce(all_losses_away.c.losses_away, 0).label('losses_away'),
        func.coalesce(all_losses_home.c.losses_home, 0).label('losses_home'),
        func.coalesce(all_goals_away.c.goal_away, 0).label('goals_away'),
        func.coalesce(all_goals_home.c.goal_home, 0).label('goals_home'),
        func.coalesce(all_goals_against_away.c.goal_against_away, 0).label('goals_against_away'),
        func.coalesce(all_goals_against_home.c.goal_against_home, 0).label('goals_against_home'),
    ).outerjoin(all_matches_away, Team.id == all_matches_away.c.away_team_id)\
     .outerjoin(all_matches_home, Team.id == all_matches_home.c.home_team_id)\
     .outerjoin(all_wins_away, Team.id == all_wins_away.c.away_team_id)\
     .outerjoin(all_wins_home, Team.id == all_wins_home.c.home_team_id)\
     .outerjoin(all_losses_away, Team.id == all_losses_away.c.away_team_id)\
     .outerjoin(all_losses_home, Team.id == all_losses_home.c.home_team_id)\
     .outerjoin(all_goals_away, Team.id == all_goals_away.c.away_team_id)\
     .outerjoin(all_goals_home, Team.id == all_goals_home.c.home_team_id)\
     .outerjoin(all_goals_against_away, Team.id == all_goals_against_away.c.away_team_id)\
     .outerjoin(all_goals_against_home, Team.id == all_goals_against_home.c.home_team_id)\
     .all()

    team_data = [
        {
            "id": team.id,
            "name": team.name,
            "matches": matches_away + matches_home,
            "wins": wins_away + wins_home,
            "losses": losses_away + losses_home,
            "draws": (matches_away + matches_home) - (wins_away + wins_home) - (losses_away + losses_home),
            "goals_for": goals_for_away + goals_for_home,
            "goals_against": goals_against_away + goals_against_home,
            "goal_difference": (goals_for_away + goals_for_home) - (goals_against_away + goals_against_home),
            "points": 3*(wins_away + wins_home) + ((matches_away + matches_home) - (wins_away + wins_home) - (losses_away + losses_home)),
            "badge": TEAM_BADGES.get(team.id, 'No_Badge.png'),
            "foundation_year": team.graduation_year
        }
        for team, matches_away, matches_home, wins_away, wins_home, losses_away, losses_home, goals_for_away, goals_for_home, goals_against_away, goals_against_home in results
    ]

    team_data.sort(key=lambda t: (t["points"], t["wins"], t["goal_difference"], t["goals_for"]), reverse=True)

    print("\n\n\ndebuggando\n")
    for team in team_data:
        print(team)
    print("\n\n\n")
    
    return render_template('standings.html', teams=team_data)

@app.route('/matches')
def matches():
    all_matches = get_matches_data()

    matches_by_date = {}
    for match, home_team, away_team in all_matches:
        match_day = match.match_date.date() if match.match_date else None

        match_data = {
            "id": match.id,
            "home_team_name": home_team.name,
            "away_team_name": away_team.name,
            "home_team_goals": match.home_team_goals,
            "away_team_goals": match.away_team_goals,
            "home_team_badge": TEAM_BADGES.get(home_team.id, 'No_Badge.png'),
            "away_team_badge": TEAM_BADGES.get(away_team.id, 'No_Badge.png'),
        }

        matches_by_date.setdefault(match_day, []).append(match_data)
    
    return render_template('matches.html', matches_by_date=matches_by_date)










#TESTS
@app.route('/test_player_page')
def test_player_page():
    class FakePlayer:
        name = "Jogador Teste"
        nickname = "Apelido Teste"
        captain = True
        matches_played = 99
        championship_titles = 99

    return render_template(
        'player_stats.html',
        player=FakePlayer(),
        goals=99,
        assists=99,
        poma=9,
        pora=99,
        totr=99,
        badge_file='No_Badge.png'
    )






#TODO: quando terminar de codar tudo trocar de true para debug=False
if __name__ == '__main__':
    # from livereload import Server
    # server = Server(app.wsgi_app)
    # server.watch('templates/*.html')
    # server.watch('static/*.css')
    # server.watch('static/*.js')
    # server.serve(port=5000, debug=True)
    app.run(debug=True, port=5000)