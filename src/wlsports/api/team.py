from tornado_json.exceptions import api_assert, APIError
from tornado_json import schema
from pony.orm import db_session, CommitException, select
from tornado.web import authenticated

from wlsports.db import Team as TeamEntity
from wlsports.db import Player as PlayerEntity
from wlsports.handlers import APIHandler


class Team(APIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "usernames": {"type": "array"},
                "name": {"type": "string"},
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
    )
    def put(self):
        """
        PUT to create a team

        * `name`
        * `usernames`: list of teammates to add (except yourself)
        """
        attrs = dict(self.body)

        with db_session:
            if TeamEntity.get(name=attrs['name']):
                raise APIError(
                    409,
                    log_message="Team with name {} already exists!"
                    .format(attrs['name'])
                )

            # Add team mates
            players = []
            for pname in attrs["usernames"]:
                # Skip self (only add teammates)
                if pname == self.get_current_user():
                    continue

                player = PlayerEntity.get(username=pname)
                api_assert(
                    player is not None,
                    400,
                    log_message="No player exists with name {}!".format(pname)
                )
                players.append(player)
            # Add self
            player = PlayerEntity[self.get_current_user()]
            players.append(player)

            # Create team
            team = TeamEntity(
                name=attrs['name'],
                users=players
            )

            return {'name': team.name}

    @schema.validate(
        output_schema={
            "type": "object",
            "properties": {
                "usernames": {"type": "array"},
                "name": {"type": "string"},
            }
        },
    )
    def get(self, name):
        """
        Get team with `name`
        """
        with db_session:
            team = TeamEntity.get(name=name)
            if team is None:
                raise APIError(
                    400,
                    log_message="Team with name {} does not exist!"
                    .format(name)
                )

            usernames = [p.username for p in team.users]
            name = team.name

            return {
                "usernames": usernames,
                "name": name
            }
