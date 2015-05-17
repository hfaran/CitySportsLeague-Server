import bcrypt
from tornado_json.exceptions import api_assert, APIError
from tornado_json import schema
from pony.orm import db_session, select
from tornado.web import authenticated

from wlsports.db import Game as GameEntity
from wlsports.handlers import APIHandler


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
