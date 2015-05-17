from __future__ import division

import json

import bcrypt
from tornado_json.exceptions import api_assert, APIError
from tornado_json import schema
from pony.orm import db_session, select, commit
from tornado.web import authenticated

from wlsports.db import Game as GameEntity
from wlsports.db import Player as PlayerEntity
from wlsports.db import Player as TeamEntity
from wlsports.handlers import APIHandler
from wlsports.util import validate_date_text
from wlsports.api.player import get_player_invitations


class Game(APIHandler):

    # TODO authenticated and only players in one of the game teams can view this
    @schema.validate(
        output_schema={
            "type": "object",
            "properties": {
                "id": {"type": "number"},
                "teams": {"type": "array"},
                "host": {"type": "string"},
                "location": {"type": "string"},
                "date": {"type": "string"},
                "accepted_players": {"type": "array"},
                "cancelled": {"type": "boolean"},
                "final_score": {"type": "string"},
            }
        }
    )
    def get(self, game_id):
        """GET game with game_id"""
        with db_session:
            game = GameEntity.get(id=game_id)
            api_assert(
                game is not None,
                400,
                log_message="No such game {} exists!".format(game_id)
            )
            game_dict = game.to_dict(with_collections=True)
        if not game_dict["location"]:
            game_dict["location"] = ""
        if not game_dict["date"]:
            game_dict["date"] = ""
        if not game_dict["cancelled"]:
            game_dict["cancelled"] = False
        if not game_dict["final_score"]:
            game_dict["final_score"] = ""

        return game_dict


class DateAndLoc(APIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "location": {"type": "string"},
                "id": {"type": "number"}
            },
            "required": [
                "date",
                "location",
                "id"
            ]
        },
        output_schema={
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "location": {"type": "string"},
                "id": {"type": "number"}
            }
        }
    )
    def post(self):
        """(Game host only) Update date and location of game

        * `date`: Must be in YYYY-MM-DD format
        * `location`
        * `id`: ID of game to change
        """
        attrs = dict(self.body)

        with db_session:
            game = GameEntity.get(id=attrs['id'])
            api_assert(
                game is not None,
                400,
                log_message="No such game {} exists!".format(attrs['id'])
            )

            api_assert(
                game.host.username == self.get_current_user(),
                403,
                log_message="Only the host of this game may edit it!"
            )

            try:
                validate_date_text(attrs['date'])
            except ValueError as err:
                raise APIError(
                    400,
                    log_message=str(err)
                )

            game.location = attrs['location']
            game.date = attrs['date']
            commit()

            game_dict = {k: v for k, v in game.to_dict().items() if k in [
                "id",
                "date",
                "location"
            ]}
            game_dict["date"] = str(game_dict["date"])

            return game_dict


class InviteRespond(APIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "id": {"type": "number"},
                "decision": {"enum": ["Accept", "Decline"]},
            }
        },
        output_schema={
            "type": "string"
        }
    )
    def post(self):
        """Decline or accept invite

        * `id`: ID of game you want to respond to invite for
        * `decision`: Either "Accept" or "Decline"
        """
        attrs = dict(self.body)

        with db_session:
            game = GameEntity.get(id=attrs['id'])
            me = PlayerEntity[self.get_current_user()]
            api_assert(
                game is not None,
                400,
                log_message="No such game {} exists!".format(attrs['id'])
            )
            player_invites = get_player_invitations(me.username)
            api_assert(
                attrs['id'] in player_invites,
                400,
                log_message="This game is not in your list of invitations!"
            )

            if attrs['decision'] == "Accept":
                game.accepted_players.add(me)
                return "You successfully joined game {}!".format(attrs['id'])
            elif attrs['decision'] == "Decline":
                game.cancelled = True
                return "You declined and the game ({}) has been cancelled!".format(
                    attrs['id']
                )


class Finish(APIHandler):

    def post(self):
        attrs = dict(self.body)

        with db_session:
            game = GameEntity.get(id=attrs['id'])
            api_assert(
                game is not None,
                400,
                log_message="No such game {} exists!".format(attrs['id'])
            )

            api_assert(
                game.host.username == self.get_current_user(),
                403,
                log_message="Only the host of this game may edit it!"
            )

            api_assert(
                game.cancelled is not True,
                400,
                "This game has been cancelled. :("
            )

            api_assert(
                len(game.accepted_players) ==
                len([p for t in game.teams for p in t.users]),
                400,
                "Not everyone has accepted invites for this game yet!"
            )

            team_names = [team.name for team in game.teams]
            team_a = TeamEntity[team_names[0]]
            team_b = TeamEntity[team_names[1]]

            # Make sure final_score has legit team names
            final_score = attrs['final_score']
            for team_name, score in final_score.iteritems():
                api_assert(
                    team_name in team_names,
                    400,
                    "{} is not part of this game!".format(team_name)
                )

            # Set wins, losses and ties
            if final_score[team_a.name] > final_score[team_b.name]:
                team_a.wins += 1
                team_b.losses += 1
            elif final_score[team_a.name] < final_score[team_b.name]:
                team_b.wins += 1
                team_a.losses += 1
            else:
                team_a.ties += 1
                team_b.ties += 1

            # Calculate new points_ratio
            for team1, team2 in [(team_a, team_b), (team_b, team_a)]:
                total_games = team1.wins + team1.losses + team1.ties
                team1.points_ratio = (
                    (
                        team1.points_ratio * max(total_games, 0)
                    ) + (
                        final_score[team1.name] / final_score[team2.name]
                    )
                ) / total_games

            # Set final score
            game.final_score = json.dumps(final_score)
