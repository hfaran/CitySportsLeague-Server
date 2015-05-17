import bcrypt
from tornado_json.exceptions import api_assert, APIError
from tornado_json import schema
from pony.orm import db_session, CommitException
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
            }
        }
    )
    def get(self):
        """
        (Player only) GET to retrieve player info
        """
        with db_session:
            player = PlayerEntity[self.get_current_user()]
            player_dict = player.to_dict(exclude=[
                "salt",
                "password"
            ])
            player_dict['birthday'] = str(player_dict['birthday'])

        return player_dict
