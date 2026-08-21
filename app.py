from flask import Flask, render_template, request, redirect, abort
from models import db, Player, Team, Championship, Standing, Round, Match, MatchAppearance, Goal, Assist, YellowCard, RedCard, TeamOfTheRound, ChampionshipTitle
from sqlalchemy import func
from sqlalchemy.orm import aliased
import models
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from zoneinfo import ZoneInfo
from collections import defaultdict
# for tests
import time

BRASILIA_TZ = ZoneInfo("America/Sao_Paulo")

# TODO: QUANDO TERMINAR DE CODAR TUUDO TEM QUE IR ATÉ O FINAL DESSA PAGINA E TROCAR O DEBUG PRA FALSE!!!!!

load_dotenv()

# TODO: add error message if SQLALCHEMY_DATABASE_URL is not set in the environment variables
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configuration of Cloudinary       
cloudinary.config( 
    cloud_name = "ccpmanza", 
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

db.init_app(app)

# SQL queries:

# SQL queries to get all players data
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

# SQL queries to get a single player data
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


# SQL queries to get all teams data
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

# SQL queries to get all players from a single team
def get_players_from_a_team(choosen_team):
    all_players = db.session.query(Player).filter(Player.team_id == choosen_team).order_by(Player.name).all()
    number_of_players = len(all_players)

    return (all_players, number_of_players)


# Creates a list of tuples with 3 objects: match, home_team and away_team. The list is ordered by the date of the match
def get_matches_data():

    # As of now (2026) Super Copa Eleva does not have the distinction 
    # of Home and Away teams in the official rules, this is purely done in 
    # the code so that we don't need to use team1 and team2 as nicknames.
    # Home_team and Away_team have the same structure so it's important 
    # to name them so that teams can be differentiated in a match

    Home_team = aliased(Team) # creates a alias of the table Team
    Away_team = aliased(Team)

    results = db.session.query(Match, Home_team, Away_team)\
        .join(Home_team, Match.home_team_id == Home_team.id)\
        .join(Away_team, Match.away_team_id == Away_team.id)\
        .order_by(Match.match_date.desc())\
        .all()

    return results

# Dictionary to map team IDs to badge image filenames - maybe change it to a database column in the future, but as of 2026 it works (small amount of teams)
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

# Default player photo in case the player doesn't have a photo uploaded to Cloudinary
DEFAULT_PLAYER_PHOTO_WHITE = "https://res.cloudinary.com/ccpmanza/image/upload/no_player_photo_white_uy3xrm.png"

# Dictonary to convert month numbers to month names in Portuguese
MONTH_NAMES_PT = {
    1: "Janeiro",    2: "Fevereiro",  3: "Março",
    4: "Abril",      5: "Maio",       6: "Junho",
    7: "Julho",      8: "Agosto",     9: "Setembro",
    10: "Outubro",  11: "Novembro",  12: "Dezembro"
}

# function that formats a date to the format "day de month" in Portuguese --> (DD de MM)
def format_date_pt(date):
    if date is None:
        return ""
    # return f"{date.day} de {MONTH_NAMES_PT[date.month]} de {date.year}"
    return f"{date.day} de {MONTH_NAMES_PT[date.month]}"
app.jinja_env.filters['format_date_pt'] = format_date_pt










# ROUTES↓
@app.route('/')
def index():
    # empty for now
    return render_template('index.html')

@app.route('/main_menu')
def main_menu():
    # empty
    # TODO: add a main menu page with
    # - next matches
    # - last matches
    # - player of the round (winner of pora)
    # - team of the round (winners of totr)
    # - best players on each stat
    # # # that's it for now # # # 

    return render_template('main_menu.html')


# Players page route - shows all players and their current stats
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

    for p in players_data:
        print("id: " + str(p["id"]) + " - name: " + str(p["name"]) + "\n")
    
    return render_template('players.html', players=players_data)


# Player stats page route - shows a single player's stats and trophies
# TODO: add a history section of last (and all) matches played by this player 
# --> TODO: add a table in the BD of which player played in which match
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

# Teams page route - shows all teams so you can click on a team and see their page
@app.route('/teams')
def teams():
    # empty
    return render_template('teams.html')

# Team page route - shows all players from that team
# TODO: add a history section of last (and all) matches played by this team (just like the player stats page, but for teams)
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

# Standings page route - shows the current standings of the championship
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

# Matches page route - shows all matches played in the championship and the next one to come
# TODO: add a button for admins so that they can create the next matches and edit their results, who played, goals, assists, cards, etc...
# TODO: add to the pop up page the possibility to add links to the youtube videos of the goals and the instagram post related to that match
@app.route('/matches')
def matches():
    # for loading page time testing purpose this variable is initialized
    start = time.time()





    all_matches = get_matches_data()
    match_ids = [match.id for match, _, _, in all_matches]

    # Data Base query is done out of the loop for faster page loading!# 

    # creates a list of tuples with 2 objects Player and MatchAppearance such that Player.id == MatchAppearance.player_id is true
    all_appearances = db.session.query(MatchAppearance, Player)\
        .join(Player, MatchAppearance.player_id == Player.id)\
        .filter(MatchAppearance.match_id.in_(match_ids))\
        .all()

    # creates a list of tuples with 2 objects Player and Goal such that Player.id == Goal.player_id is true
    all_goals = db.session.query(Goal, Player)\
        .join(Player, Goal.player_id == Player.id)\
        .filter(Goal.match_id.in_(match_ids))\
        .all()

    # creates a list of tuples with 2 objects Player and Assist such that Player.id == Assist.player_id is true
    all_assists = db.session.query(Assist, Player)\
        .join(Player, Assist.player_id == Player.id)\
        .filter(Assist.match_id.in_(match_ids))\
        .all()

    # creates a list of tuples with 2 objects Player and YellowCard such that Player.id == YellowCard.player_id is true
    all_yellow_cards = db.session.query(YellowCard, Player)\
        .join(Player, YellowCard.player_id == Player.id)\
        .filter(YellowCard.match_id.in_(match_ids))\
        .all()
    
    # creates a list of tuples with 2 objects Player and RedCard such that Player.id == RedCard.player_id is true
    all_red_cards = db.session.query(RedCard, Player)\
        .join(Player, RedCard.player_id == Player.id)\
        .filter(RedCard.match_id.in_(match_ids))\
        .all()

    # grabs all the matches_ids that exist in the list of matches (the duplicates are already removed from this list)
    round_ids = list(set(match.round_id for match, _, _ in all_matches))

    # creates a list of tuples with 2 objects Player and Round such that Player.id == Round.player_of_the_round_id is true
    all_pora = db.session.query(Round, Player)\
        .join(Player, Round.player_of_the_round_id == Player.id)\
        .filter(Round.round_number.in_(round_ids))\
        .all()

    # creates a list of objects where it includes all TeamOfTheRound which the round_id is found on the list round_ids
    all_round_selections = db.session.query(TeamOfTheRound)\
        .filter(TeamOfTheRound.round_id.in_(round_ids))\
        .all()





    # converting list of tuples/objects into dictionaries

    # creates a dictionary where match_id is the key and a list of players that played in the match is the value 
    appearances_by_match = defaultdict(list)
    for appearance, player in all_appearances:
        appearances_by_match[appearance.match_id].append(player)

    # creates a dictionary where match_id is the key and a list of tuples: (goal, player) is the value 
    goals_by_match = defaultdict(list)
    for goal, player in all_goals:
        goals_by_match[goal.match_id].append((goal, player))

    # creates a dictionary where match_id is the key and a list of tuples: (assist, player) is the value 
    assists_by_match = defaultdict(list)
    for assist, player in all_assists:
        assists_by_match[assist.match_id].append((assist, player))

    # creates a dictionary where match_id is the key and the value is a list of tuples: (player, yellow) or (player, red)
    cards_by_match = defaultdict(list)
    for card, player in all_yellow_cards:
        cards_by_match[card.match_id].append((player, "yellow"))
    for card, player in all_red_cards:
        cards_by_match[card.match_id].append((player, "red"))

    # creates a dictionary where match_id is the key and a list of tuples: (pora, player) is the value 
    pora_by_round = defaultdict(list)
    for pora, player in all_pora:
        pora_by_round[pora.round_number] = player

    # creates a dictionary where round_id is the key and the value is a set with all players chosen as team of the round
    round_selected_by_round = defaultdict(set)
    for row in all_round_selections:
        round_selected_by_round[row.round_id].add(row.player_id)

    print("\n")
    print(pora_by_round) #ta certo]
    print("\n")




    # creates a dictionary that will hold the matches grouped by date. 
    # The key is the date and the value is a list of matches played on that date.
    matches_by_date = {}
    # creates a dictionary that contains all the matches details so that the HTML page 
    # can display all of it in the pop up page when you click on a match. 
    # The key is match_id and the value is a dictionary with all the match details.
    match_details = {}

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
            "date": match.match_date,
            "round_id": match.round_id,
        }

        matches_by_date.setdefault(match_day, []).append(match_data)

        # Details for the pop up page
        if match.match_date:
            local_dt = match.match_date.astimezone(BRASILIA_TZ)
            match_time_str = local_dt.strftime("%H:%M")
        else:
            match_time_str = "Horário não definido"

        # Player of the match: winner of poma (player of the match award)
        player_of_the_match_data = None
        if match.player_of_the_match_id:
            player_of_the_match = Player.query.get(match.player_of_the_match_id)
            pora_winner = pora_by_round.get(match.round_id)
            players_of_the_round = round_selected_by_round[match.round_id]

            player_of_the_match_data = {
                "name": player_of_the_match.name,
                "nickname": player_of_the_match.nickname if player_of_the_match.nickname else "",
                "is_captain": player_of_the_match.captain,
                "photo": player_of_the_match.photo_url if player_of_the_match.photo_url else DEFAULT_PLAYER_PHOTO_WHITE,
                "pora": pora_winner is not None and pora_winner.id in player_of_the_match.id,
            }

        # Players selected for team of the round (if any)
        round_selected_ids = round_selected_by_round[match.round_id]

        home_players = []
        away_players = []
        for player in appearances_by_match[match.id]:
            player_data = {
                "name": player.name,
                "nickname": player.nickname if player.nickname else "",
                "is_captain": player.captain,
                "photo": player.photo_url if player.photo_url else DEFAULT_PLAYER_PHOTO_WHITE,
                "round_selected": player.id in round_selected_ids,
            }
            if player.team_id == match.home_team_id:
                home_players.append(player_data)
            elif player.team_id == match.away_team_id:
                away_players.append(player_data)

        print()
        print(round_selected_ids)

        # Goals
        goals_data = [
            {
                "player_name": p.name,
                "team_name": p.team.name,
                "own_goal": g.own_goal,
                "photo": p.photo_url if p.photo_url else DEFAULT_PLAYER_PHOTO_WHITE,
            }
            for g, p in goals_by_match[match.id]
        ]

        # Assists
        assists_data = [
            {
                "player_name": p.name,
                "team_name": p.team.name,
                "photo": p.photo_url if p.photo_url else DEFAULT_PLAYER_PHOTO_WHITE,
            }
            for _, p in assists_by_match[match.id]
        ]

        # Cards
        cards_data = [
            {
                "player_name": p.name,
                "team_name": p.team.name,
                "card_type": t,
                "photo": p.photo_url if p.photo_url else DEFAULT_PLAYER_PHOTO_WHITE,
            }
            for p, t in cards_by_match[match.id]
        ]

        # JSON file with all details of each match
        match_details[match.id] = {
            "home_team_name": home_team.name,
            "away_team_name": away_team.name,
            "home_team_badge": TEAM_BADGES.get(home_team.id, 'No_Badge.png'),
            "away_team_badge": TEAM_BADGES.get(away_team.id, 'No_Badge.png'),
            "home_team_goals": match.home_team_goals,
            "away_team_goals": match.away_team_goals,
            "date": format_date_pt(match.match_date) if match.match_date else "Data não definida",
            "time": match_time_str,
            "location": match.location if match.location else "Local não definido",
            "player_of_the_match": player_of_the_match_data,
            "home_players": home_players,
            "away_players": away_players,
            "goals": goals_data,
            "assists": assists_data,
            "cards": cards_data,
        }

    # load time check start
    end = time.time()
    print(f"Tempo de execução: {end - start:.3f} segundos")
    # load time check end

    return render_template('matches.html', matches_by_date=matches_by_date, match_details = match_details)








# TESTS
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

# TODO: quando terminar de codar tudo trocar de true para debug=False
# --> translation: when you finish coding everything change from true to debug=False
if __name__ == '__main__':
    # from livereload import Server
    # server = Server(app.wsgi_app)
    # server.watch('templates/*.html')
    # server.watch('static/*.css')
    # server.watch('static/*.js')
    # server.serve(port=5000, debug=True)
    app.run(debug=True, port=5000)