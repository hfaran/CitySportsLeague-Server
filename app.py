#!/usr/bin/env python2.7


from datetime import date
from pony.orm import Database, PrimaryKey, Required, Optional, sql_debug, \
    LongStr, Set


db = Database("sqlite", "welikesports.sqlite", create_db=True)


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    first = Required(str)
    last = Required(str)
    birthday = Required(date)
    gender = Optional(str)
    teams = Set("Team")
    city = Required(str)
    country = Required(str)
    bio = Optional(LongStr)


class Sport(db.Entity):
    name = PrimaryKey(str)
    players_per_team = Required(int)
    games = Set("Game")


class Team(db.Entity):
    name = PrimaryKey(str)
    users = Set(User)
    games = Set("Game")


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    location = Required(str)
    date = Required(date)
    final_score = Required(str)
    sport = Required(Sport)
    teams = Set(Team)


sql_debug(True)
db.generate_mapping(create_tables=True)
