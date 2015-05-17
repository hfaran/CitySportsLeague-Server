from datetime import date

from pony.orm import Database, PrimaryKey, Required, Optional, sql_debug, \
    LongStr, Set


database = Database()


class Player(database.Entity):
    username = PrimaryKey(str)
    salt = Required(str)
    first = Required(str)
    last = Required(str)
    password = Required(str)
    birthday = Required(date)
    gender = Optional(str)
    teams = Set("Team")
    city = Required(str)
    country = Required(str)
    bio = Optional(LongStr)

    accepted_games = Set("Game", reverse="accepted_players")


class Sport(database.Entity):
    name = PrimaryKey(str)
    players_per_team = Required(int)
    teams = Set("Team")


class Team(database.Entity):
    name = PrimaryKey(str)
    users = Set(Player)
    games = Set("Game")
    sport = Required(Sport)


class Game(database.Entity):
    id = PrimaryKey(int, auto=True)
    teams = Set(Team)

    location = Optional(str)
    date = Optional(date)
    cancelled = Optional(bool)
    final_score = Optional(str)

    accepted_players = Set(Player, reverse="accepted_games")


def _bind_db(db="../welikesports.sqlite", debug=True):
    if debug:
        sql_debug(True)
    database.bind("sqlite", db, create_db=True)
    database.generate_mapping(create_tables=True)
