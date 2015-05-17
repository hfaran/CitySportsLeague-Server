import bcrypt
from tornado_json.exceptions import api_assert, APIError
from tornado_json import schema
from pony.orm import db_session, CommitException, select
from tornado.web import authenticated

from wlsports.db import Player as PlayerEntity
from wlsports.handlers import APIHandler


class Player(APIHandler):

    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "first": {"type": "string"},
                "last": {"type": "string"},
                "password": {"type": "string"},
                "gender": {"enum": ["M", "F"]},
                "birthday": {"type": "string"},
                "city": {"type": "string"},
                "country": {"type": "string"},
                "bio": {"type": "string"},
            },
            "required": [
                "username",
                "first",
                "last",
                "password",
                "birthday",
                "city",
                "country"
            ],
        },
        output_schema={
            "type": "object",
            "properties": {
                "username": {"type": "string"}
            }
        }
    )
    def put(self):
        """
        PUT the required parameters to permanently register a new player

        * `username`
        * `first`: First name
        * `last`: Last name
        * `password`: Password for future logins
        * `gender`: M/F
        * `birthday`: e.g., "1993-05-16"
        * `city`
        * `country`
        * `bio`
        """
        attrs = dict(self.body)

        # Set salt and password
        salt = bcrypt.gensalt(rounds=12)
        attrs['password'] = bcrypt.hashpw(
            password=attrs['password'].encode(),
            salt=salt
        ).decode()
        attrs['salt'] = salt.decode()

        # Create player
        with db_session:
            api_assert(
                attrs['username'],
                400,
                log_message="Provided username is empty!"
            )
            if PlayerEntity.get(username=attrs['username']):
                raise APIError(
                    409,
                    log_message="Player with username {} already exists!"
                    .format(attrs['username'])
                )
            player = PlayerEntity(**attrs)

        # Log the user in
        self.set_secure_cookie(
            "user",
            attrs['username'],
            self.settings['app_config'].session_timeout_days
        )

        return {"username": player.username}


class Me(APIHandler):

    @authenticated
    @schema.validate(
        output_schema={
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "first": {"type": "string"},
                "last": {"type": "string"},
                "gender": {"type": "string"},
                "birthday": {"type": "string"},
                "city": {"type": "string"},
                "country": {"type": "string"},
                "bio": {"type": "string"},
                "teams": {"type": "array"},
                "accepted_games":{"type": "array"}
            }
        }
    )
    def get(self):
        """
        (Player only) GET to retrieve player info

        * `games`: Array of game IDs that player has accepted
        * `teams`: Array of team names
        """
        with db_session:
            player = PlayerEntity[self.get_current_user()]
            player_dict = player.to_dict(
                exclude=["salt", "password"],
                with_collections=True
            )
            player_dict['birthday'] = str(player_dict['birthday'])

        return player_dict


class Search(APIHandler):

    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        },
        output_schema={
            "type": "array"
        }
    )
    def post(self):
        """
        Search for players whose name starts with query
        """
        with db_session:
            usernames = select(
                p.username for p in PlayerEntity
                if p.username.startswith(self.body['query'])
            )[:]

        return usernames


class Invitations(APIHandler):

    @authenticated
    @schema.validate(
        output_schema={
            "type": "array"
        }
    )
    def get(self):
        """
        GET array of IDs for open game invitations for self
        """
        username = self.get_current_user()

        with db_session:
            player = PlayerEntity[username]
            teams = player.teams
            team_games = [game for team in teams for game in team.games]
            # Get games that the team is added for that have not been
            # cancelled
            team_game_ids = {game.id for game in team_games
                             if game.cancelled is not True}
            player_accepted_ids = {game.id for game in player.accepted_games}

            return list(team_game_ids - player_accepted_ids)
