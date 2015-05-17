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


class Sport(database.Entity):
    name = PrimaryKey(str)
    players_per_team = Required(int)
    games = Set("Game")


class Team(database.Entity):
    name = PrimaryKey(str)
    users = Set(Player)
    games = Set("Game")


class Game(database.Entity):
    id = PrimaryKey(int, auto=True)
    location = Required(str)
    date = Required(date)
    final_score = Required(str)
    sport = Required(Sport)
    teams = Set(Team)


def _bind_db(db="../welikesports.sqlite", debug=True):
    if debug:
        sql_debug(True)
    database.bind("sqlite", db, create_db=True)
    database.generate_mapping(create_tables=True)
